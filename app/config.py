from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Config:
    # Bot Configuration
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # Authorization
    ALLOWED_USER_IDS = [int(id.strip()) for id in os.getenv('ALLOWED_USER_IDS', '').split(',') if id.strip()]
    ALLOWED_GROUP_IDS = [int(id.strip()) for id in os.getenv('ALLOWED_GROUP_IDS', '').split(',') if id.strip()]
    
    # Company Information
    COMPANY_NAME = os.getenv('COMPANY_NAME')
    COMPANY_LOGO_URL = os.getenv('COMPANY_LOGO_URL')
    COMPANY_LOGO_WIDTH = int(os.getenv('COMPANY_LOGO_WIDTH', '80'))
    COMPANY_LOGO_HEIGHT = int(os.getenv('COMPANY_LOGO_HEIGHT', '80'))
    COMPANY_ADDRESS = os.getenv('COMPANY_ADDRESS')
    COMPANY_EMAIL = os.getenv('COMPANY_EMAIL')
    COMPANY_PHONE = os.getenv('COMPANY_PHONE')
    COMPANY_WEBSITE = os.getenv('COMPANY_WEBSITE', '')
    COMPANY_SUFFIX = os.getenv('COMPANY_SUFFIX', '')  # Optional, defaults to empty string
    
    # Quotation Settings
    QUOTATION_EXPIRY_DAYS = int(os.getenv('QUOTATION_EXPIRY_DAYS', '30'))
    
    # Storage settings
    SAVE_TO_STORAGE = os.getenv('SAVE_TO_STORAGE', 'False').lower() in ('true', '1', 't')
    STORAGE_PATH = os.getenv('STORAGE_PATH', 'quotes')
    
    @classmethod
    def get_company_info(cls):
        """Returns company information as a dictionary for template rendering"""
        return {
            'COMPANY_NAME': cls.COMPANY_NAME,
            'COMPANY_LOGO_URL': cls.COMPANY_LOGO_URL,
            'COMPANY_LOGO_WIDTH': cls.COMPANY_LOGO_WIDTH,
            'COMPANY_LOGO_HEIGHT': cls.COMPANY_LOGO_HEIGHT,
            'COMPANY_ADDRESS': cls.COMPANY_ADDRESS,
            'COMPANY_EMAIL': cls.COMPANY_EMAIL,
            'COMPANY_PHONE': cls.COMPANY_PHONE,
            'COMPANY_SUFFIX': cls.COMPANY_SUFFIX,
            'COMPANY_WEBSITE': cls.COMPANY_WEBSITE
        } 