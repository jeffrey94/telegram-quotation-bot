# Telegram Quotation Bot

A Telegram bot for generating professional quotations. This bot allows users to create customized quotations with customer details, item listings, terms, and notes.

## Features

- Create customized quotations with customer details
- Add multiple items with quantities and prices
- Include terms, conditions, and notes
- Generate HTML and PDF outputs
- Support for both private and group chat interactions
- User and group authorization
- Public/private mode toggle (restrict to authorized users or allow anyone)
- AI-powered quotation generation from natural language input
- Intelligent message filtering for function-relevant queries
- Consistent font styling in quotation templates

## Setup

### Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (from BotFather)
- OpenAI API Key (for AI-powered quotation extraction)

### Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd telegram-quotation-bot
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```
# Telegram Bot settings
TELEGRAM_BOT_TOKEN=your_bot_token
ALLOWED_USER_IDS=comma_separated_user_ids
ALLOWED_GROUP_IDS=comma_separated_group_ids

# Access Control
PUBLIC_MODE=False  # Set to True to allow anyone to use the bot

# Company details
COMPANY_NAME=Your Company
COMPANY_LOGO_URL=https://your-company-logo-url.com/logo.png
COMPANY_ADDRESS=Your Company Address
COMPANY_PHONE=Your Company Phone
COMPANY_EMAIL=your.company@email.com
COMPANY_WEBSITE=www.yourcompany.com

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
```

### Running the Bot

```bash
python run_bot.py
```

## Usage

### Private Chat Commands

- `/start` - Start the bot and see available commands
- `/help` - Get help information
- `/newquote` - Start creating a new quotation
- `/cancel` - Cancel the current operation

### Admin Commands

- `/setpublic` - Set the bot to public mode (anyone can use it)
- `/setprivate` - Set the bot to private mode (only authorized users)
- `/checkmode` - Check the current access mode of the bot

### Quotation Creation Methods

The bot offers two methods for creating quotations:

1. **Step-by-step**: A guided process where the bot asks for each detail one at a time
2. **AI-powered**: You can provide all information at once in natural language, and the AI will extract the details

### Group Chat

The bot can also be used in authorized group chats:

1. Add the bot to a Telegram group
2. Make sure the group ID is added to `ALLOWED_GROUP_IDS` in the `.env` file
3. Use `/newquote` to initiate a quotation
4. The bot will send you a private message to collect details
5. After completion, the quotation will be sent to you privately

## Project Structure

```
telegram-quotation-bot/
├── app/
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── constants.py
│   │   ├── handlers.py
│   │   └── quotation_bot.py
│   ├── config.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── test_pdf.py
│   │   └── gpt_quotation.py
│   └── templates/
│       └── quotation_template.html
├── temp/         # Generated quotations
├── run_bot.py
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```

## Recent Changes

### v1.1.0
- Added public/private mode toggle with admin commands
- Implemented AI-powered quotation generation from natural language input
- Enhanced message handling with intelligent filtering for function-relevant queries
- Improved font consistency in quotation templates
- Added ability to provide additional information during AI summary phase
- Fixed quotation generation issues with proper parameter handling

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contribution

Contributions are welcome! Please feel free to submit a Pull Request.
