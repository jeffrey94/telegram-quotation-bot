"""
Constants for the Telegram quotation bot.
"""

# Conversation states
CUSTOMER_NAME = 0
CUSTOMER_COMPANY = 1
CUSTOMER_ADDRESS = 2
CUSTOMER_PHONE = 3
CUSTOMER_EMAIL = 4
ITEM_NAME = 5
ITEM_QUANTITY = 6
ITEM_PRICE = 7
ADD_ITEMS = 8
TERMS = 9
NOTES = 10
ISSUED_BY = 11
DISCOUNT = 12

# AI-powered flow states
CHOOSE_MODE = 13  # Choose between step-by-step or AI-powered mode
AI_INPUT = 14     # Get freeform input from user
AI_CLARIFICATION = 15  # Ask for clarification on missing/unclear data
AI_SUMMARY = 16   # Show summary and get confirmation

# Global dictionary to store quotation data for each user
# Structure: {user_id: {customer_name, customer_company, items: [], ...}}
quotation_data = {} 