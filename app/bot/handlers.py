"""
Handlers for the quotation bot conversation.
"""

from telegram import Update, Chat, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from app.utils.models import QuotationData, QuotationItem
from app.utils.test_pdf import generate_quotation_html
from app.utils.gpt_quotation import GPTQuotationParser
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
    CHOOSE_MODE,
    AI_INPUT,
    AI_CLARIFICATION,
    AI_SUMMARY,
    quotation_data
)
from typing import Dict, List, Tuple, Any, Optional
import logging
import os
from datetime import datetime
from app.utils.file_cleanup import schedule_file_cleanup

# Initialize GPT parser
gpt_parser = GPTQuotationParser()

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
        
        # Get the count of existing items to create the item number
        item_count = len(quotation_data[user_id]['items']) + 1
        item_number = f"{item_count:03d}"  # Format as 001, 002, etc.
        
        # Add the item to the quotation
        quotation_data[user_id]['items'].append(
            QuotationItem(
                item_no=item_number,
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

async def handle_mode_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user's choice between step-by-step and AI-powered modes."""
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    
    if chat_type != Chat.PRIVATE and context.user_data.get('expect_private'):
        return CHOOSE_MODE
    
    # Handle callback query (button press)
    if update.callback_query:
        await update.callback_query.answer()  # Acknowledge the button press
        
        if update.callback_query.data == "mode_step":
            # Initialize quotation data for step-by-step mode
            quotation_data[user_id] = {'items': []}
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Great! Let's create your quotation step by step.\n"
                "First, please enter the customer's name:"
            )
            return CUSTOMER_NAME
        
        elif update.callback_query.data == "mode_ai":
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Awesome! Please include the following in one message:\n"
                "- Customer name\n"
                "- Company name\n"
                "- Address\n"
                "- Phone & email\n"
                "- Items (with name, quantity, unit price)\n"
                "- Terms & conditions\n"
                "- Discount (if any)\n"
                "- Issued by (optional)\n"
                "I'll take care of the rest! 🚀"
            )
            return AI_INPUT
    
    # Handle text message (fallback)
    elif update.message:
        if update.message.text.lower() == "step-by-step 🧱":
            # Initialize quotation data for step-by-step mode
            quotation_data[user_id] = {'items': []}
            await update.message.reply_text(
                "Great! Let's create your quotation step by step.\n"
                "First, please enter the customer's name:"
            )
            return CUSTOMER_NAME
        
        elif update.message.text.lower() == "all at once 🚀":
            await update.message.reply_text(
                "Awesome! Please include the following in one message:\n"
                "- Customer name\n"
                "- Company name\n"
                "- Address\n"
                "- Phone & email\n"
                "- Items (with name, quantity, unit price)\n"
                "- Terms & conditions\n"
                "- Discount (if any)\n"
                "- Issued by (optional)\n"
                "I'll take care of the rest! 🚀"
            )
            return AI_INPUT
        
        else:
            await update.message.reply_text(
                "Please choose a mode by clicking one of the buttons below.",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("Step-by-step 🧱", callback_data="mode_step"),
                        InlineKeyboardButton("All at once 🚀", callback_data="mode_ai")
                    ]
                ])
            )
            return CHOOSE_MODE
    
    return CHOOSE_MODE

def create_clarification_message(extracted_data, missing_fields):
    """Create a user-friendly clarification message with context from extracted data."""
    logger = logging.getLogger(__name__)
    
    # Create a message showing what was understood so far
    understood_msg = "I understood these details:\n"
    if extracted_data:
        # Field display mapping 
        field_display = {
            "customer_name": "Customer name",
            "customer_company": "Company name",
            "customer_address": "Address",
            "customer_phone": "Phone number",
            "customer_email": "Email address", 
            "terms": "Terms & conditions",
            "discount": "Discount",
            "issued_by": "Issued by"
        }
        
        for key, value in extracted_data.items():
            if key != 'items' and value:  # Skip items and empty values
                friendly_key = field_display.get(key, key.replace('_', ' ').capitalize())
                understood_msg += f"- {friendly_key}: {value}\n"
        
        # Add items if they exist
        if 'items' in extracted_data and extracted_data['items']:
            understood_msg += "- Items:\n"
            for item in extracted_data['items']:
                understood_msg += f"  - {item.get('name', 'Unknown')}: {item.get('quantity', 0)} × {item.get('unit_price', 0)}\n"
    else:
        understood_msg = "I couldn't understand any details from your message.\n"
    
    # Create the missing fields section
    missing_msg = "\nI need the following information:\n"
    
    # Field display mapping for missing fields
    missing_field_display = {
        "customer_name": "Customer name",
        "customer_company": "Company name", 
        "customer_address": "Address",
        "customer_phone": "Phone number",
        "customer_email": "Email address",
        "items": "Items (with name, quantity, unit price)",
        "terms": "Terms & conditions",
        "discount": "Discount (if any)",
        "issued_by": "Issued by (who's creating this quote)"
    }
    
    for field in missing_fields:
        friendly_field = missing_field_display.get(field, field.replace('_', ' ').capitalize())
        missing_msg += f"- {friendly_field}\n"
    
    return understood_msg + missing_msg + "\nPlease provide these details:"

async def handle_ai_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle freeform input for AI-powered quotation creation."""
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    logger = logging.getLogger(__name__)
    
    if chat_type != Chat.PRIVATE and context.user_data.get('expect_private'):
        return AI_INPUT
    
    # Show processing message
    processing_msg = await update.message.reply_text(
        "Processing your input... 🤔"
    )
    
    try:
        # Extract data using GPT
        logger.info(f"Processing AI input from user {user_id}: {update.message.text[:50]}...")
        data, missing_fields = await gpt_parser.extract_quotation_data(update.message.text)
        
        # Initialize quotation data
        quotation_data[user_id] = data if data else {'items': []}
        
        if missing_fields:
            # Store the extracted data and missing fields
            context.user_data['extracted_data'] = data
            context.user_data['missing_fields'] = missing_fields
            
            # Generate clarification message with context
            clarification_msg = create_clarification_message(data, missing_fields)
            
            logger.info(f"Asking for clarification from user {user_id}: {missing_fields}")
            # Send a new message instead of editing the existing one
            await update.message.reply_text(clarification_msg)
            return AI_CLARIFICATION
        
        # Validate the extracted data
        validation_issues = await gpt_parser.validate_quotation_data(data)
        logger.info(f"Validation issues for user {user_id}: {validation_issues}")
        
        if validation_issues:
            # Send a new message instead of editing the existing one
            await update.message.reply_text(
                "I found some issues with the data:\n" +
                "\n".join(f"- {issue}" for issue in validation_issues) +
                "\n\nPlease provide the correct information:"
            )
            return AI_INPUT
        
        # Generate summary
        logger.info(f"Generating summary for user {user_id}")
        summary = await gpt_parser.generate_summary(data)
        
        # Show summary and ask for confirmation with a new message
        await update.message.reply_text(
            f"{summary}\n\nDoes this look correct?",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Yes, generate quote ✅", callback_data="confirm_yes"),
                    InlineKeyboardButton("No, try again 🔄", callback_data="confirm_no")
                ]
            ])
        )
        return AI_SUMMARY
        
    except Exception as e:
        # Initialize empty data to avoid errors
        quotation_data[user_id] = {'items': []}
        
        # Log the error with more details
        logger.error(f"Error in AI input processing for user {user_id}: {str(e)}", exc_info=True)
        
        # Provide a more helpful error message to the user with a new message
        await update.message.reply_text(
            "I encountered an error processing your input. The error has been logged.\n\n"
            "You can:\n"
            "1. Try again with clearer formatting\n"
            "2. Use the step-by-step mode (use /newquote to restart)\n\n"
            f"Error details: {str(e)[:100]}"
        )
        return AI_INPUT

async def handle_ai_clarification(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle clarification responses for AI-powered quotation."""
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    logger = logging.getLogger(__name__)
    
    if chat_type != Chat.PRIVATE and context.user_data.get('expect_private'):
        return AI_CLARIFICATION
    
    # Show processing message
    processing_msg = await update.message.reply_text(
        "Processing your clarification... 🤔"
    )
    
    try:
        logger.info(f"Processing clarification from user {user_id}: {update.message.text[:50]}...")
        
        # Get original data
        original_data = context.user_data.get('extracted_data', {})
        original_missing_fields = context.user_data.get('missing_fields', [])
        
        logger.info(f"Original data had fields: {list(original_data.keys())}")
        logger.info(f"Original missing fields: {original_missing_fields}")
        
        # Create a combined message for better context
        # This gives the AI more context by including both the original data and the new clarification
        combined_msg = "Previous information:\n"
        for key, value in original_data.items():
            if key != 'items':  # Handle items separately
                combined_msg += f"- {key}: {value}\n"
        
        # Add items if they exist
        if 'items' in original_data and original_data['items']:
            combined_msg += "- items:\n"
            for item in original_data['items']:
                combined_msg += f"  - {item.get('name', 'Unknown')}, {item.get('quantity', 0)} unit, {item.get('unit_price', 0)}/unit\n"
        
        # Add the new clarification
        combined_msg += "\nAdditional information:\n" + update.message.text
        
        logger.info(f"Created combined context message: {combined_msg[:100]}...")
        
        # Extract data with full context
        clarification_data, new_missing_fields = await gpt_parser.extract_quotation_data(combined_msg)
        
        # Smart merge of the data - we need to be careful with the items
        merged_data = {}
        
        # First, copy all data from original
        for key, value in original_data.items():
            merged_data[key] = value
        
        # Then, update with clarification data, but handle items specially
        for key, value in clarification_data.items():
            if key == 'items' and 'items' in original_data and original_data['items']:
                # Keep original items unless clarification specifically updates them
                continue
            merged_data[key] = value
        
        logger.info(f"Merged data has fields: {list(merged_data.keys())}")
        
        # Update missing fields - only keep fields that are still missing after clarification
        missing_fields = []
        for field in original_missing_fields:
            if field not in clarification_data or not clarification_data[field]:
                missing_fields.append(field)
        
        # Add any new missing fields discovered
        for field in new_missing_fields:
            if field not in missing_fields:
                missing_fields.append(field)
        
        logger.info(f"Updated missing fields: {missing_fields}")
        
        # Store updated data
        quotation_data[user_id] = merged_data
        
        if missing_fields:
            # Still have missing fields
            context.user_data['extracted_data'] = merged_data
            context.user_data['missing_fields'] = missing_fields
            
            # Use the helper function to create a more informative message
            clarification_msg = create_clarification_message(merged_data, missing_fields)
            
            # Send a new message instead of editing the existing one
            await update.message.reply_text(clarification_msg)
            return AI_CLARIFICATION
        
        # Validate the merged data
        validation_issues = await gpt_parser.validate_quotation_data(merged_data)
        logger.info(f"Validation issues after clarification for user {user_id}: {validation_issues}")
        
        if validation_issues:
            # Send a new message instead of editing the existing one
            await update.message.reply_text(
                "I found some issues with the data:\n" +
                "\n".join(f"- {issue}" for issue in validation_issues) +
                "\n\nPlease provide the correct information:"
            )
            return AI_INPUT
        
        # Generate summary
        logger.info(f"Generating summary for clarified data for user {user_id}")
        summary = await gpt_parser.generate_summary(merged_data)
        
        # Show summary and ask for confirmation with a new message
        await update.message.reply_text(
            f"{summary}\n\nDoes this look correct?",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Yes, generate quote ✅", callback_data="confirm_yes"),
                    InlineKeyboardButton("No, try again 🔄", callback_data="confirm_no")
                ]
            ])
        )
        return AI_SUMMARY
        
    except Exception as e:
        # Ensure quotation_data is initialized
        if user_id not in quotation_data:
            quotation_data[user_id] = {'items': []}
            
        # Log the error with more details
        logger.error(f"Error in AI clarification processing for user {user_id}: {str(e)}", exc_info=True)
        
        # Provide a more helpful error message to the user with a new message
        await update.message.reply_text(
            "I encountered an error processing your clarification. The error has been logged.\n\n"
            "You can:\n"
            "1. Try again with clearer information\n"
            "2. Use /newquote to start over\n\n"
            f"Error details: {str(e)[:100]}"
        )
        return AI_CLARIFICATION

async def handle_ai_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle confirmation of AI-generated quotation summary."""
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    logger = logging.getLogger(__name__)
    
    if chat_type != Chat.PRIVATE and context.user_data.get('expect_private'):
        return AI_SUMMARY
    
    # Make sure we're handling a callback query
    if not update.callback_query:
        await update.message.reply_text(
            "Please use the buttons to confirm or reject the summary.",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Yes, generate quote ✅", callback_data="confirm_yes"),
                    InlineKeyboardButton("No, try again 🔄", callback_data="confirm_no")
                ]
            ])
        )
        return AI_SUMMARY
    
    # Acknowledge the callback query
    await update.callback_query.answer()
    
    if update.callback_query.data == "confirm_no":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="No problem! Let's try again. Please provide all the quotation details in one message:"
        )
        return AI_INPUT
    
    elif update.callback_query.data == "confirm_yes":
        try:
            # Generate quotation
            data = quotation_data.get(user_id, {})
            
            if not data:
                logger.error(f"No data found for user {user_id} in quotation_data")
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Error: No quotation data found. Please start again with /newquote"
                )
                return ConversationHandler.END
                
            logger.info(f"Generating quote for user {user_id} with data fields: {list(data.keys())}")
            
            # Run the validator to normalize all values
            validation_issues = await gpt_parser.validate_quotation_data(data)
            
            # Check if there are still critical issues that would prevent HTML generation
            critical_issues = []
            for issue in validation_issues:
                if "Invalid price" in issue or "No valid items" in issue:
                    critical_issues.append(issue)
            
            if critical_issues:
                logger.error(f"Critical validation issues for user {user_id}: {critical_issues}")
                
                # Create an informative message asking for specific corrections
                error_message = "I found critical issues that prevent generating the quotation:\n"
                for issue in critical_issues:
                    error_message += f"- {issue}\n"
                
                error_message += "\nPlease address these specific issues and try again:"
                
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=error_message
                )
                return AI_INPUT
            
            # Fill in required fields with N/A if missing
            required_fields = ["customer_name", "customer_company", "customer_address", 
                               "customer_phone", "customer_email"]
            
            for field in required_fields:
                if field not in data or not data[field]:
                    data[field] = "N/A"
                    logger.info(f"Set missing {field} to N/A")
            
            # Convert items to QuotationItem objects
            items = []
            if 'items' in data and data['items']:
                for i, item in enumerate(data['items']):
                    try:
                        # Ensure all required fields are present with normalized values
                        item_name = item.get('name', f'Item {i+1}')
                        quantity = item.get('quantity', 1)
                        unit_price = item.get('unit_price', 0)
                        
                        # Convert to proper types if they're strings (should already be normalized by validator)
                        if isinstance(quantity, str):
                            import re
                            quantity = float(re.sub(r'[^0-9.]', '', quantity)) if re.sub(r'[^0-9.]', '', quantity) else 1
                        
                        if isinstance(unit_price, str):
                            import re
                            unit_price = float(re.sub(r'[^0-9.]', '', unit_price)) if re.sub(r'[^0-9.]', '', unit_price) else 0
                        
                        items.append(
                            QuotationItem(
                                item_no=f"{i+1:03d}",
                                item_name=item_name,
                                quantity=quantity,
                                unit_price=unit_price
                            )
                        )
                    except Exception as item_err:
                        logger.error(f"Error processing item {i}: {str(item_err)}")
            
            if not items:
                logger.error(f"No items found for user {user_id}")
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Error: No valid items found in quotation data. Please start again with /newquote"
                )
                return ConversationHandler.END
            
            # Process discount
            discount = 0
            if 'discount' in data:
                try:
                    if isinstance(data['discount'], (int, float)):
                        discount = data['discount']
                    elif isinstance(data['discount'], str) and data['discount'].strip():
                        import re
                        discount_str = re.sub(r'[^0-9.]', '', data['discount'])
                        discount = float(discount_str) if discount_str else 0
                except (ValueError, TypeError) as e:
                    logger.error(f"Error processing discount: {str(e)}")
            
            # Ensure terms is not empty or None
            terms = data.get('terms', '')
            if not terms or terms.strip() == '':
                terms = "Payment terms not specified"
            
            # Create QuotationData object
            quotation = QuotationData(
                customer_name=data.get('customer_name', 'N/A'),
                customer_company=data.get('customer_company', 'N/A'),
                customer_address=data.get('customer_address', 'N/A'),
                customer_phone=data.get('customer_phone', 'N/A'),
                customer_email=data.get('customer_email', 'N/A'),
                items=items,
                terms=terms,  # Use the validated terms
                notes=data.get('notes', ''),  # Use empty string if not provided
                issued_by=data.get('issued_by', 'Not specified'),  # Use default value if not provided
                discount=discount
            )
            
            # Generate HTML quotation
            html_content = generate_quotation_html(quotation)
            
            # Save and send the quotation
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Generating your quotation... 📄"
            )
            
            # Make sure temp directory exists
            os.makedirs("temp", exist_ok=True)
            
            # Save HTML file
            html_path = f"temp/quotation_{user_id}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            # Send the file
            await context.bot.send_document(
                chat_id=user_id,
                document=open(html_path, "rb"),
                filename="quotation.html",
                caption="Here's your quotation! 📄\nOpen it in a browser to view or save as PDF."
            )
            
            # Schedule file cleanup (10 minutes = 600 seconds)
            schedule_file_cleanup(html_path, 600)
            
            # Clean up
            if user_id in quotation_data:
                del quotation_data[user_id]
            
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"Error generating quotation for user {user_id}: {str(e)}", exc_info=True)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"I encountered an error generating your quotation: {str(e)[:100]}\n\n"
                "Please try again with /newquote"
            )
            return ConversationHandler.END
    
    # Default fallback
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I didn't understand your response. Please use /newquote to start over."
    )
    return AI_SUMMARY

async def handle_ai_additional_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle additional text input during AI summary state to update quotation data."""
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    logger = logging.getLogger(__name__)
    
    if chat_type != Chat.PRIVATE and context.user_data.get('expect_private'):
        return AI_SUMMARY
    
    # Process the additional input
    additional_text = update.message.text
    logger.info(f"Processing additional input in AI_SUMMARY state: {additional_text}")
    
    # Show processing message
    processing_msg = await update.message.reply_text(
        "Processing your additional information... 🤔"
    )
    
    try:
        # Get current data
        current_data = quotation_data.get(user_id, {})
        if not current_data:
            current_data = {'items': []}
            quotation_data[user_id] = current_data
        
        # Create a combined message with current data for context
        combined_msg = "Previous information:\n"
        for key, value in current_data.items():
            if key != 'items':  # Handle items separately
                combined_msg += f"- {key}: {value}\n"
        
        # Add items if they exist
        if 'items' in current_data and current_data['items']:
            combined_msg += "- items:\n"
            for item in current_data['items']:
                combined_msg += f"  - {item.get('name', 'Unknown')}, {item.get('quantity', 0)} unit, {item.get('unit_price', 0)}/unit\n"
        
        # Add the additional info
        combined_msg += "\nAdditional information:\n" + additional_text
        
        # Extract data with the combined context
        updated_data, missing_fields = await gpt_parser.extract_quotation_data(combined_msg)
        
        # Run the validator to normalize values
        await gpt_parser.validate_quotation_data(updated_data)
        
        # Handle special cases first
        # Check for "issued by" specific input
        if additional_text.lower().startswith('issued by'):
            issued_by = additional_text[len('issued by'):].strip()
            if issued_by:
                updated_data['issued_by'] = issued_by
                logger.info(f"Directly set issued_by to: {issued_by}")
        
        # Check for "discount" specific input
        if any(word in additional_text.lower() for word in ['discount', 'discount:', 'discount is']):
            import re
            # Try to extract discount value
            discount_matches = re.search(r'discount\s*(?:is|:)?\s*(\d+\.?\d*|\.\d+)?\s*%?', additional_text.lower())
            if discount_matches and discount_matches.group(1):
                try:
                    updated_data['discount'] = float(discount_matches.group(1))
                    logger.info(f"Directly set discount to: {updated_data['discount']}")
                except (ValueError, TypeError):
                    pass
        
        # Smart merge with priority to new data
        for key, value in updated_data.items():
            if key == 'items' and 'items' in current_data and current_data['items']:
                # Don't overwrite existing items unless explicitly requested
                continue
            elif value:  # Only update if the value is not empty
                current_data[key] = value
        
        # Update the quotation data
        quotation_data[user_id] = current_data
        
        # Generate an updated summary
        summary = await gpt_parser.generate_summary(current_data)
        
        # Check if there are any missing required fields to prompt for
        required_fields = ["customer_name", "customer_company", "customer_address", 
                          "customer_phone", "customer_email", "items", "terms"]
        
        still_missing = [f for f in required_fields if f not in current_data or not current_data[f]]
        
        if still_missing:
            # Still need some information
            missing_fields_message = "\n\nI still need some information:\n" + "\n".join(f"- {field}" for field in still_missing)
            missing_fields_message += "\n\nPlease provide this information, or type 'N/A' if not applicable."
            
            # Send a new message instead of editing the existing one
            await update.message.reply_text(
                f"{summary}\n{missing_fields_message}",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("Continue anyway ✅", callback_data="confirm_yes"),
                        InlineKeyboardButton("Try again 🔄", callback_data="confirm_no")
                    ]
                ])
            )
        else:
            # Send a new message with the updated summary
            await update.message.reply_text(
                f"{summary}\n\nDoes this look correct?",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("Yes, generate quote ✅", callback_data="confirm_yes"),
                        InlineKeyboardButton("No, try again 🔄", callback_data="confirm_no")
                    ]
                ])
            )
        
        return AI_SUMMARY
        
    except Exception as e:
        logger.error(f"Error processing additional input: {str(e)}", exc_info=True)
        # Send a new message instead of editing the existing one
        await update.message.reply_text(
            f"I couldn't process your additional information. Error: {str(e)[:100]}\n\n"
            "You can try again or use the buttons to continue or restart."
        )
        return AI_SUMMARY 