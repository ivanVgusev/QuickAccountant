sorry = {
    'en': "Sorry, we couldn't process your expenses this time. Could you please try again?",
    'ru': "Извините, не удалось обработать ваши расходы. Попробуйте, пожалуйста, еще раз."
}

sorry_no_entries = {
    'en': "Looks like you don’t have any expenses to extract right now.",
    'ru': "Похоже, у вас пока нет расходов для обработки."
}

sorry_no_entries_period = {
    'en': "It looks like you have no expenses for this time period.",
    'ru': "Похоже, что на этот период у вас нет никаких расходов."
}

"""
LLM
"""

expense_extractor_prompt = {
    'en': """
        You are an assistant that extracts expense data from natural language text and returns ONLY a JSON object 
        with these keys:

        - price: number (float or int) - currency: string (only standard 3-letter currency abbreviations, e.g. USD, 
        EUR, RUB — do NOT return full currency names like "pounds" or "dollars"; do NOT return currency signs like $ 
        or ₽) - description: string describing the purchase (or 0 if missing). Return words in the initial form ('200 
        rubles for chewing gum' -> 'chewing gum');

          IMPORTANT: - do NOT include currency names or currency codes in the description. - description must only 
          describe the item or service bought, excluding any mention of currency or price. - if the description 
          cannot be clearly separated from the currency name, or if no valid description is present, return 0 in the 
          description field. - never guess or repeat currency names as descriptions.

        Example with full info:
        {{
          "price": 5,
          "currency": "RUB",
          "description": "стакан молока"
        }}

        Example with missing description:
        {{
          "price": 50,
          "currency": "USD",
          "description": 0
        }}

        Incorrect example (do NOT repeat currency in description):
        {{
          "price": 15,
          "currency": "WST",
          "description": "самоанских тал"
        }}

        Corrected example:
        {{
          "price": 15,
          "currency": "WST",
          "description": 0
        }}

        If any field cannot be extracted, return 0 or a valid default value as above.  
        Never return None or null.  
        Return ONLY the JSON object, no explanations or extra text, no other text but the JSON object.

        Input text: "{user_input}"
        """,
    'ru': """Вы — ассистент, который извлекает данные о расходах из текста на естественном языке и возвращает ТОЛЬКО объект JSON со следующими ключами:
            
            - price: число (float или int).
            - currency: строка (только стандартные трёхбуквенные коды валют, например USD, EUR, RUB. Не возвращайте полные названия валют вроде «фунты» или «доллары»; не используйте символы валют вроде $ или ₽).
            - description: строка с описанием покупки (или 0, если описание отсутствует). Все слова в описании должны быть приведены в начальную форму (лемму). Примеры:
              «200 рублей на жвачку» -> «жвачка»
              «700 рублей на аптеку» -> «аптека»
              «600 рублей поиграл в футбол» -> «поиграть в футбол»
            
            ВАЖНО:
            - В поле description не включайте названия валют или их коды.
            - description должно содержать только предмет или услугу, без упоминания валюты или цены.
            - Если описание нельзя чётко отделить или оно отсутствует, возвращайте 0.
            - Никогда не повторяйте валюту в описании.
            - Никогда не возвращайте None или null — только 0 или валидное значение.
            - Ответ всегда должен быть строго валидным JSON без пояснений.
            
            Пример с полной информацией:
            {{
              "price": 5,
              "currency": "RUB",
              "description": "стакан молоко"
            }}
            
            Пример с отсутствующим описанием:
            {{
              "price": 50,
              "currency": "USD",
              "description": 0
            }}
            
            Неправильный пример (неверное описание):
            {{
              "price": 15,
              "currency": "WST",
              "description": "самоанских тал"
            }}
            
            Правильный пример:
            {{
              "price": 15,
              "currency": "WST",
              "description": 0
            }}
            
            Входной текст: "{user_input}"
            """
}

purchase_category_prompt = {
    'en': """You are a professional accountant. Your task is to determine which category from the list below 
    best describes the given purchase.

        List of categories:

        * Housing: Rent/mortgage, Utilities, Internet and communication, Home maintenance, Furniture
        * Groceries and Household Items: Food, Cleaning supplies, Personal hygiene, Household goods
        * Transportation: Fuel, Public transport, Taxi/carsharing, Car insurance, Car maintenance, Parking
        * Children: Clothing, Toys, Kindergarten/school, Clubs, Medical expenses
        * Health: Medication, Insurance, Doctor services, Fitness
        * Work and Education: Courses, Books, Stationery, Online services
        * Entertainment and Leisure: Restaurants, Cinema, Travel, Hobbies
        * Clothing and Shoes: Everyday clothing, Sportswear, Footwear, Accessories
        * Pets: Pet food, Veterinary services, Accessories

        Instructions:

        1. Always choose exactly one category from the list above. 
        2. Under no circumstances return None, null or a category that is not listed. 
        3. The output must be **only** the category name exactly as written in the list, with no extra words, 
        no punctuation, and nothing else at all. One line only. No questions, no multiple choice, no examples.
        4. If the input does not provide enough information to determine a specific category, return 0.

        Reply with exactly one line: only the category name. Example: Transportation

        Input text: "{user_input}" """,
    'ru': """Вы профессиональный бухгалтер. Ваша задача — определить, какая категория из списка ниже
лучше всего описывает данную покупку.

Список категорий:

Жильё: аренда/ипотека, коммунальные услуги, интернет и связь, обслуживание дома, мебель

Продукты и хозяйственные товары: еда, моющие средства, личная гигиена, товары для дома

Транспорт: топливо, общественный транспорт, такси/каршеринг, страховка автомобиля, обслуживание автомобиля, парковка

Дети: одежда, игрушки, детский сад/школа, кружки, медицинские расходы

Здоровье: медикаменты, страховка, услуги врачей, фитнес

Работа и образование: курсы, книги, канцелярия, онлайн-сервисы

Развлечения и отдых: рестораны, кино, путешествия, хобби

Одежда и обувь: повседневная одежда, спортивная одежда, обувь, аксессуары

Домашние животные: корм, ветеринарные услуги, аксессуары

Инструкции:

Всегда выбирайте ровно одну категорию из приведённого списка.

Ни в коем случае не возвращайте None, null или категорию, которой нет в списке.

В ответе должно быть только название категории точно так, как в списке, без лишних слов,
знаков препинания и всего остального. Одна строка. Никаких вопросов, вариантов ответа (а/б/в) и примеров.

Если входные данные не содержат достаточно информации для определения конкретной категории, верните 0.

Ответьте ровно одной строкой — только названием категории. Пример: Транспорт

Входной текст: "{user_input}" """
}

ASR_upscale_prompt = {
    'en': """You are a smart speech transcription editor.  
            Your task is to correct errors from speech recognition (ASR).  
            Preserve the original meaning and numbers.  
            Fix incorrectly recognized words, replacing them with logical and grammatically correct ones.  
            Remove obvious recognition artifacts (for example: "uh", "mm", repetitions).  
            If part of a phrase sounds strange, restore it to the most likely and meaningful version.  
            Never add information that is not in the original text.  
            Return only the corrected text without explanations.  
            If the phrase sounds correct, do not change anything, just return the same phrase without edits.  
            
            Here’s an example of text after incorrect speech recognition:  
            "350 rubles delivery this"  
            
            Expected response:  
            "350 rubles food delivery"  
            
            Now do this for the following phrase: {query}""",
    'ru': "Ты — умный редактор расшифровок речи. "
          "Твоя задача — исправлять ошибки распознавания речи (ASR). "
          "Сохраняй исходный смысл и цифры. "
          "Исправляй неправильно подобранные слова, заменяй их на логичные и грамматически правильные. "
          "Убирай явные артефакты распознавания (например: 'э-э', 'мм', повторы). "
          "Если часть фразы звучит странно, восстанавливай её до наиболее вероятного и осмысленного варианта. "
          "Никогда не добавляй информации, которой нет в исходном тексте. "
          "Возвращай только исправленный текст без пояснений."
          "Если фраза звучит правильно, ничего не изменяй, возвращай ту же самую фразу без исправлений."
          "Вот пример текста после неверного распознавания речи:"
          "\"350 рублей доставка этой\""
          "Ожидаемый ответ:\n"
          "\"350 рублей доставка еды\""
          "Теперь сделай это для следующей фразы: {query}"

}

"""
DB HANDLER
"""

db_confirmation_message_no_description = {
    'en': [
        "✅ Great! I’ve logged {price} {currency} for you. 🎉",
        "👌 Done! Your entry of {price} {currency} is saved.",
        "🎯 Success! Added {price} {currency} to your records.",
        "✨ All set! {price} {currency} is safely stored.",
        "📌 Noted! {price} {currency} has been added.",
        "🚀 Boom! {price} {currency} recorded.",
        "🎉 Yay! I’ve saved {price} {currency} for you.",
        "✅ Got it! {price} {currency} is now logged.",
        "📝 Done! Your {price} {currency} is in the books.",
        "👍 Perfect! I’ve added {price} {currency} to your log.",
        "🙌 Entry complete! {price} {currency} registered.",
        "✅ Done and dusted! {price} {currency} saved.",
        "📒 Recorded! {price} {currency} noted down.",
        "💾 Saved! {price} {currency} successfully logged.",
        "👌 All clear! Your {price} {currency} is stored.",
        "🎊 Hooray! {price} {currency} added to the list.",
        "🟢 Success! {price} {currency} registered.",
        "📍 Marked! {price} {currency} is now in records.",
        "✅ Sure thing! Logged {price} {currency}.",
        "🌟 Done! {price} {currency} safely registered."
    ],
    'ru': [
        "✅ Отлично! Я записал {price} {currency}. 🎉",
        "👌 Готово! {price} {currency} сохранено.",
        "🎯 Успех! Добавил {price} {currency} в записи.",
        "✨ Всё на месте! {price} {currency}.",
        "📌 Отмечено! {price} {currency} внесено.",
        "🚀 Есть! {price} {currency} зафиксировано.",
        "🎉 Ура! {price} {currency} сохранено.",
        "✅ Принято! {price} {currency} занесено.",
        "📝 Готово! {price} {currency} в журнале.",
        "👍 Отлично! {price} {currency} добавлено.",
        "🙌 Запись сделана! {price} {currency} учтено.",
        "✅ Всё готово! {price} {currency} сохранено.",
        "📒 Записано! {price} {currency} добавлено.",
        "💾 Сохранено! {price} {currency} учтено.",
        "👌 Всё чисто! {price} {currency} зафиксировано.",
        "🎊 Супер! {price} {currency} внесено.",
        "🟢 Успешно! {price} {currency} зарегистрировано.",
        "📍 Отметил! {price} {currency} теперь в записях.",
        "✅ Конечно! Занёс {price} {currency}.",
        "🌟 Готово! {price} {currency} учтено."
    ]
}

db_confirmation_message_description_no_category = {
    'en': [
        "Got it! {price} {currency} is saved: \"{description}\".",
        "Done! Logged {price} {currency}: \"{description}\".",
        "Success! Added {price} {currency}: \"{description}\".",
        "All set! {price} {currency} purchase \"{description}\" noted.",
        "Noted! \"{description}\" cost {price} {currency}.",
        "Boom! Saved {price} {currency}: \"{description}\".",
        "Yay! Your expense of {price} {currency}: \"{description}\" is recorded.",
        "Got it covered! {price} {currency}: \"{description}\" logged.",
        "Done! Added {price} {currency}: \"{description}\".",
        "Perfect! {price} {currency}: \"{description}\" registered.",
        "Entry complete! \"{description}\" — {price} {currency}.",
        "Done and dusted! \"{description}\" — {price} {currency}.",
        "Recorded: {price} {currency} — \"{description}\".",
        "Saved! Expense {price} {currency}: \"{description}\" noted.",
        "All clear! Logged {price} {currency}: \"{description}\".",
        "Hooray! \"{description}\" ({price} {currency}) has been saved.",
        "Success! {price} {currency} recorded: \"{description}\".",
        "Marked: {price} {currency}. \"{description}\".",
        "Sure thing! Registered {price} {currency}: \"{description}\".",
        "Done! {price} {currency}: \"{description}\" stored."
    ],
    'ru': [
        "Готово! {price} {currency}: \"{description}\" записано.",
        "Отлично! Учёл {price} {currency}: \"{description}\".",
        "Успех! Добавил {price} {currency}: \"{description}\".",
        "Всё на месте! Покупка \"{description}\": {price} {currency} учтена.",
        "Отмечено! \"{description}\" — {price} {currency}.",
        "Есть! Записал {price} {currency}: \"{description}\".",
        "Ура! Трата {price} {currency}: \"{description}\" сохранена.",
        "Принято! {price} {currency}: \"{description}\" учтено.",
        "Готово! Добавил {price} {currency}: \"{description}\".",
        "Отлично! Зарегистрировал {price} {currency}: \"{description}\".",
        "Запись завершена! \"{description}\" — {price} {currency}.",
        "Всё готово! \"{description}\" — {price} {currency} сохранено.",
        "Записано: {price} {currency}: \"{description}\".",
        "Сохранено! Расход {price} {currency}: \"{description}\" учтён.",
        "Всё чисто! Учёл {price} {currency}: \"{description}\".",
        "Супер! \"{description}\" ({price} {currency}) внесено.",
        "Успешно! {price} {currency}: \"{description}\" зарегистрировано.",
        "Отметил: {price} {currency}. \"{description}\".",
        "Конечно! Занёс {price} {currency}: \"{description}\".",
        "Готово! Трата {price} {currency}: \"{description}\" учтена."
    ]
}

db_confirmation_message_description = {
    'en': [
        "Got it! {price} {currency} is saved: \"{description}\". 📂 Category: {category}.",
        "Done! Logged {price} {currency}: \"{description}\". 🗂️ Category: {category}.",
        "Success! Added {price} {currency}: \"{description}\". 📌 Category: {category}.",
        "All set! {price} {currency} purchase \"{description}\" noted. 📂 Category: {category}.",
        "Noted! \"{description}\" cost {price} {currency}. Category: {category}.",
        "Boom! Saved {price} {currency}: \"{description}\". 📂 {category}.",
        "Yay! Your expense of {price} {currency}: \"{description}\" is recorded. 📂 Category: {category}.",
        "Got it covered! {price} {currency}: \"{description}\" logged. 📂 {category}.",
        "Done! Added {price} {currency}: \"{description}\". Category: {category}.",
        "Perfect! {price} {currency}: \"{description}\" registered. 📂 {category}.",
        "Entry complete! \"{description}\" — {price} {currency}. Category: {category}.",
        "Done and dusted! \"{description}\" — {price} {currency}. 📂 {category}.",
        "Recorded: {price} {currency} — \"{description}\". Category: {category}.",
        "Saved! Expense {price} {currency}: \"{description}\" noted. 📂 {category}.",
        "All clear! Logged {price} {currency}: \"{description}\". Category: {category}.",
        "Hooray! \"{description}\" ({price} {currency}) has been saved. 📂 {category}.",
        "Success! {price} {currency} recorded: \"{description}\". 📂 Category: {category}.",
        "Marked: {price} {currency}. \"{description}\". Category: {category}.",
        "Sure thing! Registered {price} {currency}: \"{description}\". 📂 {category}.",
        "Done! {price} {currency}: \"{description}\" stored. Category: {category}."
    ],
    'ru': [
        "Готово! {price} {currency}: \"{description}\" записано. 📂 Категория: {category}.",
        "Отлично! Учёл {price} {currency}: \"{description}\". 🗂️ Категория: {category}.",
        "Успех! Добавил {price} {currency}: \"{description}\". 📌 Категория: {category}.",
        "Всё на месте! Покупка \"{description}\": {price} {currency} учтена. 📂 Категория: {category}.",
        "Отмечено! \"{description}\" — {price} {currency}. Категория: {category}.",
        "Есть! Записал {price} {currency}: \"{description}\". 📂 {category}.",
        "Ура! Трата {price} {currency}: \"{description}\" сохранена. 📂 Категория: {category}.",
        "Принято! {price} {currency}: \"{description}\" учтено. 📂 {category}.",
        "Готово! Добавил {price} {currency}: \"{description}\". Категория: {category}.",
        "Отлично! Зарегистрировал {price} {currency}: \"{description}\". 📂 {category}.",
        "Запись завершена! \"{description}\" — {price} {currency}. Категория: {category}.",
        "Всё готово! \"{description}\" — {price} {currency} сохранено. 📂 {category}.",
        "Записано: {price} {currency}: \"{description}\". Категория: {category}.",
        "Сохранено! Расход {price} {currency}: \"{description}\" учтён. 📂 {category}.",
        "Всё чисто! Учёл {price} {currency}: \"{description}\". Категория: {category}.",
        "Супер! \"{description}\" ({price} {currency}) внесено. 📂 {category}.",
        "Успешно! {price} {currency}: \"{description}\" зарегистрировано. 📂 Категория: {category}.",
        "Отметил: {price} {currency}. \"{description}\". Категория: {category}.",
        "Конечно! Занёс {price} {currency}: \"{description}\". 📂 {category}.",
        "Готово! Трата {price} {currency}: \"{description}\" учтена. Категория: {category}."
    ]
}

db_last_10_entries_message = {
    'en': "You have no expense records to delete yet.",
    'ru': "У вас пока что нет записей о расходах."
}

db_delete_entry_message = {
    'en': 'All done! Entry for {index_timestamp} deleted successfully!',
    'ru': 'Все готово! Запись за {index_timestamp} успешно удалена!'
}

db_show_expenses_message = {
    'en': '💸 Expenses for the period:\n {expenses_string}\n\n 🌍 Total: {expenses_USD} USD',
    'ru': '💸 Расходы за период:\n {expenses_string}\n\n 🌍 Всего: {expenses_USD} USD'
}

unknown_category = {
    'en': 'Unrecognized expenses',
    'ru': 'Нераспознанные расходы'
}

"""
BOT
"""

help_message = {
    'en': "🔹 <b>Privacy First</b>\n"
          "Quick Accountant is fully open source and respects your privacy. We do not collect or use your data for "
          "any external purpose. All your expenses are stored locally in the database and in your personal CSV "
          "exports — nothing is sent to third parties. You stay in control of your data at all times.\n"
          "🔹 <b>Where is my data stored?</b>\n"
          "In the bot’s local database. It is completely free!\n"
          "🔹 <b>Can I edit past expenses?</b>\n"
          "Currently, you can only delete the last 10 entries with /delete.\n"
          "🔹 <b>Does it support currencies?</b>\n"
          "Yes, the bot saves the currency you specify (USD, EUR, RUB, etc.).\n"
          "🔹 <b>Can I export all expenses?</b>\n"
          "Yes, use /csv to download your expense sheet.\n"
          "🔹 <b>What if the voice recognition is wrong?</b>\n"
          "You can fix it by typing the expense manually or deleting the wrong entry.\n\n"
          "✉️ Still got questions? Just ask us @QuickAccountantBotSupport!",

    'ru': "🔹 <b>Приватность прежде всего</b>\n"
          "Quick Accountant — open source проект. Мы уважаем вашу конфиденциальность "
          "и не собираем ваши данные для сторонних целей. "
          "Все ваши расходы сохраняются локально в базе данных — "
          "<b>ничего</b> не передаётся третьим лицам. Именно <b>вы</b> контролируете свои данные.\n"
          "🔹 <b>Где хранятся мои данные?</b>\n"
          "В локальной базе данных бота. Это бесплатно!\n"
          "🔹 <b>Могу ли я редактировать прошлые расходы?</b>\n"
          "На данный момент можно удалить только последние 10 записей с помощью /delete.\n"
          "🔹 <b>Поддерживаются ли валюты?</b>\n"
          "Да, бот сохраняет указанную вами валюту (USD, EUR, RUB и т.д.).\n"
          "🔹 <b>Можно ли экспортировать все расходы?</b>\n"
          "Да, используйте /csv для скачивания вашей таблицы расходов.\n"
          "🔹 <b>Что делать, если распознавание голоса ошиблось?</b>\n"
          "Вы можете исправить это, введя расход вручную или удалив неверную запись.\n\n"
          "✉️ Остались вопросы? Просто напишите нам @QuickAccountantBotSupport!"

}

calendar_start_message = {
    'en': 'Select the start date: ',
    'ru': 'Выберите началальную дату: '
}

calendar_end_message = {
    'en': 'Now select the end date: ',
    'ru': 'Теперь выберите конечную дату: '
}

delete_entry_message = {
    'en': 'Select the expense you want to delete: ',
    'ru': 'Выберите расход, который хотите удалить: '
}

start_intro = {
    'en': "Here’s a quick overview of what I can do for you!\n"
          "🔷 Add expenses easily — Just type something like 5 "
          "dollars on a cup of coffee or send me a voice message, and I’ll record it for you.\n"
          "🔷 View your spending — "
          "Use /expenses to see a summary of where your money is going.\n"
          "🔷 Delete recent entries — Need to fix a "
          "mistake? Use /delete to remove one of your last 10 expense records.\n"
          "🔷 Export your data — Type /csv to "
          "download your expenses as a CSV file, ready for Excel or Google Sheets.\n"
          "🔷 Get more details — Use /help to "
          "learn about our mission and privacy policy.\n"
          "🔷 If you want to delete ALL the information about your expenses and your profile, use /reset.\n\n"
          "💬 Have questions? Reach out anytime at "
          "@QuickAccountantBotSupport.\n\n"
          "<i>P.S. For the best bot performance, please specify exactly what you spent money on.</i>\nFor example: "
          "'20 bucks <b>for a T-shirt</b>'\n"
          "<i>P.P.S. If you use voice messages, do not start talking right away, as Telegram does not immediately "
          "start recording your voice.</i>"
    ,
    'ru': "Вот краткий обзор того, что я умею!\n"
          "🔷 Добавляйте расходы легко — просто напишите что-то вроде '300 рублей "
          "на чашку кофе' или отправьте мне голосовое сообщение. Я все запишу!\n"
          "🔷 Просматривайте траты — используйте "
          "/expenses, чтобы увидеть сводку ваших расходов.\n"
          "🔷 Удаляйте последние записи. Допустили ошибку? Введите "
          "/delete, чтобы удалить одну из последних 10 записей.\n"
          "🔷 Экспортируйте данные — используйте /csv, "
          "чтобы скачать ваши расходы в формате CSV, экспортируемом в Excel или Google Таблицах.\n"
          "🔷 Узнайте больше — "
          "введите /help, чтобы ознакомиться с нашей политикой конфиденциальности и часто задаваемыми вопросами.\n"
          "🔷 Если вы хотите удалить ВСЕ данные о расходах и вашем аккаунте, используйте /reset.\n\n"
          "💬 Есть вопросы? "
          "Свяжитесь с нами в @QuickAccountantBotSupport.\n\n"
          "<i>P.S. Для лучшей работы бота, уточняйте, пожалуйста, на что именно потратили деньги.</i>\nНапример: "
          "'Тысяча рублей <b>на ресторан</b>\n'"
          "<i>P.P.S. Если вы пользуетесь голосовыми сообщениями, не начинайте говорить сразу, так как Telegram "
          "начинает записывать ваш голос через полсекунды/секунду.</i>"
}

show_categories = {
    'en': 'Show expense categories',
    'ru': 'Показать категории расходов'
}

reset_account_confirmation = {
    'en': 'Are you sure you want to delete ALL expense records?',
    'ru': 'Вы уверены, что хотите удалить ВСЕ записи о расходах?'
}

reset_account_confirmation_answer = {
    'en': 'Yes!',
    'ru': 'Да!'
}

reset_account_deleted_successfully = {
    'en': 'All expense records have been deleted.',
    'ru': 'Все записи о расходах были удалены.'
}

reset_account_deleted_unsuccessfully = {
    'en': 'You have no expenses to delete.',
    'ru': 'У вас нет расходов, которые можно было бы удалить.'
}
