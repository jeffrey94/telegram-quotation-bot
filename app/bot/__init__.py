"""
Telegram bot package for quotation generation.
"""

from telegram.ext import Application
from app.config import Config
from .quotation_bot import main

def create_application() -> Application:
    """Create and configure the bot application."""
    # Create the application
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Add handlers from quotation_bot
    main(application)
    
    return application 