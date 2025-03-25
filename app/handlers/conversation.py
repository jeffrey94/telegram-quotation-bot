"""
Conversation handlers for the Telegram Quotation Bot.
"""

import logging
from typing import Dict, Any, List, Optional
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, 
    CommandHandler, 
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from app.bot import is_user_authorized
from app.utils.models import QuotationData, QuotationItem
from app.utils.pdf_generator import PDFGenerator

# Enable logging
logger = logging.getLogger(__name__)

# Define conversation states
(
    CUSTOMER_NAME,
    COLLECTING_ITEMS,
    ITEM_NAME,
    ITEM_QUANTITY,
    ITEM_PRICE,
    NOTES,
    GENERATING_PDF
) = range(7)

# Define keys for ConversationHandler context data
CURRENT_QUOTATION = "current_quotation"
CURRENT_ITEM = "current_item"
ITEMS_LIST = "items_list"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start the conversation to create a new quotation.
    
    Args:
        update: The Telegram update.
        context: The conversation context.
        
    Returns:
        int: The next conversation state.
    """
    user = update.effective_user
    
    # Check if user is authorized
    if not is_user_authorized(user.id):
        await update.message.reply_text(
            "You are not authorized to use this bot. Please contact the administrator."
        )
        return ConversationHandler.END
    
    # Initialize conversation data
    context.user_data[ITEMS_LIST] = []
    
    await update.message.reply_text(
        f"Hello {user.first_name}! Let's create a new quotation.\n\n"
        "First, who is the customer?"
    )
    
    return CUSTOMER_NAME


async def customer_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Save the customer name and ask for items.
    
    Args:
        update: The Telegram update.
        context: The conversation context.
        
    Returns:
        int: The next conversation state.
    """
    customer_name = update.message.text.strip()
    context.user_data["customer_name"] = customer_name
    
    await update.message.reply_text(
        f"Great! Creating quotation for *{customer_name}*.\n\n"
        "Now, let's add items to the quotation. What's the first item name?",
        parse_mode="Markdown"
    )
    
    return ITEM_NAME


async def item_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Save the item name and ask for quantity.
    
    Args:
        update: The Telegram update.
        context: The conversation context.
        
    Returns:
        int: The next conversation state.
    """
    item_name = update.message.text.strip()
    
    # Initialize current item
    context.user_data[CURRENT_ITEM] = {"item_name": item_name}
    
    await update.message.reply_text(
        f"Item: *{item_name}*\n\n"
        "What's the quantity?",
        parse_mode="Markdown"
    )
    
    return ITEM_QUANTITY


async def item_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Save the item quantity and ask for unit price.
    
    Args:
        update: The Telegram update.
        context: The conversation context.
        
    Returns:
        int: The next conversation state.
    """
    try:
        quantity = float(update.message.text.strip())
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
            
        context.user_data[CURRENT_ITEM]["quantity"] = quantity
        
        await update.message.reply_text(
            f"Quantity: *{quantity}*\n\n"
            "What's the unit price?",
            parse_mode="Markdown"
        )
        
        return ITEM_PRICE
        
    except ValueError:
        await update.message.reply_text(
            "Please enter a valid positive number for the quantity."
        )
        return ITEM_QUANTITY


async def item_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Save the item price and ask if more items should be added.
    
    Args:
        update: The Telegram update.
        context: The conversation context.
        
    Returns:
        int: The next conversation state.
    """
    try:
        unit_price = float(update.message.text.strip())
        if unit_price <= 0:
            raise ValueError("Price must be positive")
            
        # Complete the current item
        current_item = context.user_data[CURRENT_ITEM]
        current_item["unit_price"] = unit_price
        
        # Add to items list
        items_list = context.user_data[ITEMS_LIST]
        items_list.append(current_item)
        
        # Create a summary of the current item
        item_name = current_item["item_name"]
        quantity = current_item["quantity"]
        total = quantity * unit_price
        
        keyboard = [
            [
                InlineKeyboardButton("Add Another Item", callback_data="add_item"),
                InlineKeyboardButton("Done", callback_data="done")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Added: *{item_name}* x {quantity} @ ${unit_price:,.2f} = ${total:,.2f}\n\n"
            f"You have {len(items_list)} item(s) in your quotation.\n\n"
            "Would you like to add another item or are you done?",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
        return COLLECTING_ITEMS
        
    except ValueError:
        await update.message.reply_text(
            "Please enter a valid positive number for the unit price."
        )
        return ITEM_PRICE


async def collecting_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the user's choice to add more items or finish.
    
    Args:
        update: The Telegram update.
        context: The conversation context.
        
    Returns:
        int: The next conversation state.
    """
    query = update.callback_query
    await query.answer()
    
    if query.data == "add_item":
        await query.edit_message_text(
            "Let's add another item. What's the item name?"
        )
        return ITEM_NAME
    else:  # query.data == "done"
        await query.edit_message_text(
            "Great! All items added.\n\n"
            "Any notes or terms to add to the quotation? (Type 'none' if not)"
        )
        return NOTES


async def handle_manual_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle when the user types 'done' instead of using buttons.
    
    Args:
        update: The Telegram update.
        context: The conversation context.
        
    Returns:
        int: The next conversation state.
    """
    if update.message.text.lower().strip() == "done":
        await update.message.reply_text(
            "Great! All items added.\n\n"
            "Any notes or terms to add to the quotation? (Type 'none' if not)"
        )
        return NOTES
    
    # If not "done", treat as a new item name
    return await item_name(update, context)


async def notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Save notes and generate the quotation.
    
    Args:
        update: The Telegram update.
        context: The conversation context.
        
    Returns:
        int: The next conversation state.
    """
    notes_text = update.message.text.strip()
    if notes_text.lower() == "none":
        notes_text = None
    
    context.user_data["notes"] = notes_text
    
    await update.message.reply_text(
        "Generating your quotation PDF...",
    )
    
    # Create the quotation
    try:
        # Convert the collected items to QuotationItem objects
        items = []
        for item_data in context.user_data[ITEMS_LIST]:
            items.append(QuotationItem(
                item_name=item_data["item_name"],
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"]
            ))
        
        # Create the quotation data object
        quotation = QuotationData(
            customer_name=context.user_data["customer_name"],
            items=items,
            notes=context.user_data["notes"]
        )
        
        # Generate the PDF
        pdf_generator = PDFGenerator()
        pdf_path = pdf_generator.generate_pdf(quotation)
        
        # Send the file
        with open(pdf_path, "rb") as pdf_file:
            await update.message.reply_document(
                document=pdf_file,
                filename=pdf_path.name,
                caption=f"Here's your quotation for {quotation.customer_name}!\n\nQuotation Number: {quotation.quotation_number}"
            )
        
        await update.message.reply_text(
            "Quotation generated successfully! Type /start or /newquote to create another one."
        )
        
        # Clean up context data
        context.user_data.clear()
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error generating quotation: {e}")
        await update.message.reply_text(
            "Sorry, there was an error generating your quotation. Please try again later."
        )
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel the conversation.
    
    Args:
        update: The Telegram update.
        context: The conversation context.
        
    Returns:
        int: ConversationHandler.END to end the conversation.
    """
    await update.message.reply_text(
        "Quotation creation cancelled. Type /start or /newquote to create a new quotation."
    )
    context.user_data.clear()
    return ConversationHandler.END


def register_handlers(application) -> None:
    """
    Register conversation handlers with the application.
    
    Args:
        application: The Telegram application.
    """
    # Create conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("newquote", start)
        ],
        states={
            CUSTOMER_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, customer_name)
            ],
            ITEM_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, item_name)
            ],
            ITEM_QUANTITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, item_quantity)
            ],
            ITEM_PRICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, item_price)
            ],
            COLLECTING_ITEMS: [
                CallbackQueryHandler(collecting_items),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_manual_done)
            ],
            NOTES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, notes)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(conv_handler)
