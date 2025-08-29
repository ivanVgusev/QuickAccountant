# Quick Accountant 🤖💸

A multilingual Telegram bot that helps you track and manage your personal expenses with voice and text input support.

## 🌟 Features

- **Voice & Text Input**: Add expenses using both voice messages and text
- **Multilingual Support**: Currently supports English and Russian
- **Currency Conversion**: Automatically converts all expenses to USD for unified tracking
- **Expense Categorization**: AI-powered categorization of your purchases
- **Periodic Reports**: View expenses for any date range with calendar interface
- **Data Export**: Download your expense history as CSV files
- **Privacy-Focused**: All data stored locally - no third-party sharing

## 🛠️ Tech Stack

- **Backend**: Python 3.11+
- **Telegram Integration**: aiogram 3.x
- **Speech Recognition**: OpenAI Whisper
- **AI Processing**: Groq API (LLM)
- **Data Storage**: Pandas DataFrames with CSV backend
- **Currency Conversion**: Real-time exchange rates via external API

## 📋 Prerequisites

- Python 3.11 or higher
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- Groq API Key from [Groq Console](https://console.groq.com)
- FFmpeg (for audio processing)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ivanVgusev/QuickAccountant
   cd quick-accountant

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt

3. **Set up environment variables**

    Create a configuration.py file with:
   ```bash
    BOT_API = "your_telegram_bot_token"
    GROQ_API_KEY = "your_groq_api_key"
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    GROQ_MODEL = "llama-3.1-8b-instant" 
    GROQ_MODEL_BACKUP = "mixtral-8x7b-32768" # Backup used when the main model runs out of tokens 
    CHAT_ID_EASTER_EGG = 123456789  # Optional: for special user handling

## 🎯 Usage

<b>Available Commands:</b>

/start - Set up bot and choose language

/expenses - View expenses for a selected period

/delete - Delete one of the last 10 expense records

/csv - Download your expense history as CSV

/help - Get help and FAQ information

/reset - Delete ALL expense records (irreversible)

<b>Adding Expenses:</b>

Text: Send messages like "20 dollars for lunch" or "1000 рублей на кофе"

Voice: Send voice messages describing your expenses

<b>Example Interactions:</b>
   ```bash
   User: 15 euros for museum ticket
   Bot: ✅ Got it! 15 EUR: "museum ticket" registered. 📂 Category: Entertainment and Leisure.
   
   User: /expenses
   Bot: [Shows calendar to select date range]
   ```

## 📁 Project Structure
   ```bash
   quick-accountant/
   ├── bot.py                 # Main bot handler and command processors
   ├── ASR.py                # Audio speech recognition with Whisper
   ├── groq_client.py        # Groq API integration for expense extraction
   ├── db_handler.py         # Database operations and expense management
   ├── currency_convertor.py # Currency conversion utilities
   ├── multilingual_texts.py # All bot messages and prompts
   ├── configuration.py      # API keys and configuration (create this)
   ├── db_storage/          # User data storage directory
   └── requirements.txt     # Python dependencies
   ```   

## 🔧 Configuration

<b>Environment Setup:</b>
1. Get a Telegram Bot Token from @BotFather

2. Obtain a Groq API key from Groq Console

3. Install Whisper dependencies: pip install openai-whisper

4. Install FFmpeg for audio processing

<b>File Structure:</b>

User data is stored in db_storage/ as CSV files (one per user)

Language preferences are stored in db_user_language.csv

## 🌐 Supported Currencies

The bot supports all major currencies (USD, EUR, RUB, GBP, JPY, etc.) using standard 3-letter currency codes. 
All expenses are automatically converted to USD for unified reporting.

## 📊 Categories
📊 Categories
Expenses are automatically categorized into:

    Housing (rent, utilities, maintenance)
    
    Groceries and Household Items
    
    Transportation
    
    Children expenses
    
    Health and fitness
    
    Work and Education
    
    Entertainment and Leisure
    
    Clothing and Shoes
    
    Pets

## 🔒 Privacy & Data Security
All user data is stored locally in CSV format

No data is shared with third parties

Voice messages are processed locally with Whisper

Users can delete all their data with /reset command

Open source – transparent codebase

## 🐛 Troubleshooting
<b>Common Issues:</b>

Audio not processing: Ensure FFmpeg is installed

Groq API errors: Check your API key and quota

Currency conversion fails: Internet connection required for live rates

No response from bot: Check if the bot is running and API keys are valid

<b>Support:</b>

Contact @QuickAccountantBotSupport on Telegram for assistance.

## 📄 License
This project is open source and available under the MIT License.

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support
For questions and support:

Open an issue on GitHub

Contact @QuickAccountantBotSupport on Telegram



<b>✨💰Quick Accountant - Making personal finance tracking simple and accessible for everyone!💰✨</b>
