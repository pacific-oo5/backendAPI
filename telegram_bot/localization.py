from userauth.models import TelegramProfile
from asgiref.sync import sync_to_async

LANGUAGES = {
    'kg': {'name': 'Кыргызча', 'flag': '🇰🇬'},
    'ru': {'name': 'Русский', 'flag': '🇷🇺'},
    'en': {'name': 'English', 'flag': '🇺🇸'}
}

TEXTS = {
    'kg': {
        'start': "Салам! 🎯 Аккаунтыңызды байланыштыруу үчүн уникалдуу ачкычты киргизиңиз:",
        'already_linked': "Сизде буга чейин байланыштырылган ачкыч бар: <b>{token}</b>",
        'token_kept': "Сиздин ачкыч сакталды ✅",
        'enter_new_token': "Жаңы ачкычты жөнөтүңүз:",
        'account_linked': "Аккаунт ачкычка байланыштырылды: <b>{token}</b> 🎉",
        'invalid_token': "Туура эмес ачкыч. Кайра аракет кылыңыз.",
        'enter_keyword': "Кошуу үчүн баскыч сөздү киргизиңиз (бир нече сөздү үтүр менен бөлүңүз):",
        'keyword_added': "Баскыч сөз '{text}' кошулду! ✅",
        'keyword_exists': "Бул сөз мурунтан эле фильтрде бар.",
        'enter_del_keyword': "Өчүрүү үчүн баскыч сөздү киргизиңиз:",
        'keyword_deleted': "Баскыч сөз '{text}' өчүрүлдү! 🗑️",
        'keyword_not_found': "Бул сөз фильтрде жок.",
        'no_filters': "Азырынча фильтрлер жок.",
        'filters_list': "Сиздин фильтрлер:\n",
        'not_linked': "Алгач /start командасы менен аккаунтыңызды байланыштырыңыз.",
        'unknown_command': "Төмөнкү командаларды колдонуңуз:",

        'inline_search_title': '🔍 Жумуш издөө',
        'inline_search_description': 'Издөө үчүн тилди/технологияны киргизиңиз',
        'inline_search_message': 'Жумуш издөө үчүн технологияны же жөндөмдү киргизиңиз\n\nМисалы: python, javascript, дизайнер',
        'inline_no_results_title': '😔 Вакансиялар табылган жок',
        'inline_no_results_description': '"{query}" боюнча эч нерсе табылган жок',
        'inline_no_results_message': '"{query}" боюнча жумуш табылган жок\n\nБашка издөө сурамын байкап көрүңүз',
        'salary': 'сом',
        'location': 'Алыстан',
        'work_type': 'Жумуштун түрү',
        'view_vacancy_button': 'Толук маалымат',

        'view_vacancy': '📋 Вакансияны көрүү',
        'view_vacancy_link': 'Вакансиянын шилтемеси',

        'help_text': """
🤖 <b>Бот жөнүндө инструкция</b>

🎯 <b>Негизги командалар:</b>
/start - Ботту ишке киргизүү же аккаунт байланыштыруу
/help - Жардам көрсөтүү
/lang - Тилди өзгөртүү

🔍 <b>Фильтр башкаруу:</b>
/addfilter - Жаңы баскыч сөз кошуу
/delfilter - Баскыч сөз өчүрүү
/listfilters - Баарын көрүү

💡 <b>Кеңештер:</b>
• Бир нече сөздү үтүр менен бөлүп жаза аласыз: python,django,css
• Вакансиялар сиздин баскыч сөздөрүңүзгө ылайык келгенде эле билдирим аласыз
        """,
        'choose_language': "Тилди тандаңыз:",
        'language_changed': "Тил өзгөртүлдү: {language} ✅",
        'new_response': "📩 Жаңы жооп сиздин <b>{title}</b> вакансийаңызга",
        'candidate': "Аталышы: {username}\nТажрыйбасы: {experience}\nШаар: {city}",
    },
    'ru': {
        'start': "Привет! 🎯 Введите ваш уникальный ключ для привязки аккаунта:",
        'already_linked': "У вас уже привязан токен: <b>{token}</b>",
        'token_kept': "Ваш токен оставлен ✅",
        'enter_new_token': "Отправьте новый токен для привязки:",
        'account_linked': "Аккаунт привязан к токену: <b>{token}</b> 🎉",
        'invalid_token': "Неверный токен. Попробуйте снова.",
        'enter_keyword': "Введите ключевое слово для добавления (несколько слов через запятую):",
        'keyword_added': "Ключевое слово '{text}' добавлено! ✅",
        'keyword_exists': "Слово уже есть в фильтрах.",
        'enter_del_keyword': "Введите ключевое слово для удаления:",
        'keyword_deleted': "Ключевое слово '{text}' удалено! 🗑️",
        'keyword_not_found': "Слова нет в фильтрах.",
        'no_filters': "Фильтров пока нет.",
        'filters_list': "Ваши фильтры:\n",
        'not_linked': "Сначала привяжите аккаунт через /start.",
        'unknown_command': "Используйте команды:",
        'view_vacancy_button': 'Подробная информация',

        'inline_search_title': '🔍 Поиск вакансий',
        'inline_search_description': 'Введите язык/технологию для поиска',
        'inline_search_message': 'Введите технологию или навык для поиска вакансий\n\nНапример: python, javascript, designer',
        'inline_no_results_title': '😔 Вакансий не найдено',
        'inline_no_results_description': 'По запросу "{query}" ничего не найдено',
        'inline_no_results_message': 'По запросу "{query}" вакансий не найдено\n\nПопробуйте другой поисковый запрос',
        'salary': 'сом',
        'location': 'Удаленно',
        'work_type': 'Тип работы',

        'view_vacancy': '📋 Посмотреть вакансию',
        'view_vacancy_link': 'Ссылка на вакансию',

        'help_text': """
🤖 <b>Инструкция по боту</b>

🎯 <b>Основные команды:</b>
/start - Запуск бота или привязка аккаунта
/help - Помощь
/lang - Смена языка

🔍 <b>Управление фильтрами:</b>
/addfilter - Добавить ключевое слово
/delfilter - Удалить ключевое слово
/listfilters - Посмотреть все

💡 <b>Советы:</b>
• Можно вводить несколько слов через запятую: python,django,css
• Уведомления будут приходить только по вашим ключевым словам
        """,
        'choose_language': "Выберите язык:",
        'language_changed': "Язык изменен: {language} ✅",
        'new_response': "📩 Новый отклик на вашу вакансию <b>{title}</b>",
        'candidate': "Имя кандидата: {username}\nОпыт: {experience}\nГород: {city}",
    },
    'en': {
        'start': "Hello! 🎯 Enter your unique key to link your account:",
        'already_linked': "You already have a linked token: <b>{token}</b>",
        'token_kept': "Your token has been kept ✅",
        'enter_new_token': "Send a new token for linking:",
        'account_linked': "Account linked to token: <b>{token}</b> 🎉",
        'invalid_token': "Invalid token. Please try again.",
        'enter_keyword': "Enter keyword to add (multiple words separated by commas):",
        'keyword_added': "Keyword '{text}' added! ✅",
        'keyword_exists': "Word already exists in filters.",
        'enter_del_keyword': "Enter keyword to delete:",
        'keyword_deleted': "Keyword '{text}' deleted! 🗑️",
        'keyword_not_found': "Word not found in filters.",
        'no_filters': "No filters yet.",
        'filters_list': "Your filters:\n",
        'not_linked': "First link your account with /start.",
        'unknown_command': "Use commands:",
        'view_vacancy_button': 'Detailed information',

        'inline_search_title': '🔍 Search for vacancies',
        'inline_search_description': 'Enter language/technology to search',
        'inline_search_message': 'Enter a technology or skill to search for jobs\n\nFor example: python, javascript, designer',
        'inline_no_results_title': '😔 No vacancies found',
        'inline_no_results_description': 'Nothing found for "{query}"',
        'inline_no_results_message': 'No jobs found for "{query}"\n\nTry another search query',
        'salary': 'som',
        'location': 'Remotely',
        'work_type': 'Type of work',

        'view_vacancy': '📋 View vacancy',
        'view_vacancy_link': 'Vacancy link',

        'help_text': """
🤖 <b>Bot Instructions</b>

🎯 <b>Main commands:</b>
/start - Start bot or link account
/help - Help
/lang - Change language

🔍 <b>Filter management:</b>
/addfilter - Add keyword
/delfilter - Delete keyword
/listfilters - View all

💡 <b>Tips:</b>
• You can enter multiple words separated by commas: python,django,css
• Notifications will come only for your keywords
        """,
        'choose_language': "Choose language:",
        'language_changed': "Language changed: {language} ✅",
        'new_response': "📩 New response to your vacancy <b>{title}</b>",
        'candidate': "Candidate: {username}\nExperience: {experience}\nCity: {city}",
    }
}

async def get_user_language(telegram_id):
    """Получаем язык пользователя асинхронно"""
    profile = await sync_to_async(lambda: TelegramProfile.objects.filter(telegram_id=telegram_id).first())()
    if profile and profile.language in LANGUAGES:
        return profile.language
    return 'ru'
