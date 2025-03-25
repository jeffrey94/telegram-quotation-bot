"""
Configuration settings for the application.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from typing import List

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in .env file")

# Allowed User IDs for authentication
allowed_users_str = os.getenv('ALLOWED_USER_IDS', '')
ALLOWED_USER_IDS = []
if allowed_users_str:
    try:
        ALLOWED_USER_IDS = [int(user_id.strip()) for user_id in allowed_users_str.split(',')]
    except ValueError:
        logger.error("Invalid user IDs in ALLOWED_USER_IDS. Expected comma-separated integers.")
        raise ValueError("Invalid user IDs in ALLOWED_USER_IDS. Expected comma-separated integers.")

# Allowed Group IDs for authentication
allowed_groups_str = os.getenv('ALLOWED_GROUP_IDS', '')
ALLOWED_GROUP_IDS = []
if allowed_groups_str:
    try:
        ALLOWED_GROUP_IDS = [int(group_id.strip()) for group_id in allowed_groups_str.split(',')]
    except ValueError:
        logger.error("Invalid group IDs in ALLOWED_GROUP_IDS. Expected comma-separated integers.")
        raise ValueError("Invalid group IDs in ALLOWED_GROUP_IDS. Expected comma-separated integers.")

# Company Details
COMPANY_NAME = "SOHO STUDIO SDN. BHD."
COMPANY_REG_NO = "201301009441 (1039283-W)"
COMPANY_ADDRESS = "No. 46, Jalan Seri Orkid 1, Taman Seri Orkid, 81300 Skudai, Johor Bahru, Johor, Malaysia."
COMPANY_PHONE = "07-511 5001"
COMPANY_FAX = "07-511 6002"
COMPANY_EMAIL = "admin@sohostudio.my"

# Factory Details
FACTORY_ADDRESS = "No. 3, Jalan Ekoperniagaan 1/25, Taman Ekoperniagaan, 81100 Johor Bahru, Johor, Malaysia."
FACTORY_PHONE = "07-595 3900"
FACTORY_FAX = "07-595 3970"

# Currency
CURRENCY_SYMBOL = "RM"

# Template paths
TEMPLATES_DIR = BASE_DIR / "app" / "templates"
QUOTATION_TEMPLATE = TEMPLATES_DIR / "quotation_template.html"

# Output paths
TEMP_DIR = BASE_DIR / "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# Date and currency formatting
DATE_FORMAT = "%Y-%m-%d"

# Optional storage settings
SAVE_TO_STORAGE = os.getenv("SAVE_TO_STORAGE", "False").lower() == "true"
STORAGE_PATH = os.getenv("STORAGE_PATH", str(BASE_DIR / "quotes"))
