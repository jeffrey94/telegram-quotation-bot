"""
Main entry point for the Telegram Quotation Bot application.
"""

import logging
from app.bot import create_application

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def main():
    """Run the bot."""
    logger.info("Starting Telegram Quotation Bot")
    
    # Create and configure the application
    application = create_application()
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling()
    
    logger.info("Bot stopped")


if __name__ == "__main__":
    main()
