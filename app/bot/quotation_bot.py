"""
Telegram bot for generating quotations.
"""

import logging
from pathlib import Path
from telegram import Update, Chat
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    filters
)
from app.config.settings import TELEGRAM_BOT_TOKEN, ALLOWED_USER_IDS, ALLOWED_GROUP_IDS
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
from .handlers import (
    handle_customer_name,
    handle_customer_company,
    handle_customer_address,
    handle_customer_phone,
    handle_customer_email,
    handle_item_name,
    handle_item_quantity,
    handle_item_price,
    handle_add_items,
    handle_terms,
    handle_notes,
    handle_issued_by,
    handle_discount
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def is_authorized(update: Update) -> bool:
    """Check if the user or chat is authorized to use the bot."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    
    logger.info(f"Authorization check - User ID: {user_id}, Chat ID: {chat_id}, Chat Type: {chat_type}")
    logger.info(f"Allowed Users: {ALLOWED_USER_IDS}")
    logger.info(f"Allowed Groups: {ALLOWED_GROUP_IDS}")
    
    # Check if it's a private chat with an authorized user
    if chat_type == Chat.PRIVATE:
        is_allowed = user_id in ALLOWED_USER_IDS
        logger.info(f"Private chat authorization result: {is_allowed}")
        return is_allowed
    
    # Check if it's a group chat that's authorized
    if chat_type in [Chat.GROUP, Chat.SUPERGROUP]:
        is_allowed = chat_id in ALLOWED_GROUP_IDS
        logger.info(f"Group chat authorization result: {is_allowed}")
        return is_allowed
        
    return False

async def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    
    logger.info(f"Start command received - User ID: {user_id}, Chat ID: {chat_id}, Chat Type: {chat_type}")
    
    if not is_authorized(update):
        logger.warning(f"Unauthorized access attempt - User ID: {user_id}, Chat ID: {chat_id}")
        await update.message.reply_text(
            "Sorry, you are not authorized to use this bot. "
            "Please contact the administrator for access."
        )
        return
    
    chat_type = update.effective_chat.type
    
    if chat_type == Chat.PRIVATE:
        message = (
            "Welcome to the Quotation Generator Bot! 🤖\n\n"
            "Available commands:\n"
            "/newquote - Start creating a new quotation\n"
            "/cancel - Cancel the current operation\n"
            "/help - Show this help message"
        )
    else:
        message = (
            "Hello! I'm the Quotation Generator Bot! 🤖\n\n"
            "Available commands:\n"
            "/newquote - Start creating a new quotation\n"
            "/cancel - Cancel the current operation\n"
            "/help - Show this help message\n\n"
            "Note: In a group chat, please mention me when using commands like: @QuotationBot /newquote"
        )
    
    await update.message.reply_text(message)

async def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    if not is_authorized(update):
        await update.message.reply_text(
            "Sorry, you are not authorized to use this bot."
        )
        return
    
    chat_type = update.effective_chat.type
    
    if chat_type == Chat.PRIVATE:
        message = (
            "Here's how to use the Quotation Generator Bot:\n\n"
            "1. /newquote - Start creating a new quotation\n"
            "2. Follow the prompts to enter:\n"
            "   - Customer details\n"
            "   - Items (name, quantity, price)\n"
            "   - Terms and conditions\n"
            "   - Notes\n"
            "   - Discount (if any)\n"
            "3. The bot will generate a quotation in HTML format\n"
            "4. Open the HTML file in a browser to save as PDF\n\n"
            "/cancel - Cancel the current operation at any time"
        )
    else:
        message = (
            "Here's how to use the Quotation Generator Bot in this group:\n\n"
            "1. Use /newquote to start creating a quotation\n"
            "2. The bot will start a private chat with you to collect all necessary information\n"
            "3. Once completed, the quotation will be sent to you privately\n"
            "4. You can then share the quotation with the group if needed\n\n"
            "/cancel - Cancel the current operation at any time"
        )
    
    await update.message.reply_text(message)

async def new_quote(update: Update, context: CallbackContext) -> int:
    """Start the quotation creation process."""
    if not is_authorized(update):
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return ConversationHandler.END
    
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    
    # Initialize quotation data for this user
    quotation_data[user_id] = {
        'items': []
    }
    
    # Clear any previous user data
    context.user_data.clear()
    
    # If in a group chat, direct the user to private chat
    if chat_type in [Chat.GROUP, Chat.SUPERGROUP]:
        # Set flag to expect responses in private chat
        context.user_data['expect_private'] = True
        context.user_data['original_chat_id'] = update.effective_chat.id
        
        bot_username = context.bot.username
        await update.message.reply_text(
            f"I've sent you a private message to create your quotation. "
            f"Please check your private chat with me (@{bot_username})."
        )
        
        # Send a private message to the user
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "Let's create a new quotation! 📝\n\n"
                    "First, please enter the customer's name:"
                )
            )
            return CUSTOMER_NAME
        except Exception as e:
            logger.error(f"Could not send private message to user {user_id}: {e}")
            await update.message.reply_text(
                "Error: I couldn't send you a private message. "
                "Please start a private chat with me first and then try again."
            )
            return ConversationHandler.END
    
    # In private chat, continue as normal
    await update.message.reply_text(
        "Let's create a new quotation! 📝\n\n"
        "First, please enter the customer's name:"
    )
    
    return CUSTOMER_NAME

async def cancel(update: Update, context: CallbackContext) -> int:
    """Cancel and end the conversation."""
    if not is_authorized(update):
        await update.message.reply_text("Sorry, you are not authorized to use this bot.")
        return ConversationHandler.END
    
    user_id = update.effective_user.id
    if user_id in quotation_data:
        del quotation_data[user_id]
    
    await update.message.reply_text(
        "Quotation creation cancelled. All data has been cleared.\n"
        "Use /newquote to start again."
    )
    
    return ConversationHandler.END

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('newquote', new_quote)],
        states={
            CUSTOMER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_customer_name)],
            CUSTOMER_COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_customer_company)],
            CUSTOMER_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_customer_address)],
            CUSTOMER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_customer_phone)],
            CUSTOMER_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_customer_email)],
            ITEM_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_item_name)],
            ITEM_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_item_quantity)],
            ITEM_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_item_price)],
            ADD_ITEMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_add_items)],
            TERMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_terms)],
            NOTES: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_notes)],
            ISSUED_BY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_issued_by)],
            DISCOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_discount)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        name="quotation_conversation",
        persistent=False,
        allow_reentry=True,
        per_chat=False,
        per_user=True
    )

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler)

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 