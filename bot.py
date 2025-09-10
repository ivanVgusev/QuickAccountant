# aiogram imports
from aiogram import Dispatcher, Bot, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, BotCommand,
                           ReactionTypeEmoji)
from aiogram.enums import ChatAction
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

# external imports
import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime
import random

# internal imports
import configuration
import multilingual_texts
from groq_client import main_query, ASR_upscale
import db_handler
from ASR import transcript

BOT_TOKEN = configuration.BOT_API
BOT_TOKEN_TEST = configuration.BOT_API_TEST

dp = Dispatcher()
# main use
tbot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
# # test use
# tbot = Bot(token=BOT_TOKEN_TEST, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

expenses_calendar = SimpleCalendar()


class PeriodSelection(StatesGroup):
    start_date = State()
    end_date = State()


db_storage_path = Path("db_storage")
if not db_storage_path.exists():
    Path.mkdir(db_storage_path)

language_choice = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
    ]
])


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="set up bot/change language"),
        BotCommand(command="expenses", description="view expenses"),
        BotCommand(command="delete", description="delete an expense record"),
        BotCommand(command="csv", description="download .csv"),
        BotCommand(command="help", description="help/FAQ"),
        BotCommand(command="reset", description="delete ALL expense records from the database"),
    ]
    await bot.set_my_commands(commands)


@dp.message(Command('start'))
async def start_info(message: Message) -> None:
    user_first_name = message.from_user.first_name

    await message.answer(
        f"👋 Hi, {user_first_name}!\n"
        "I’m <b>Quick Accountant</b> — your personal budgeting assistant💸\n"
        "🌐 Please choose your language to continue:",
        reply_markup=language_choice
    )


@dp.message(Command('help'))
async def start_info(message: Message) -> None:
    user_chat_id = message.chat.id
    user_lang = await db_handler.get_user_language(user_chat_id)

    await message.answer(multilingual_texts.help_message.get(user_lang))


@dp.callback_query(F.data.startswith("lang_"))
async def process_callback_lang_choice(callback_query: CallbackQuery) -> None:
    user_chat_id = callback_query.message.chat.id

    lang_code = callback_query.data.split("_")[1]

    await db_handler.add_user_language(user_chat_id, lang_code)
    await callback_query.message.answer(multilingual_texts.start_intro.get(lang_code))


@dp.message(Command('expenses'))
async def show_expenses(message: Message, state: FSMContext) -> None:
    user_chat_id = message.chat.id
    user_lang = await db_handler.get_user_language(user_chat_id)

    await message.answer(
        multilingual_texts.calendar_start_message.get(user_lang),
        reply_markup=await expenses_calendar.start_calendar()
    )
    await state.set_state(PeriodSelection.start_date)


@dp.callback_query(SimpleCalendarCallback.filter(), PeriodSelection.start_date)
async def callback_calendar_show_expenses_start(callback_query: CallbackQuery,
                                                callback_data: SimpleCalendarCallback,
                                                state: FSMContext):
    user_chat_id = callback_query.message.chat.id
    user_lang = await db_handler.get_user_language(user_chat_id)

    # "Today" button handling; if chosen, it skips the end date callback query
    if callback_data.act == "TODAY":
        await callback_query.message.delete()

        start_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = datetime.today().replace(hour=23, minute=59, second=59, microsecond=0)

        response = await db_handler.show_expenses(user_chat_id, start_date, end_date)

        callback_data_keyboard = (
            f"categories_start_{start_date.strftime('%Y-%m-%d')}_end_{end_date.strftime('%Y-%m-%d')}"
        )
        await state.clear()

        # if the response was a sorry message, it doesn't add the button to it
        if response == multilingual_texts.sorry.get(user_lang):
            await callback_query.message.answer(response)
        else:
            categories_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=multilingual_texts.show_categories.get(user_lang),
                        callback_data=callback_data_keyboard
                    )
                ]
            ])
            await callback_query.message.answer(response, reply_markup=categories_keyboard)

    # "Cancel" button handling
    elif callback_data.act == "CANCEL":
        await callback_query.message.delete()

    # Normal flow
    else:
        selected, start_user_date = await expenses_calendar.process_selection(callback_query, callback_data)
        if selected:
            await callback_query.message.delete()
            await state.update_data(start_date=start_user_date)
            await callback_query.message.answer(
                multilingual_texts.calendar_end_message.get(user_lang),
                reply_markup=await expenses_calendar.start_calendar()
            )
            await state.set_state(PeriodSelection.end_date)


@dp.callback_query(SimpleCalendarCallback.filter(), PeriodSelection.end_date)
async def callback_calendar_show_expenses_end(callback_query: CallbackQuery,
                                              callback_data: SimpleCalendarCallback,
                                              state: FSMContext):
    user_chat_id = callback_query.message.chat.id
    user_lang = await db_handler.get_user_language(user_chat_id)

    # "Today" button handling
    if callback_data.act == "TODAY":
        await callback_query.message.delete()

        data = await state.get_data()
        start_date = data.get("start_date")
        end_date = datetime.today().replace(hour=23, minute=59, second=59, microsecond=0)

        response = await db_handler.show_expenses(user_chat_id, start_date, end_date)

        callback_data_keyboard = (
            f"categories_start_{start_date.strftime('%Y-%m-%d')}_end_{end_date.strftime('%Y-%m-%d')}"
        )

        await state.clear()

        if response == multilingual_texts.sorry.get(user_lang):
            await callback_query.message.answer(response)
        else:
            categories_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=multilingual_texts.show_categories.get(user_lang),
                        callback_data=callback_data_keyboard
                    )
                ]
            ])
            await callback_query.message.answer(response, reply_markup=categories_keyboard)

    # "Cancel" button handling
    elif callback_data.act == "CANCEL":
        await callback_query.message.delete()

    # Normal flow
    else:
        selected, end_user_date = await expenses_calendar.process_selection(callback_query, callback_data)
        if not selected:
            return
        await callback_query.message.delete()
        data = await state.get_data()
        start_date = data.get("start_date")
        end_date = end_user_date.replace(hour=23, minute=59, second=59, microsecond=0)

        response = await db_handler.show_expenses(user_chat_id, start_date, end_date)

        callback_data_keyboard = (
            f"categories_start_{start_date.strftime('%Y-%m-%d')}_end_{end_date.strftime('%Y-%m-%d')}"
        )

        await state.clear()

        if response == multilingual_texts.sorry.get(user_lang):
            await callback_query.message.answer(response)
        else:
            categories_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=multilingual_texts.show_categories.get(user_lang),
                        callback_data=callback_data_keyboard
                    )
                ]
            ])
            await callback_query.message.answer(response, reply_markup=categories_keyboard)


@dp.callback_query(F.data.startswith('categories'))
async def process_callback_show_categories(callback_query: CallbackQuery) -> None:
    user_chat_id = callback_query.message.chat.id

    start_date = datetime.strptime(callback_query.data.split('_')[2], '%Y-%m-%d')
    end_date = datetime.strptime(callback_query.data.split('_')[4], '%Y-%m-%d')
    end_date = end_date.replace(hour=23, minute=59, second=59)

    categories_str = await db_handler.categories(user_chat_id, start_date, end_date)
    await callback_query.message.answer(categories_str)


@dp.message(Command('delete'))
async def delete_entry(message: Message) -> None:
    user_chat_id = message.chat.id
    user_lang = await db_handler.get_user_language(user_chat_id)

    expenses = await db_handler.last_10_entries(user_chat_id)
    if isinstance(expenses, str):
        await message.answer(expenses)
    else:
        buttons = []
        for exp in expenses:
            if exp.get('description') == 0:
                text = f"{exp.get('timestamp').strftime('%d %b')} – {exp.get('price')} {exp.get('currency')}"
            else:
                text = (f"{exp.get('timestamp').strftime('%d %b')} – {exp.get('price')} {exp.get('currency')} "
                        f"({exp.get('description')})")

            buttons.append([
                InlineKeyboardButton(
                    text=text,
                    callback_data=f"del_expense={exp.get('timestamp')}"
                )
            ])
        keyboard = InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)
        await message.answer(multilingual_texts.delete_entry_message.get(user_lang), reply_markup=keyboard)


@dp.callback_query(F.data.startswith("del_expense="))
async def delete_expense_callback(callback_query):
    user_chat_id = callback_query.message.chat.id
    expense_id = callback_query.data.split("=")[1]
    expense_id = datetime.strptime(expense_id, "%Y-%m-%d %H:%M:%S.%f")

    confirmation_message = await db_handler.delete_entry(user_chat_id, expense_id)
    await callback_query.message.answer(confirmation_message)


@dp.message(Command('csv'))
async def get_csv(message: Message) -> None:
    user_chat_id = message.chat.id
    user_lang = await db_handler.get_user_language(user_chat_id)

    csv_path = Path(f'db_storage/{user_chat_id}.csv')
    if csv_path.exists():
        await message.answer_document(FSInputFile(csv_path))
    else:
        await message.answer(multilingual_texts.sorry_no_entries.get(user_lang))


@dp.message(Command('reset'))
async def reset_account(message: Message) -> None:
    user_chat_id = message.chat.id
    user_lang = await db_handler.get_user_language(user_chat_id)

    categories_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=multilingual_texts.reset_account_confirmation_answer.get(user_lang),
                callback_data='reset'
            )
        ]
    ])
    await message.answer(multilingual_texts.reset_account_confirmation.get(user_lang),
                         reply_markup=categories_keyboard)


@dp.callback_query(F.data == 'reset')
async def reset_account_callback(callback_query):
    user_chat_id = callback_query.message.chat.id

    response = await db_handler.reset_account(user_chat_id)
    await callback_query.message.answer(response)


@dp.message(F.voice)
async def voice_data_input(message: Message):
    user_chat_id = message.chat.id
    user_lang = await db_handler.get_user_language(user_chat_id)

    await tbot.send_chat_action(message.chat.id, action=ChatAction.TYPING)

    # easter egg for user Vi (my gf)
    if not user_chat_id == configuration.CHAT_ID_EASTER_EGG:
        # message reactions
        await tbot.set_message_reaction(
            chat_id=message.chat.id,
            message_id=message.message_id,
            reaction=[ReactionTypeEmoji(emoji=random.choice(["🫡", "👍", "👌", "🤝"]))]
        )
    else:
        await tbot.set_message_reaction(
            chat_id=message.chat.id,
            message_id=message.message_id,
            reaction=[ReactionTypeEmoji(emoji=random.choice(["🫡", "👍", "👌", "💩"]))]
        )

    # ASR transforms voice message to text
    file_bytes = await message.bot.download(message.voice.file_id)
    query = await transcript(file_bytes)
    # ASR upscale function uses GROQ to enhance ASR results (needed due to the low-performance Whisper model used)
    query_upscaled = await ASR_upscale(query, user_lang)

    # GROQ analyzes text query
    content = await main_query(query_upscaled, user_lang)

    # if the return in groq_client.main_query() was NaN, str with apologies is returned
    if isinstance(content, dict):
        confirmation = await db_handler.add_entry(content, user_chat_id, user_lang)
    else:
        confirmation = content

    await message.answer(confirmation)


@dp.message(F.text)
async def text_data_input(message: Message) -> None:
    user_chat_id = message.chat.id
    user_lang = await db_handler.get_user_language(user_chat_id)

    await tbot.send_chat_action(message.chat.id, action=ChatAction.TYPING)

    # easter egg for user Vi (my gf)
    if not user_chat_id == configuration.CHAT_ID_EASTER_EGG:
        # message reactions
        await tbot.set_message_reaction(
            chat_id=message.chat.id,
            message_id=message.message_id,
            reaction=[ReactionTypeEmoji(emoji=random.choice(["🫡", "👍", "👌", "🤝"]))]
        )
    else:
        await tbot.set_message_reaction(
            chat_id=message.chat.id,
            message_id=message.message_id,
            reaction=[ReactionTypeEmoji(emoji=random.choice(["🫡", "👍", "👌", "💩"]))]
        )

    # GROQ analyzes text query
    content = await main_query(message.model_dump_json(), user_lang)

    # if the return in groq_client.main_query() was NaN, str with apologies is returned
    if isinstance(content, dict):
        confirmation = await db_handler.add_entry(content, user_chat_id, user_lang)
    else:
        confirmation = content

    await message.answer(confirmation)


async def main() -> None:
    await set_commands(tbot)
    await dp.start_polling(tbot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
