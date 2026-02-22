# Quick Accountant

A multilingual Telegram bot for tracking and managing personal expenses using text and voice input.

## Features

- **Voice & Text Input** – add expenses via text messages or voice notes  
- **Multilingual Support** – English and Russian  
- **Currency Conversion** – all expenses are converted to USD for unified tracking  
- **Expense Categorization** – AI-based categorization of purchases  
- **Periodic Reports** – view expenses for any date range using a calendar  
- **Data Export** – download expense history as CSV  
- **Privacy-Focused** – all data is stored locally, no third-party sharing  

## Tech Stack

- **Backend**: Python 3.11+  
- **Telegram Framework**: aiogram 3.x  
- **Speech Recognition**: OpenAI Whisper  
- **LLM Processing**: LLM API (e.g. Yandex GPT)  
- **Data Storage**: CSV files via Pandas  
- **Currency Conversion**: live exchange rates via external API  

## Prerequisites

- Python 3.11 or higher  
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)  
- LLM API key (e.g. Yandex GPT from Yandex Cloud)  
- FFmpeg (required for audio processing)  

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/ivanVgusev/QuickAccountant
cd quick-accountant
```

Install dependencies

```bash
Copy code
pip install -r requirements.txt
```

2. **Create configuration file**

```python
BOT_API = "your_telegram_bot_token"
YGPT_API = "Api-Key your_yandex_gpt_key"
YGPT_CATALOGUE_ID = "your_folder_id"
YGPT_MODEL_LITE = "yandexgpt-lite/latest"
YGPT_MODEL_PRO = "yandexgpt/latest"
```

## Usage
Available Commands
/start – initialize the bot and choose language

/expenses – view expenses for a selected period

/delete – delete one of the last 10 expense records

/csv – download expense history as CSV

/help – show help and FAQ

/reset – delete all expense records (irreversible)

## Adding Expenses

Text input

```python
20 dollars for lunch
1000 рублей на кофе
Voice input
Send a voice message describing the expense.
```


## Project Structure
```bash
Copy code
quick-accountant/
├── bot.py                  # Main bot logic
├── ASR.py                  # Speech recognition (Whisper)
├── llm_client.py           # LLM API integration (Yandex GPT)
├── db_handler.py           # Expense storage and management
├── currency_convertor.py  # Currency conversion utilities
├── multilingual_texts.py  # All texts and prompts
├── configuration.py       # Configuration file (user-created)
├── db_storage/             # User CSV data
└── requirements.txt
```

Supported Currencies
Supports all major currencies using standard 3-letter codes (USD, EUR, RUB, GBP, JPY, etc.).
All expenses are automatically converted to USD for reporting.

## Expense Categories
Housing

Groceries and Household Items

Transportation

Children Expenses

Health and Fitness

Work and Education

Entertainment and Leisure

Clothing and Shoes

Pets

## Privacy & Data Security
All user data is stored locally in CSV format

No data is shared with third parties

Voice messages are processed locally with Whisper

Users can delete all data using /reset

Open-source and transparent

## Troubleshooting
Audio not processed
Ensure FFmpeg is installed and available in PATH.

## LLM API errors
Check API key and quota limits.

## Currency conversion fails
Requires an active internet connection.

## Bot not responding
Verify that the bot is running and API keys are valid.

## License
MIT License.

## Contributing
Pull requests are welcome.

## Support
Open an issue on GitHub

Telegram: @QuickAccountantBotSupport