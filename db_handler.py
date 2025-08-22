from datetime import datetime
from pathlib import Path
import numpy as np
import random
from currency_convertor import to_dollars
import pandas as pd
import multilingual_texts


async def add_user_language(chat_id: int, user_language: str):
    db_user_language_path = Path("db_user_language.csv")
    if not db_user_language_path.exists():
        db_user_language = pd.DataFrame({
            "chat_id": [int(chat_id)],
            "language": [user_language]
        }).set_index("chat_id")

    else:
        db_user_language = pd.read_csv(db_user_language_path, index_col='chat_id')

        # handling situation where user calls /start again to change the language
        if chat_id in db_user_language.index and db_user_language.loc[chat_id, 'language'] != user_language:
            db_user_language.loc[chat_id, 'language'] = user_language

        if chat_id not in db_user_language.index:
            entry = pd.DataFrame({
                "chat_id": [int(chat_id)],
                "language": [user_language]
            }).set_index("chat_id")
            db_user_language = pd.concat([db_user_language, entry])

    db_user_language.to_csv(db_user_language_path, index=True)


async def get_user_language(chat_id):
    db_user_language_path = Path("db_user_language.csv")
    db_user_language = pd.read_csv(db_user_language_path, index_col='chat_id')
    return db_user_language.loc[chat_id, 'language']


async def add_entry(data, chat_id, user_lang):
    # converting original enty into USD
    USD = await to_dollars(data.get('price'), data.get('currency'))

    current_time = datetime.now()

    if (not data.get('description')
            or data.get('description') == 0
            or data.get('description') == '0'
            or data.get('description') == ' '
            or data.get('description') == ''
            or data.get('description') is None
            or (isinstance(data.get('description'), float) and np.isnan(data.get('description')))):
        data['description'] = 0
        data['category'] = 0

    # int price -> float price
    data['price'] = float(data.get('price'))

    entry = pd.DataFrame(index=[current_time], data=data)
    entry.index.name = 'timestamp'
    entry['USD'] = [USD]

    csv_path = Path(f'db_storage/{chat_id}.csv')
    if csv_path.exists():
        user_db = pd.read_csv(csv_path, index_col='timestamp')
        user_db = pd.concat([user_db, entry])
        user_db.to_csv(csv_path)
    else:
        entry.to_csv(csv_path)

    # If statement for handling situations where user does not leave description for his expense.
    price = data.get("price")
    currency = data.get("currency")
    description = data.get("description")
    category = data.get("category")

    if data.get('description') == 0:
        confirmation_message = random.choice(multilingual_texts.db_confirmation_message_no_description.get(user_lang))
        confirmation_message = (confirmation_message.format(price=price, currency=currency, description=description,
                                                            category=category))
    elif data.get('description') != 0 and data.get('category') == 0:
        confirmation_message = random.choice(multilingual_texts.
                                             db_confirmation_message_description_no_category.get(user_lang))
        confirmation_message = (confirmation_message.format(price=price, currency=currency, description=description,
                                                            category=category))
    else:
        confirmation_message = random.choice(multilingual_texts.db_confirmation_message_description.get(user_lang))
        confirmation_message = (confirmation_message.format(price=price, currency=currency, description=description,
                                                            category=category))
    return confirmation_message


async def last_10_entries(chat_id) -> list[dict] | str:
    user_lang = await get_user_language(chat_id)

    csv_path = Path(f'db_storage/{chat_id}.csv')
    if csv_path.exists():
        user_db = pd.read_csv(csv_path, parse_dates=['timestamp'])
        if len(user_db) == 0:
            return multilingual_texts.db_last_10_entries_message.get(user_lang)
    else:
        return multilingual_texts.db_last_10_entries_message.get(user_lang)

    last_10 = user_db.tail(10).to_dict(orient='records')

    return last_10


async def delete_entry(chat_id, index_timestamp):
    user_lang = await get_user_language(chat_id)

    csv_path = Path(f'db_storage/{chat_id}.csv')
    user_db = pd.read_csv(csv_path, index_col='timestamp', parse_dates=['timestamp'])
    user_db_delete_entry = user_db.drop(index_timestamp)
    user_db_delete_entry.to_csv(csv_path)

    index_timestamp = index_timestamp.strftime("%d %B %Y %H:%M")
    confirmation_message = multilingual_texts.db_delete_entry_message.get(user_lang)
    confirmation_message = confirmation_message.format(index_timestamp=index_timestamp)
    return confirmation_message


async def show_expenses(chat_id, start_date, end_date):
    user_lang = await get_user_language(chat_id)

    csv_path = Path(f'db_storage/{chat_id}.csv')
    if csv_path.exists():
        user_db = pd.read_csv(csv_path, index_col='timestamp', parse_dates=['timestamp'])
        expenses = user_db.loc[start_date:end_date]

        # no expenses over the chosen period of time
        if len(expenses) == 0:
            return multilingual_texts.sorry_no_entries.get(user_lang)

        date_expenses = expenses.index
        description_expenses = expenses.values

        response = ''
        current_date_iter = None
        for date, description in zip(date_expenses, description_expenses):
            if current_date_iter != date.strftime('%d %b %Y'):
                current_date_iter = date.strftime('%d %b %Y')
                response += f'🗓{current_date_iter}\n'

            # if user provided a description
            if (description[2] != 0
                    and description[2] != '0'
                    and description[2] != ' '
                    and description[2] != ''
                    and (description[2] is not None
                         or (isinstance(description[2], float) and not np.isnan(description[2])))):

                outp_string = f'{date.strftime("%H:%M")} – {description[0]}\t{description[1]}\t({description[2]})'
                response += outp_string + '\n\n'
            else:
                outp_string = f'{date.strftime("%H:%M")} – {description[0]}\t{description[1]}'
                response += outp_string + '\n\n'

        # adding total
        expenses_by_currency = expenses['price'].groupby(expenses['currency']).sum()
        expenses_USD = round(expenses['USD'].sum(), 2)
        expenses_string = ""

        for currency, amount in expenses_by_currency.items():
            expenses_string += f"{amount:.2f} {currency}, "
        expenses_string = expenses_string[:-2] + ' '

        total = multilingual_texts.db_show_expenses_message.get(user_lang)
        total = total.format(expenses_string=expenses_string, expenses_USD=expenses_USD)
        response += total

        if len(response) != 0:
            return response
        else:
            return multilingual_texts.sorry.get(user_lang)
    else:
        return multilingual_texts.sorry.get(user_lang)


async def categories(chat_id, start_date, end_date):
    user_lang = await get_user_language(chat_id)

    csv_path = Path(f'db_storage/{chat_id}.csv')
    if csv_path.exists():
        user_db = pd.read_csv(csv_path, index_col='timestamp', parse_dates=['timestamp'])
        expenses = user_db.loc[start_date:end_date]

        # no expenses over the chosen period of time
        if len(expenses) == 0:
            return multilingual_texts.sorry_no_entries.get(user_lang)

        expenses = expenses['USD'].groupby(expenses['category']).sum()
        expenses = expenses.rename(index={"0": multilingual_texts.unknown_category.get(user_lang)})
        expenses_percent = expenses / expenses.sum() * 100

        expenses_str = ''
        category_expenses = expenses_percent.index
        percentage_expenses = expenses_percent.values

        for category, percentage in zip(category_expenses, percentage_expenses):
            expenses_str += f"{category} – {round(percentage, 1)}%\n"
        return expenses_str

    else:
        return multilingual_texts.sorry


async def reset_account(chat_id):
    user_lang = await get_user_language(chat_id)

    csv_path = Path(f'db_storage/{chat_id}.csv')
    if csv_path.exists():
        csv_path.unlink()
        return multilingual_texts.reset_account_deleted_successfully.get(user_lang)
    else:
        return multilingual_texts.reset_account_deleted_unsuccessfully.get(user_lang)
