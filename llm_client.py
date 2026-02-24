import json
import logging
import httpx
import numpy as np


from configuration import (
    YGPT_CATALOGUE_ID,
    YGPT_MODEL_LITE,
    YGPT_MODEL_PRO,
    YGPT_API,
    YGPT_LLM_URL,
)
import multilingual_texts

if not YGPT_API or not YGPT_CATALOGUE_ID:
    raise ValueError("YGPT_API and YGPT_CATALOGUE_ID must be set in .env")


async def llm_request(
    prompt_text: str,
    temperature: float = 0.6,
    llm_model: str = "lite",
) -> str | None:
    """
    Async request to Yandex GPT. Returns response text or None on failure.
    """
    if llm_model == "lite":
        model = YGPT_MODEL_LITE
    elif llm_model == "pro":
        model = YGPT_MODEL_PRO
    else:
        logging.warning("llm_client.llm_request: llm_model should be 'lite' or 'pro', using lite")
        model = YGPT_MODEL_LITE

    if not model:
        model = YGPT_MODEL_LITE

    payload = {
        "modelUri": f"gpt://{YGPT_CATALOGUE_ID}/{model}",
        "completionOptions": {
            "stream": False,
            "temperature": temperature,
            "maxTokens": "2000",
        },
        "messages": [
            {
                "role": "user",
                "text": prompt_text,
            }
        ],
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": YGPT_API,
    }

    timeout = httpx.Timeout(connect=30.0, read=60.0, write=10.0, pool=5.0)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(YGPT_LLM_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            text = data["result"]["alternatives"][0]["message"]["text"]
            return text.strip() if text else None
    except httpx.TimeoutException as e:
        logging.error(f"llm_client.llm_request: timeout {e}")
        return None
    except httpx.ConnectError as e:
        logging.error(f"llm_client.llm_request: connection error {e}")
        return None
    except httpx.HTTPStatusError as e:
        logging.error(f"llm_client.llm_request: HTTP {e.response.status_code} {e.response.text}")
        return None
    except (KeyError, IndexError, TypeError) as e:
        logging.error(f"llm_client.llm_request: parse error {e}")
        return None
    except Exception as e:
        logging.error(f"llm_client.llm_request: unexpected error {e}")
        return None


async def extract_json(text: str):
    if not text:
        return None
    start = text.find("{")
    if start == -1:
        return None
    stack = []
    for i in range(start, len(text)):
        char = text[i]
        if char == "{":
            stack.append("{")
        elif char == "}":
            stack.pop()
            if not stack:
                candidate = text[start : i + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    pass
    return None


async def expense_extractor(user_input: str, language: str):
    """
    Sends text to Yandex GPT and returns expense structure (dict or np.nan).
    """
    prompt = multilingual_texts.expense_extractor_prompt.get(language).format(
        user_input=user_input
    )
    text = await llm_request(prompt, temperature=0.2, llm_model="lite")
    if not text:
        logging.warning("llm_client.expense_extractor: no response from LLM")
        return np.nan
    content = await extract_json(text)
    if content is not None:
        logging.info("llm_client.expense_extractor: JSON extracted successfully")
        return content
    logging.warning("llm_client.expense_extractor: JSON not extracted")
    return np.nan


# Exact category names as in prompts (for extraction from model output)
VALID_CATEGORIES_EN = [
    "Housing",
    "Groceries and Household Items",
    "Transportation",
    "Children",
    "Health",
    "Work and Education",
    "Entertainment and Leisure",
    "Clothing and Shoes",
    "Pets",
]
VALID_CATEGORIES_RU = [
    "Жильё",
    "Продукты и хозяйственные товары",
    "Транспорт",
    "Дети",
    "Здоровье",
    "Работа и образование",
    "Развлечения и отдых",
    "Одежда и обувь",
    "Домашние животные",
]


def extract_category_from_response(text: str, language: str) -> str | None:
    """Take only the first valid category name from LLM response (avoids quiz-style output)."""
    if not text or not text.strip():
        return None
    categories = VALID_CATEGORIES_RU if language == "ru" else VALID_CATEGORIES_EN
    # Prefer exact match in first line
    first_line = text.strip().split("\n")[0].strip()
    if first_line in categories or first_line == "0":
        return first_line
    # Else find first category mentioned anywhere in the response
    for cat in categories:
        if cat in text:
            return cat
    if "0" in first_line or first_line.lower() in ("0", "ноль", "zero"):
        return "0"
    return None


def normalize_category_for_display(category: str, language: str) -> str:
    """
    Normalize a category string for grouping/display (e.g. strip LLM quiz junk from old DB values).
    Returns a valid category name or "0" for unknown.
    """
    if category is None or (isinstance(category, float) and np.isnan(category)):
        return "0"
    s = str(category).strip()
    if not s:
        return "0"
    categories = VALID_CATEGORIES_RU if language == "ru" else VALID_CATEGORIES_EN
    if s in categories or s == "0":
        return s
    extracted = extract_category_from_response(s, language)
    return extracted if extracted is not None else "0"


async def purchase_category(user_input: str, language: str):
    """
    Attributes a category to the purchase. Returns category string or np.nan.
    """
    prompt = multilingual_texts.purchase_category_prompt.get(language).format(
        user_input=user_input
    )
    text = await llm_request(prompt, temperature=0.2, llm_model="lite")
    if not text:
        logging.warning("llm_client.purchase_category: category not extracted")
        return np.nan
    extracted = extract_category_from_response(text, language)
    if extracted is not None:
        logging.info("llm_client.purchase_category: category extracted successfully")
        return extracted
    logging.warning("llm_client.purchase_category: category not extracted, response was truncated or invalid")
    return np.nan


async def main_query(user_input: str, user_lang: str):
    if user_input is None or (
        isinstance(user_input, float) and np.isnan(user_input)
    ):
        return multilingual_texts.sorry.get(user_lang)

    expense = await expense_extractor(user_input, user_lang)

    if not isinstance(expense, dict):
        return multilingual_texts.sorry.get(user_lang)

    if expense.get("price") == 0:
        return multilingual_texts.sorry.get(user_lang)

    if (
        expense.get("description") == 0
        or expense.get("description") == "0"
        or expense.get("description") == " "
        or expense.get("description") == ""
        or (
            expense.get("description") is None
            or (
                isinstance(expense.get("description"), float)
                and np.isnan(expense.get("description"))
            )
        )
    ):
        expense["description"] = 0
        expense["category"] = 0
    else:
        category = await purchase_category(expense.get("description"), user_lang)
        expense["category"] = category

    if (
        expense.get("category") == 0
        or expense.get("category") == "0"
        or expense.get("category") == " "
        or expense.get("category") == ""
        or (
            expense.get("category") is None
            or (
                isinstance(expense.get("category"), float)
                and np.isnan(expense.get("category"))
            )
        )
    ):
        expense["category"] = 0

    return expense

