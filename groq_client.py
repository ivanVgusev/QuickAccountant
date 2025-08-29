import json
import logging

import httpx
import numpy as np

from configuration import GROQ_API_URL, GROQ_API_KEY, GROQ_MODEL, GROQ_MODEL_BACKUP
import multilingual_texts

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in .env")


def extract_json(text):
    start = text.find('{')
    if start == -1:
        return None

    stack = []
    for i in range(start, len(text)):
        char = text[i]
        if char == '{':
            stack.append('{')
        elif char == '}':
            stack.pop()
            if not stack:
                candidate = text[start:i + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    pass
    return None


async def expense_extractor(user_input: str, language):
    """
    Sends text to Groq and receives event structure.
    """

    prompt = multilingual_texts.expense_extractor_prompt.get(language).format(user_input=user_input)

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    body = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }

    # httpx for asynchronous requests
    max_retries = 10
    timeout = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        for retry in range(max_retries):
            response = await client.post(GROQ_API_URL, json=body, headers=headers)
            if response is not None and response != "":
                resp_json = response.json()

                # if the TPM (token per minute) exceeds the plan, it'll switch to another model
                if resp_json.get('error'):
                    body = {
                        "model": GROQ_MODEL_BACKUP,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2
                    }
                    logging.info(f'groq_client.expense_extractor:Switched to backup model {GROQ_MODEL_BACKUP}')
                    continue

                choices = resp_json.get('choices')
                if choices and len(choices) > 0:
                    message = choices[0].get('message')
                    if message:
                        content = message.get('content')
                        if content:
                            content = extract_json(content)

                            logging.info('groq_client.expense_extractor:JSON content extracted successfully')
                            return content

        logging.warning('groq_client.expense_extractor:JSON content NOT EXTRACTED')
        return np.nan


async def purchase_category(user_input: str, language):
    """
    Attributes a category to the purchase.
    """

    prompt = multilingual_texts.purchase_category_prompt.get(language).format(user_input=user_input)

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    body = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }

    # httpx for asynchronous requests
    max_retries = 10
    retries_amount = 0
    timeout = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        for retry in range(max_retries):
            response = await client.post(GROQ_API_URL, json=body, headers=headers)
            if response is not None and response != "":
                resp_json = response.json()

                # if the TPM (token per minute) exceeds the plan, it'll switch to another model
                if resp_json.get('error'):
                    body = {
                        "model": GROQ_MODEL_BACKUP,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2
                    }
                    logging.info(f'groq_client.purchase_category:Switched to backup model {GROQ_MODEL_BACKUP}')
                    continue

                choices = resp_json.get('choices')
                if choices and len(choices) > 0:
                    message = choices[0].get('message')
                    if message:
                        content = message.get('content')
                        if content:
                            content = content.strip()

                            logging.info('groq_client.purchase_category:JSON content extracted successfully')
                            return content
            retries_amount += 1

        logging.warning('groq_client.purchase_category:JSON content NOT EXTRACTED')
        return np.nan


async def main_query(user_input: str, user_lang):
    if user_input is None:
        return multilingual_texts.sorry.get(user_lang)

    expense = await expense_extractor(user_input, user_lang)

    if not isinstance(expense, dict):
        return multilingual_texts.sorry.get(user_lang)

    if expense.get('price') == 0:
        return multilingual_texts.sorry.get(user_lang)

    if (expense.get('description') == 0
            or expense.get('description') == '0'
            or expense.get('description') == ' '
            or expense.get('description') == ''

            or (expense.get('description') is None
                or (isinstance(expense.get('description'), float) and np.isnan(expense.get('description'))))):

        expense['description'] = 0
        expense['category'] = 0
    else:
        category = await purchase_category(expense.get('description'), user_lang)
        expense['category'] = category

    if (expense.get('category') == 0
            or expense.get('category') == '0'
            or expense.get('category') == ' '
            or expense.get('category') == ''
            or (expense.get('category') is None
                or (isinstance(expense.get('category'), float) and np.isnan(expense.get('category'))))):
        expense['category'] = 0

    return expense
