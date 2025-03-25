# Telegram Quotation Bot

A Telegram bot for generating professional quotations. This bot allows users to create customized quotations with customer details, item listings, terms, and notes.

## Features

- Create customized quotations with customer details
- Add multiple items with quantities and prices
- Include terms, conditions, and notes
- Generate HTML and PDF outputs
- Support for both private and group chat interactions
- User and group authorization

## Setup

### Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (from BotFather)

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
TELEGRAM_BOT_TOKEN=your_bot_token
ALLOWED_USER_IDS=comma_separated_user_ids
ALLOWED_GROUP_IDS=comma_separated_group_ids
```

### Running the Bot

```bash
python -m app.bot.quotation_bot
```

## Usage

### Private Chat Commands

- `/start` - Start the bot and see available commands
- `/help` - Get help information
- `/newquote` - Start creating a new quotation
- `/cancel` - Cancel the current operation

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
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   └── utils/
│       ├── __init__.py
│       ├── models.py
│       └── test_pdf.py
├── temp/         # Generated quotations
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```

## License

[Your License]

## Contribution

Contributions are welcome! Please feel free to submit a Pull Request.
