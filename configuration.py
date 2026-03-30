import os
from dotenv import load_dotenv

load_dotenv()

CHAT_ID_EASTER_EGG = int(os.getenv('CHAT_ID_EASTER_EGG'))
HUGGING_FACE_TOKEN = os.getenv('HUGGING_FACE_TOKEN')

# telegram
BOT_API = os.getenv('BOT_API')
BOT_API_TEST = os.getenv('BOT_API_TEST')
USER_TOKEN_STORAGE_PATH = "token_storage/"

# Yandex GPT
YGPT_CATALOGUE_ID = os.getenv('YGPT_CATALOGUE_ID')
YGPT_MODEL_LITE = os.getenv('YGPT_MODEL_LITE')
YGPT_MODEL_PRO = os.getenv('YGPT_MODEL_PRO')
YGPT_API = os.getenv('YGPT_API')
YGPT_LLM_URL = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'

# ASR
ASR_MODEL = "small"
CPU_THREADS = 4

# PROXY
HTTP_PROXY = os.getenv("HTTP_PROXY")
