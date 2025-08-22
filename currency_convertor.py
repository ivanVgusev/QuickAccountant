import json
import httpx
import logging
import numpy as np
import asyncio
from aiogram.enums import ChatAction


async def to_dollars(amount: float, original_currency: str) -> float:
    """
    This func converts currencies to USD.

    :param amount: float value, amount converted to USD
    :param original_currency: input currency later transformed to USD
    :return: value in USD
    """
    url = F'https://hexarate.paikama.co/api/rates/latest/{original_currency}?target=USD'
    try:
        async with httpx.AsyncClient() as client:
            currency_rate = await client.get(url)
            currency_rate.raise_for_status()

    except httpx.RequestError as e:
        logging.error(f"HTTP request failed: {e}")
        return np.nan
    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error response: {e.response.status_code} - {e.response.text}")
        return np.nan

    try:
        currency_rate = json.loads(currency_rate.text)
        currency_rate = currency_rate.get('data').get('mid')

        USD = float(amount * currency_rate)
        # rounded to two decimals
        USD = round(USD, 2)
        return USD

    except Exception as e:
        logging.error(e)
        return np.nan
