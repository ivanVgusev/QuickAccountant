import os
from dotenv import load_dotenv

load_dotenv()

# telegram
BOT_API = os.getenv('BOT_API')
BOT_API_TEST = os.getenv('BOT_API_TEST')
USER_TOKEN_STORAGE_PATH = "token_storage/"

# groq
GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_MODEL = os.getenv('GROQ_MODEL')
GROQ_MODEL_BACKUP = os.getenv('GROQ_MODEL_BACKUP')

CHAT_ID_EASTER_EGG = int(os.getenv('CHAT_ID_EASTER_EGG'))
