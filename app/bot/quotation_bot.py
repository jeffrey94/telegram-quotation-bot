"""
Telegram bot for generating quotations.
"""

import logging
from pathlib import Path
from telegram import Update, Chat, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    filters,
    CallbackQueryHandler
)
from app.config import Config
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
    CHOOSE_MODE,
    AI_INPUT,
    AI_CLARIFICATION,
    AI_SUMMARY,
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
    handle_discount,
    handle_mode_choice,
    handle_ai_input,
    handle_ai_clarification,
    handle_ai_summary,
    handle_ai_additional_input
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def is_authorized(update: Update) -> bool:
    """Check if the user or chat is authorized to use the bot."""
    # If public mode is enabled, all users are authorized
    if Config.PUBLIC_MODE:
        return True
        
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    
    logger.info(f"Authorization check - User ID: {user_id}, Chat ID: {chat_id}, Chat Type: {chat_type}")
    logger.info(f"Public Mode: {Config.PUBLIC_MODE}")
    logger.info(f"Allowed Users: {Config.ALLOWED_USER_IDS}")
    logger.info(f"Allowed Groups: {Config.ALLOWED_GROUP_IDS}")
    
    # Check if it's a private chat with an authorized user
    if chat_type == Chat.PRIVATE:
        is_allowed = user_id in Config.ALLOWED_USER_IDS
        logger.info(f"Private chat authorization result: {is_allowed}")
        return is_allowed
    
    # Check if it's a group chat that's authorized
    if chat_type in [Chat.GROUP, Chat.SUPERGROUP]:
        is_allowed = chat_id in Config.ALLOWED_GROUP_IDS
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
            "This bot is currently in private mode and only authorized users can access it. "
            "Please contact the bot deployer for access privileges."
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
            "Sorry, you are not authorized to use this bot. "
            "This bot is currently in private mode and only authorized users can access it. "
            "Please contact the bot deployer for access privileges."
        )
        return
    
    chat_type = update.effective_chat.type
    user_id = update.effective_user.id
    is_admin = user_id in Config.ALLOWED_USER_IDS
    
    # Base message for all users
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
    
    # Add administrator commands if the user is an admin
    if is_admin:
        admin_message = (
            "\n\n🔑 Administrator Commands:\n"
            "/setpublic - Set the bot to public mode (anyone can use it)\n"
            "/setprivate - Set the bot to private mode (only authorized users can use it)\n"
            "/checkmode - Check the current access mode of the bot\n\n"
            f"Current mode: {'PUBLIC' if Config.PUBLIC_MODE else 'PRIVATE'}"
        )
        message += admin_message
    
    await update.message.reply_text(message)

async def new_quote(update: Update, context: CallbackContext) -> int:
    """Start the quotation creation process."""
    if not is_authorized(update):
        await update.message.reply_text(
            "Sorry, you are not authorized to use this bot. "
            "This bot is currently in private mode and only authorized users can access it. "
            "Please contact the bot deployer for access privileges."
        )
        return ConversationHandler.END
    
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    
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
                    "How would you like to provide the information?\n"
                    "1. Step-by-step (guided process)\n"
                    "2. All at once (AI-powered)"
                ),
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("Step-by-step 🧱", callback_data="mode_step"),
                        InlineKeyboardButton("All at once 🚀", callback_data="mode_ai")
                    ]
                ])
            )
            return CHOOSE_MODE
        except Exception as e:
            logger.error(f"Could not send private message to user {user_id}: {e}")
            await update.message.reply_text(
                "Error: I couldn't send you a private message. "
                "Please start a private chat with me first and then try again."
            )
            return ConversationHandler.END
    
    # For private chats, show mode selection directly
    await update.message.reply_text(
        "Let's create a new quotation! 📝\n\n"
        "How would you like to provide the information?\n"
        "1. Step-by-step (guided process)\n"
        "2. All at once (AI-powered)",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Step-by-step 🧱", callback_data="mode_step"),
                InlineKeyboardButton("All at once 🚀", callback_data="mode_ai")
            ]
        ])
    )
    return CHOOSE_MODE

async def cancel(update: Update, context: CallbackContext) -> int:
    """Cancel and end the conversation."""
    if not is_authorized(update):
        await update.message.reply_text(
            "Sorry, you are not authorized to use this bot. "
            "This bot is currently in private mode and only authorized users can access it. "
            "Please contact the bot deployer for access privileges."
        )
        return ConversationHandler.END
    
    user_id = update.effective_user.id
    if user_id in quotation_data:
        del quotation_data[user_id]
    
    await update.message.reply_text(
        "Quotation creation cancelled. All data has been cleared.\n"
        "Use /newquote to start again."
    )
    
    return ConversationHandler.END

async def handle_general_message(update: Update, context: CallbackContext) -> None:
    """Handle general messages and filter non-relevant queries using AI-like detection."""
    if not is_authorized(update):
        await update.message.reply_text(
            "Sorry, you are not authorized to use this bot. "
            "This bot is currently in private mode and only authorized users can access it. "
            "Please contact the bot deployer for access privileges."
        )
        return
    
    # Get the message text
    message_text = update.message.text.lower()
    
    # Define specific non-function queries that users might ask
    non_function_queries = {
        'weather': ['weather', 'forecast', 'temperature', 'rain', 'sunny', 'cloudy'],
        'news': ['news', 'latest news', 'current events', 'headlines', 'what\'s happening'],
        'general_chat': ['hello', 'hi', 'hey', 'how are you', 'who are you', 'what can you do', 'tell me a joke', 'joke'],
        'time': ['time', 'date', 'day', 'today', 'now'],
        'search': ['search', 'find', 'look up', 'google', 'internet'],
        'math': ['calculate', 'solve', 'math', 'equation', 'result', 'answer'],
        'translation': ['translate', 'language', 'mean in', 'what is', 'definition', 'define'],
        'other_bots': ['gpt', 'ai', 'alexa', 'siri', 'chatgpt', 'bard', 'claude', 'gemini']
    }
    
    # Check if the message is a common non-function query
    non_function_category = None
    for category, keywords in non_function_queries.items():
        if any(keyword in message_text for keyword in keywords):
            non_function_category = category
            break
    
    # Define categories of keywords related to the bot's function for better relevancy detection
    function_keywords = {
        'quotation_core': [
            'quote', 'quotation', 'invoice', 'offer', 'proposal', 'estimate', 
            'pricing', 'generate', 'create', 'make', 'new'
        ],
        'client_info': [
            'customer', 'client', 'buyer', 'company', 'business', 'contact',
            'address', 'email', 'phone', 'name'
        ],
        'item_details': [
            'item', 'product', 'service', 'goods', 'merchandise', 'quantity',
            'price', 'cost', 'amount', 'unit', 'total', 'subtotal'
        ],
        'terms': [
            'terms', 'condition', 'agreement', 'policy', 'discount', 'payment',
            'due date', 'validity', 'expiry', 'notes', 'issued', 'authorized'
        ],
        'document': [
            'pdf', 'document', 'file', 'format', 'template', 'download', 'send',
            'share', 'print', 'export', 'html'
        ],
        'process': [
            'step', 'guide', 'how to', 'instruction', 'tutorial', 'ai',
            'step-by-step', 'all at once', 'info', 'input', 'summary'
        ],
        'management': [
            'modify', 'change', 'edit', 'update', 'delete', 'remove', 'cancel',
            'revise', 'adjust', 'correct'
        ]
    }
    
    # Check relevancy based on category matches for more accurate detection
    matched_categories = []
    for category, keywords in function_keywords.items():
        if any(keyword in message_text for keyword in keywords):
            matched_categories.append(category)
    
    # Determine overall relevancy score
    relevancy_score = len(matched_categories)
    is_relevant = relevancy_score > 0
    
    # Advanced pattern detection for questions
    question_patterns = [
        '?', 'how', 'what', 'when', 'where', 'who', 'why', 'can', 'could',
        'would', 'should', 'do', 'does', 'is', 'are', 'will', 'explain'
    ]
    is_question = any(pattern in message_text for pattern in question_patterns)
    
    # Log the relevancy analysis
    logger.info(f"Message: '{message_text}' | Relevancy score: {relevancy_score} | Categories: {matched_categories} | Is question: {is_question} | Non-function category: {non_function_category}")
    
    # Handle specific non-function queries with targeted responses
    if non_function_category:
        if non_function_category == 'general_chat':
            if 'hello' in message_text or 'hi' in message_text or 'hey' in message_text:
                await update.message.reply_text(
                    "Hello! I'm the Quotation Bot. I can help you create professional quotations. "
                    "Type /newquote to start or /help for more information."
                )
                return
            elif 'how are you' in message_text:
                await update.message.reply_text(
                    "I'm just a bot focused on helping you create quotations. "
                    "I'm ready to assist with your quotation needs! Use /newquote to start."
                )
                return
            elif 'who are you' in message_text or 'what can you do' in message_text:
                await update.message.reply_text(
                    "I'm a specialized bot designed to help create professional quotations. "
                    "I can guide you step-by-step or use AI to extract information from your text. "
                    "Use /help to learn more about my capabilities."
                )
                return
            elif 'joke' in message_text:
                await update.message.reply_text(
                    "I'm focused on creating quotations, not jokes. But I can help you create "
                    "a professional quotation that's no laughing matter! Use /newquote to begin."
                )
                return
        else:
            # For other non-function categories
            await update.message.reply_text(
                "I'm a specialized quotation generation bot and cannot help with "
                f"{non_function_category} queries. I can only assist with creating and managing "
                "quotations. Use /newquote to create a quotation or /help for more information."
            )
            return
    
    # Handle irrelevant questions
    if is_question and not is_relevant:
        await update.message.reply_text(
            "I'm a specialized quotation bot and can only answer questions related to creating "
            "and managing quotations. For quotation-related help, try asking about how to create "
            "quotes, add items, or use the template. Use /help to see all available commands."
        )
        return
    
    # Handle irrelevant messages
    if not is_relevant:
        await update.message.reply_text(
            "I'm designed specifically for generating professional quotations. My capabilities are "
            "limited to this function. If you'd like to create a quotation, please use the /newquote "
            "command to get started, or /help to learn more about my features."
        )
        return
    
    # Handle relevant questions with specific responses based on the matched categories
    if is_question:
        if 'quotation_core' in matched_categories:
            await update.message.reply_text(
                "To create a new quotation, use the /newquote command. You'll have two options:\n\n"
                "1. Step-by-step: I'll guide you through entering each detail one at a time\n"
                "2. AI-powered: You can provide all information at once, and I'll extract the details"
            )
        elif 'client_info' in matched_categories:
            await update.message.reply_text(
                "For customer information, you'll need to provide details such as:\n"
                "• Customer name\n"
                "• Company name\n"
                "• Address\n"
                "• Phone number\n"
                "• Email\n\n"
                "These details will appear in the 'Quotation for' section of your document."
            )
        elif 'item_details' in matched_categories:
            await update.message.reply_text(
                "When adding items to your quotation, you'll need to specify:\n"
                "• Item name/description\n"
                "• Quantity\n"
                "• Unit price\n\n"
                "I'll calculate the total price automatically. You can add multiple items to a single quotation."
            )
        elif 'terms' in matched_categories:
            await update.message.reply_text(
                "Terms and conditions are important parts of your quotation. You can specify:\n"
                "• Payment terms\n"
                "• Validity period\n"
                "• Delivery conditions\n"
                "• Warranty information\n"
                "• Any other terms relevant to your business\n\n"
                "You can also add special notes and apply discounts if needed."
            )
        elif 'document' in matched_categories:
            await update.message.reply_text(
                "I generate quotations in HTML format that you can easily convert to PDF:\n"
                "1. The quotation is created with a professional template\n"
                "2. Open the HTML file in any browser\n"
                "3. Use the browser's 'Print' function\n"
                "4. Select 'Save as PDF' as the destination\n\n"
                "This gives you a professional PDF document to send to your clients."
            )
        else:
            # Generic response for other relevant queries
            await update.message.reply_text(
                "I can help with creating quotations, managing customer information, adding items, "
                "setting terms, and generating professional documents. To start, use the /newquote "
                "command, or type /help for more information about my capabilities."
            )
    else:
        # For relevant non-questions, provide action-oriented guidance
        await update.message.reply_text(
            "I'm ready to help you create a professional quotation! To start, use the /newquote command. "
            "You can choose between a step-by-step guided process or provide all information at once "
            "with AI assistance.\n\n"
            "Type /help for more information about my features and how to use them."
        )

async def set_public_mode(update: Update, context: CallbackContext) -> None:
    """Set the bot to public mode - anyone can use it."""
    user_id = update.effective_user.id
    
    # Only users in ALLOWED_USER_IDS can change the mode (regardless of current mode)
    if user_id not in Config.ALLOWED_USER_IDS:
        await update.message.reply_text(
            "Sorry, only authorized administrators can change the bot's access mode."
        )
        return
    
    # Change the mode
    Config.PUBLIC_MODE = True
    logger.info(f"Bot mode changed to PUBLIC by user {user_id}")
    
    await update.message.reply_text(
        "✅ Bot is now in PUBLIC mode. Anyone can use it to create quotations."
    )

async def set_private_mode(update: Update, context: CallbackContext) -> None:
    """Set the bot to private mode - only authorized users can use it."""
    user_id = update.effective_user.id
    
    # Only users in ALLOWED_USER_IDS can change the mode (regardless of current mode)
    if user_id not in Config.ALLOWED_USER_IDS:
        await update.message.reply_text(
            "Sorry, only authorized administrators can change the bot's access mode."
        )
        return
    
    # Change the mode
    Config.PUBLIC_MODE = False
    logger.info(f"Bot mode changed to PRIVATE by user {user_id}")
    
    await update.message.reply_text(
        "🔒 Bot is now in PRIVATE mode. Only authorized users can create quotations."
    )

async def check_mode(update: Update, context: CallbackContext) -> None:
    """Check the current access mode of the bot."""
    user_id = update.effective_user.id
    
    # Only users in ALLOWED_USER_IDS can check the mode
    if user_id not in Config.ALLOWED_USER_IDS:
        await update.message.reply_text(
            "Sorry, only authorized administrators can check the bot's access mode."
        )
        return
    
    mode = "PUBLIC" if Config.PUBLIC_MODE else "PRIVATE"
    await update.message.reply_text(
        f"The bot is currently in {mode} mode.\n\n"
        f"PUBLIC mode: Anyone can use the bot\n"
        f"PRIVATE mode: Only authorized users can use the bot"
    )

def main(application: Application = None) -> None:
    """Start the bot."""
    if application is None:
        application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Create a single conversation handler for both flows
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('newquote', new_quote)],
        states={
            # Mode selection state
            CHOOSE_MODE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_mode_choice),
                CallbackQueryHandler(handle_mode_choice, pattern="^mode_")
            ],
            
            # Step-by-step flow states
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
            DISCOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_discount)],
            
            # AI-powered flow states
            AI_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_input)],
            AI_CLARIFICATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_clarification)],
            AI_SUMMARY: [
                CallbackQueryHandler(handle_ai_summary, pattern="^confirm_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_additional_input)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    
    # Add mode control commands for administrators
    application.add_handler(CommandHandler('setpublic', set_public_mode))
    application.add_handler(CommandHandler('setprivate', set_private_mode))
    application.add_handler(CommandHandler('checkmode', check_mode))
    
    # Add general message handler (will only trigger if no other handlers match)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_general_message))
    
    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main() 