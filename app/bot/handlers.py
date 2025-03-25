"""
Handlers for the quotation bot conversation.
"""

from telegram import Update, Chat
from telegram.ext import ContextTypes, ConversationHandler
from app.utils.models import QuotationData, QuotationItem
from app.utils.test_pdf import generate_quotation_html
from .constants import (
    CUSTOMER_NAME,
    CUSTOMER_COMPANY,
    CUSTOMER_ADDRESS,
    CUSTOMER_PHONE,
    CUSTOMER_EMAIL,
    ADD_ITEMS,
    ITEM_NAME,
    ITEM_QUANTITY,
    ITEM_PRICE,
    TERMS,
    NOTES,
    ISSUED_BY,
    DISCOUNT,
    quotation_data
)

async def handle_customer_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle customer name input."""
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    
    # If message is from group but we expect private chat, ignore it
    if chat_type != Chat.PRIVATE and context.user_data.get('expect_private'):
        return CUSTOMER_NAME
    
    quotation_data[user_id]['customer_name'] = update.message.text
    
    await update.message.reply_text(
        "Great! Now, please enter the customer's company name:"
    )
    return CUSTOMER_COMPANY

async def handle_customer_company(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle customer company input."""
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    
    # If message is from group but we expect private chat, ignore it
    if chat_type != Chat.PRIVATE and context.user_data.get('expect_private'):
        return CUSTOMER_COMPANY
        
    quotation_data[user_id]['customer_company'] = update.message.text
    
    await update.message.reply_text(
        "Please enter the customer's address:"
    )
    return CUSTOMER_ADDRESS

async def handle_customer_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle customer address input."""
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    
    # If message is from group but we expect private chat, ignore it
    if chat_type != Chat.PRIVATE and context.user_data.get('expect_private'):
        return CUSTOMER_ADDRESS
    
    quotation_data[user_id]['customer_address'] = update.message.text
    
    await update.message.reply_text(
        "Please enter the customer's phone number:"
    )
    return CUSTOMER_PHONE

async def handle_customer_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle customer phone input."""
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    
    # If message is from group but we expect private chat, ignore it
    if chat_type != Chat.PRIVATE and context.user_data.get('expect_private'):
        return CUSTOMER_PHONE
    
    quotation_data[user_id]['customer_phone'] = update.message.text
    
    await update.message.reply_text(
        "Please enter the customer's email address:"
    )
    return CUSTOMER_EMAIL

async def handle_customer_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle customer email input."""
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    
    # If message is from group but we expect private chat, ignore it
    if chat_type != Chat.PRIVATE and context.user_data.get('expect_private'):
        return CUSTOMER_EMAIL
    
    quotation_data[user_id]['customer_email'] = update.message.text
    
    await update.message.reply_text(
        "Now let's add items to the quotation.\n"
        "Please enter the name of the first item:"
    )
    return ITEM_NAME

async def handle_item_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle item name input."""
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    
    # If message is from group but we expect private chat, ignore it
    if chat_type != Chat.PRIVATE and context.user_data.get('expect_private'):
        return ITEM_NAME
    
    context.user_data['current_item'] = {'name': update.message.text}
    
    await update.message.reply_text(
        "Please enter the quantity:"
    )
    return ITEM_QUANTITY

async def handle_item_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle item quantity input."""
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    
    # If message is from group but we expect private chat, ignore it
    if chat_type != Chat.PRIVATE and context.user_data.get('expect_private'):
        return ITEM_QUANTITY
    
    try:
        quantity = int(update.message.text)
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        context.user_data['current_item']['quantity'] = quantity
        
        await update.message.reply_text(
            "Please enter the unit price:"
        )
        return ITEM_PRICE
    
    except ValueError:
        await update.message.reply_text(
            "Please enter a valid positive number for quantity:"
        )
        return ITEM_QUANTITY

async def handle_item_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle item price input."""
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    
    # If message is from group but we expect private chat, ignore it
    if chat_type != Chat.PRIVATE and context.user_data.get('expect_private'):
        return ITEM_PRICE
    
    try:
        price = float(update.message.text.replace(',', ''))
        if price <= 0:
            raise ValueError("Price must be positive")
        
        current_item = context.user_data['current_item']
        current_item['price'] = price
        
        # Add the item to the quotation
        quotation_data[user_id]['items'].append(
            QuotationItem(
                item_name=current_item['name'],
                quantity=current_item['quantity'],
                unit_price=current_item['price']
            )
        )
        
        # Clear the current item
        context.user_data['current_item'] = None
        
        # Ask if user wants to add more items
        await update.message.reply_text(
            "Item added! Would you like to add another item?\n"
            "Send 'yes' to add another item, or 'no' to continue:"
        )
        return ADD_ITEMS
    
    except ValueError:
        await update.message.reply_text(
            "Please enter a valid positive number for price:"
        )
        return ITEM_PRICE

async def handle_add_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle whether to add more items."""
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    
    # If message is from group but we expect private chat, ignore it
    if chat_type != Chat.PRIVATE and context.user_data.get('expect_private'):
        return ADD_ITEMS
    
    response = update.message.text.lower()
    
    if response == 'yes':
        await update.message.reply_text(
            "Please enter the name of the next item:"
        )
        return ITEM_NAME
    
    elif response == 'no':
        await update.message.reply_text(
            "Please enter the terms and conditions for this quotation:"
        )
        return TERMS
    
    else:
        await update.message.reply_text(
            "Please reply with 'yes' to add another item, or 'no' to continue:"
        )
        return ADD_ITEMS

async def handle_terms(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle terms input."""
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    
    # If message is from group but we expect private chat, ignore it
    if chat_type != Chat.PRIVATE and context.user_data.get('expect_private'):
        return TERMS
    
    quotation_data[user_id]['terms'] = update.message.text
    
    await update.message.reply_text(
        "Please enter any additional notes (or send 'none' if none):"
    )
    return NOTES

async def handle_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle notes input."""
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    
    # If message is from group but we expect private chat, ignore it
    if chat_type != Chat.PRIVATE and context.user_data.get('expect_private'):
        return NOTES
    
    notes = update.message.text
    quotation_data[user_id]['notes'] = notes if notes.lower() != 'none' else ''
    
    await update.message.reply_text(
        "Please enter the name of the person issuing this quotation:"
    )
    return ISSUED_BY

async def handle_issued_by(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle issued by input."""
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    
    # If message is from group but we expect private chat, ignore it
    if chat_type != Chat.PRIVATE and context.user_data.get('expect_private'):
        return ISSUED_BY
    
    quotation_data[user_id]['issued_by'] = update.message.text
    
    await update.message.reply_text(
        "Finally, enter the discount amount (or send '0' for no discount):"
    )
    return DISCOUNT

async def handle_discount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle discount input and generate quotation."""
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    
    # If message is from group but we expect private chat, ignore it
    if chat_type != Chat.PRIVATE and context.user_data.get('expect_private'):
        return DISCOUNT
    
    try:
        discount = float(update.message.text.replace(',', ''))
        if discount < 0:
            raise ValueError("Discount cannot be negative")
        
        data = quotation_data[user_id]
        
        # Create QuotationData object
        quotation = QuotationData(
            customer_name=data['customer_name'],
            customer_company=data['customer_company'],
            customer_address=data['customer_address'],
            customer_phone=data['customer_phone'],
            customer_email=data['customer_email'],
            items=data['items'],
            terms=data['terms'],
            notes=data['notes'],
            issued_by=data['issued_by'],
            discount=discount
        )
        
        # Generate HTML
        html = generate_quotation_html(quotation)
        
        # Save HTML file
        from pathlib import Path
        output_dir = Path(__file__).resolve().parent.parent.parent / 'temp'
        output_dir.mkdir(exist_ok=True)
        html_file = output_dir / f"{quotation.filename}.html"
        html_file.write_text(html, encoding='utf-8')
        
        # Send the file to user
        await update.message.reply_document(
            document=html_file,
            filename=f"{quotation.filename}.html",
            caption=(
                "Here's your quotation! 📄\n"
                "Open this HTML file in your browser to view or save as PDF.\n\n"
                f"Quotation Number: {quotation.quotation_number}\n"
                f"Total Amount: RM {quotation.grand_total:,.2f}"
            )
        )
        
        # If this conversation was started in a group, send a notification to the group
        if context.user_data.get('expect_private') and context.user_data.get('original_chat_id'):
            try:
                await context.bot.send_message(
                    chat_id=context.user_data['original_chat_id'],
                    text=f"@{update.effective_user.username or update.effective_user.first_name} has completed their quotation!"
                )
            except Exception as e:
                # Log error but don't fail if group message can't be sent
                print(f"Error sending group notification: {e}")
        
        # Clean up
        del quotation_data[user_id]
        
        await update.message.reply_text(
            "Quotation generated successfully! 🎉\n"
            "Use /newquote to create another quotation."
        )
        
        return ConversationHandler.END
    
    except ValueError:
        await update.message.reply_text(
            "Please enter a valid number for the discount:"
        )
        return DISCOUNT 