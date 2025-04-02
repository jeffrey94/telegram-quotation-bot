"""
Main entry point for the Telegram Quotation Bot application.
"""

import logging
from app.bot import create_application
# Import file cleanup manager
from app.utils.file_cleanup import cleanup_manager

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def main():
    """Run the bot."""
    logger.info("Starting Telegram Quotation Bot")
    
    # Initialize cleanup manager (will run automatically when files are added)
    logger.info("Initializing file cleanup manager (10 minute expiry)")
    
    # Create and configure the application
    application = create_application()
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling()
    
    # Stop the cleanup manager when bot stops
    cleanup_manager.stop_cleanup_task()
    
    logger.info("Bot stopped")


if __name__ == "__main__":
    main()
