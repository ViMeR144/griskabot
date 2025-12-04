import asyncio
import logging
import os
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токен из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден! Создайте файл .env и добавьте туда BOT_TOKEN=ваш_токен")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# База данных (в реальном проекте используйте БД)
user_schedule = {}  # Расписание пользователя
user_homework = {}  # Домашние задания
user_notes = {}     # Заметки
user_reminders = {} # Напоминания


# Функция создания главного меню
def get_main_menu():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="📅 Расписание", callback_data="schedule"))
    keyboard.add(InlineKeyboardButton(text="📝 Домашние задания", callback_data="homework"))
    keyboard.add(InlineKeyboardButton(text="📌 Заметки", callback_data="notes"))
    keyboard.add(InlineKeyboardButton(text="⏰ Напоминания", callback_data="reminders"))
    keyboard.add(InlineKeyboardButton(text="📚 Полезные ссылки", callback_data="links"))
    keyboard.add(InlineKeyboardButton(text="ℹ️ О боте", callback_data="about"))
    keyboard.adjust(2, 2, 1, 1)
    return keyboard.as_markup()


# Функция создания клавиатуры для расписания
def get_schedule_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="📅 Сегодня", callback_data="schedule_today"))
    keyboard.add(InlineKeyboardButton(text="📆 Завтра", callback_data="schedule_tomorrow"))
    keyboard.add(InlineKeyboardButton(text="📋 Вся неделя", callback_data="schedule_week"))
    keyboard.add(InlineKeyboardButton(text="➕ Добавить занятие", callback_data="schedule_add"))
    keyboard.add(InlineKeyboardButton(text="🗑️ Удалить занятие", callback_data="schedule_delete"))
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu"))
    keyboard.adjust(2, 2, 1, 1)
    return keyboard.as_markup()


# Функция создания клавиатуры для домашних заданий
def get_homework_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="📋 Список заданий", callback_data="homework_list"))
    keyboard.add(InlineKeyboardButton(text="➕ Добавить задание", callback_data="homework_add"))
    keyboard.add(InlineKeyboardButton(text="✅ Выполнено", callback_data="homework_done"))
    keyboard.add(InlineKeyboardButton(text="🗑️ Удалить", callback_data="homework_delete"))
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu"))
    keyboard.adjust(2, 2, 1)
    return keyboard.as_markup()


# Функция создания клавиатуры для заметок
def get_notes_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="📋 Мои заметки", callback_data="notes_list"))
    keyboard.add(InlineKeyboardButton(text="➕ Новая заметка", callback_data="notes_add"))
    keyboard.add(InlineKeyboardButton(text="🔍 Поиск", callback_data="notes_search"))
    keyboard.add(InlineKeyboardButton(text="🗑️ Удалить", callback_data="notes_delete"))
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu"))
    keyboard.adjust(2, 2, 1)
    return keyboard.as_markup()


# Функция создания клавиатуры для полезных ссылок
def get_links_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="🌐 Сайт колледжа", url="https://example-college.ru"))
    keyboard.add(InlineKeyboardButton(text="📱 Соцсети", url="https://vk.com/college"))
    keyboard.add(InlineKeyboardButton(text="📚 Библиотека", url="https://library.college.ru"))
    keyboard.add(InlineKeyboardButton(text="💬 Чат студентов", url="https://t.me/college_chat"))
    keyboard.add(InlineKeyboardButton(text="🎮 FunPay", url="https://funpay.com"))
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu"))
    keyboard.adjust(2, 2, 1, 1)
    return keyboard.as_markup()


# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = get_main_menu()
    user_id = message.from_user.id
    
    # Инициализируем данные пользователя
    if user_id not in user_schedule:
        user_schedule[user_id] = []
    if user_id not in user_homework:
        user_homework[user_id] = []
    if user_id not in user_notes:
        user_notes[user_id] = []
    if user_id not in user_reminders:
        user_reminders[user_id] = []
    
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "🎓 Добро пожаловать в бота-помощника для колледжа!\n\n"
        "Я помогу тебе:\n"
        "• 📅 Следить за расписанием\n"
        "• 📝 Управлять домашними заданиями\n"
        "• 📌 Сохранять важные заметки\n"
        "• ⏰ Не забывать о дедлайнах\n"
        "• 📚 Быстро находить полезные ссылки\n\n"
        "Выбери действие:",
        reply_markup=keyboard
    )


# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "📚 <b>Команды бота:</b>\n\n"
        "/start - Главное меню\n"
        "/help - Помощь\n"
        "/schedule - Расписание\n"
        "/homework - Домашние задания\n"
        "/notes - Заметки\n\n"
        "Используй кнопки для навигации! 🎓",
        parse_mode="HTML"
    )


# Обработчик callback для главного меню
@dp.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery):
    keyboard = get_main_menu()
    await callback.message.edit_text(
        "🎓 <b>Главное меню</b>\n\n"
        "Выбери действие:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


# Обработчик callback для расписания
@dp.callback_query(F.data == "schedule")
async def callback_schedule(callback: CallbackQuery):
    keyboard = get_schedule_keyboard()
    await callback.message.edit_text(
        "📅 <b>Расписание занятий</b>\n\n"
        "Выбери действие:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


# Обработчик callback для расписания на сегодня
@dp.callback_query(F.data == "schedule_today")
async def callback_schedule_today(callback: CallbackQuery):
    user_id = callback.from_user.id
    today = datetime.now().strftime("%A")
    today_ru = {
        "Monday": "Понедельник",
        "Tuesday": "Вторник",
        "Wednesday": "Среда",
        "Thursday": "Четверг",
        "Friday": "Пятница",
        "Saturday": "Суббота",
        "Sunday": "Воскресенье"
    }.get(today, today)
    
    schedule = user_schedule.get(user_id, [])
    today_schedule = [s for s in schedule if s.get('day') == today_ru]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Назад к расписанию", callback_data="schedule")
    ]])
    
    if today_schedule:
        schedule_text = "\n".join([
            f"🕐 {s['time']} - {s['subject']}\n   📍 {s.get('room', 'Аудитория не указана')}\n"
            for s in sorted(today_schedule, key=lambda x: x.get('time', ''))
        ])
        await callback.message.edit_text(
            f"📅 <b>Расписание на сегодня ({today_ru})</b>\n\n{schedule_text}",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            f"📅 <b>Расписание на сегодня ({today_ru})</b>\n\n"
            "На сегодня занятий нет! 🎉\n"
            "Или добавь расписание через кнопку '➕ Добавить занятие'",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    await callback.answer()


# Обработчик callback для расписания на завтра
@dp.callback_query(F.data == "schedule_tomorrow")
async def callback_schedule_tomorrow(callback: CallbackQuery):
    user_id = callback.from_user.id
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%A")
    tomorrow_ru = {
        "Monday": "Понедельник",
        "Tuesday": "Вторник",
        "Wednesday": "Среда",
        "Thursday": "Четверг",
        "Friday": "Пятница",
        "Saturday": "Суббота",
        "Sunday": "Воскресенье"
    }.get(tomorrow, tomorrow)
    
    schedule = user_schedule.get(user_id, [])
    tomorrow_schedule = [s for s in schedule if s.get('day') == tomorrow_ru]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Назад к расписанию", callback_data="schedule")
    ]])
    
    if tomorrow_schedule:
        schedule_text = "\n".join([
            f"🕐 {s['time']} - {s['subject']}\n   📍 {s.get('room', 'Аудитория не указана')}\n"
            for s in sorted(tomorrow_schedule, key=lambda x: x.get('time', ''))
        ])
        await callback.message.edit_text(
            f"📅 <b>Расписание на завтра ({tomorrow_ru})</b>\n\n{schedule_text}",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            f"📅 <b>Расписание на завтра ({tomorrow_ru})</b>\n\n"
            "На завтра занятий нет! 🎉",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    await callback.answer()


# Обработчик callback для расписания на всю неделю
@dp.callback_query(F.data == "schedule_week")
async def callback_schedule_week(callback: CallbackQuery):
    user_id = callback.from_user.id
    schedule = user_schedule.get(user_id, [])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Назад к расписанию", callback_data="schedule")
    ]])
    
    if schedule:
        days_order = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        schedule_by_day = {}
        for s in schedule:
            day = s.get('day', '')
            if day not in schedule_by_day:
                schedule_by_day[day] = []
            schedule_by_day[day].append(s)
        
        week_text = ""
        for day in days_order:
            if day in schedule_by_day:
                week_text += f"\n<b>{day}:</b>\n"
                for s in sorted(schedule_by_day[day], key=lambda x: x.get('time', '')):
                    week_text += f"🕐 {s['time']} - {s['subject']} ({s.get('room', '?')})\n"
        
        await callback.message.edit_text(
            f"📅 <b>Расписание на неделю</b>\n{week_text}",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            "📅 <b>Расписание на неделю</b>\n\n"
            "Расписание пусто. Добавь занятия!",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    await callback.answer()


# Обработчик callback для удаления занятия
@dp.callback_query(F.data == "schedule_delete")
async def callback_schedule_delete(callback: CallbackQuery):
    user_id = callback.from_user.id
    schedule = user_schedule.get(user_id, [])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Назад", callback_data="schedule")
    ]])
    
    if not schedule:
        await callback.message.edit_text(
            "🗑️ <b>Удалить занятие</b>\n\n"
            "Расписание пусто. Нечего удалять!",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            "🗑️ <b>Удалить занятие</b>\n\n"
            "Отправь номер занятия для удаления.\n"
            "Или отправь: <code>Все</code> для очистки расписания.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    await callback.answer()


# Обработчик callback для добавления занятия
@dp.callback_query(F.data == "schedule_add")
async def callback_schedule_add(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Назад", callback_data="schedule")
    ]])
    await callback.message.edit_text(
        "➕ <b>Добавить занятие</b>\n\n"
        "Отправь информацию в формате:\n"
        "<code>День недели | Время | Предмет | Аудитория</code>\n\n"
        "Пример:\n"
        "<code>Понедельник | 09:00 | Математика | 201</code>\n\n"
        "Или:\n"
        "<code>Пн | 09:00 | Математика | 201</code>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


# Обработчик callback для домашних заданий
@dp.callback_query(F.data == "homework")
async def callback_homework(callback: CallbackQuery):
    keyboard = get_homework_keyboard()
    await callback.message.edit_text(
        "📝 <b>Домашние задания</b>\n\n"
        "Управляй своими заданиями:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


# Обработчик callback для списка домашних заданий
@dp.callback_query(F.data == "homework_list")
async def callback_homework_list(callback: CallbackQuery):
    user_id = callback.from_user.id
    homework = user_homework.get(user_id, [])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Назад к заданиям", callback_data="homework")
    ]])
    
    if homework:
        homework_text = "\n".join([
            f"{i+1}. 📚 {h['subject']}\n"
            f"   📝 {h['task']}\n"
            f"   📅 Дедлайн: {h.get('deadline', 'Не указан')}\n"
            f"   {'✅ Выполнено' if h.get('done', False) else '⏳ В работе'}\n"
            for i, h in enumerate(homework)
        ])
        await callback.message.edit_text(
            f"📋 <b>Мои домашние задания</b>\n\n{homework_text}",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            "📋 <b>Мои домашние задания</b>\n\n"
            "Заданий пока нет! 🎉\n"
            "Добавь задание через кнопку '➕ Добавить задание'",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    await callback.answer()


# Обработчик callback для добавления домашнего задания
@dp.callback_query(F.data == "homework_add")
async def callback_homework_add(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Назад", callback_data="homework")
    ]])
    await callback.message.edit_text(
        "➕ <b>Добавить домашнее задание</b>\n\n"
        "Отправь информацию в формате:\n"
        "<code>Предмет | Задание | Дедлайн</code>\n\n"
        "Пример:\n"
        "<code>Математика | Решить задачи 1-5 | 25.12.2024</code>\n\n"
        "Или без дедлайна:\n"
        "<code>Физика | Подготовить доклад</code>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


# Обработчик callback для отметки задания выполненным
@dp.callback_query(F.data == "homework_done")
async def callback_homework_done(callback: CallbackQuery):
    user_id = callback.from_user.id
    homework = user_homework.get(user_id, [])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Назад", callback_data="homework")
    ]])
    
    if not homework:
        await callback.message.edit_text(
            "✅ <b>Выполнено</b>\n\n"
            "Заданий нет!",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        undone = [h for h in homework if not h.get('done', False)]
        if undone:
            await callback.message.edit_text(
                "✅ <b>Отметить выполненным</b>\n\n"
                "Отправь номер задания для отметки.",
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            await callback.message.edit_text(
                "✅ <b>Выполнено</b>\n\n"
                "Все задания выполнены! 🎉",
                reply_markup=keyboard,
                parse_mode="HTML"
            )
    await callback.answer()


# Обработчик callback для удаления задания
@dp.callback_query(F.data == "homework_delete")
async def callback_homework_delete(callback: CallbackQuery):
    user_id = callback.from_user.id
    homework = user_homework.get(user_id, [])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Назад", callback_data="homework")
    ]])
    
    if not homework:
        await callback.message.edit_text(
            "🗑️ <b>Удалить задание</b>\n\n"
            "Заданий нет!",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            "🗑️ <b>Удалить задание</b>\n\n"
            "Отправь номер задания для удаления.\n"
            "Или отправь: <code>Все</code> для очистки.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    await callback.answer()


# Обработчик callback для заметок
@dp.callback_query(F.data == "notes")
async def callback_notes(callback: CallbackQuery):
    keyboard = get_notes_keyboard()
    await callback.message.edit_text(
        "📌 <b>Заметки</b>\n\n"
        "Сохраняй важную информацию:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


# Обработчик callback для списка заметок
@dp.callback_query(F.data == "notes_list")
async def callback_notes_list(callback: CallbackQuery):
    user_id = callback.from_user.id
    notes = user_notes.get(user_id, [])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Назад к заметкам", callback_data="notes")
    ]])
    
    if notes:
        notes_text = "\n".join([
            f"{i+1}. 📌 {note['title']}\n   {note['text'][:50]}...\n"
            for i, note in enumerate(notes[:10])  # Показываем первые 10
        ])
        await callback.message.edit_text(
            f"📋 <b>Мои заметки</b>\n\n{notes_text}",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            "📋 <b>Мои заметки</b>\n\n"
            "Заметок пока нет!\n"
            "Создай заметку через кнопку '➕ Новая заметка'",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    await callback.answer()


# Обработчик callback для добавления заметки
@dp.callback_query(F.data == "notes_add")
async def callback_notes_add(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Назад", callback_data="notes")
    ]])
    await callback.message.edit_text(
        "➕ <b>Новая заметка</b>\n\n"
        "Отправь заметку в формате:\n"
        "<code>Заголовок | Текст заметки</code>\n\n"
        "Пример:\n"
        "<code>Важная формула | E = mc²</code>\n\n"
        "Или просто текст (первая строка станет заголовком):\n"
        "<code>Лекция по физике\nСегодня разбирали квантовую механику...</code>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


# Обработчик callback для напоминаний
@dp.callback_query(F.data == "reminders")
async def callback_reminders(callback: CallbackQuery):
    user_id = callback.from_user.id
    reminders = user_reminders.get(user_id, [])
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="➕ Добавить напоминание", callback_data="reminders_add"))
    if reminders:
        keyboard.add(InlineKeyboardButton(text="🗑️ Удалить", callback_data="reminders_delete"))
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu"))
    keyboard.adjust(1, 1, 1)
    
    if reminders:
        reminders_text = "\n".join([
            f"{i+1}. ⏰ {r['text']}\n   📅 {r.get('date', 'Не указано')}\n"
            for i, r in enumerate(reminders)
        ])
        text = f"⏰ <b>Напоминания</b>\n\n{reminders_text}"
    else:
        text = "⏰ <b>Напоминания</b>\n\nНапоминаний пока нет!"
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()


# Обработчик callback для поиска заметок
@dp.callback_query(F.data == "notes_search")
async def callback_notes_search(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Назад", callback_data="notes")
    ]])
    await callback.message.edit_text(
        "🔍 <b>Поиск заметок</b>\n\n"
        "Отправь ключевое слово для поиска:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


# Обработчик callback для удаления заметки
@dp.callback_query(F.data == "notes_delete")
async def callback_notes_delete(callback: CallbackQuery):
    user_id = callback.from_user.id
    notes = user_notes.get(user_id, [])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Назад", callback_data="notes")
    ]])
    
    if not notes:
        await callback.message.edit_text(
            "🗑️ <b>Удалить заметку</b>\n\n"
            "Заметок нет!",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            "🗑️ <b>Удалить заметку</b>\n\n"
            "Отправь номер заметки для удаления.\n"
            "Или отправь: <code>Все</code> для очистки.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    await callback.answer()


# Обработчик callback для добавления напоминания
@dp.callback_query(F.data == "reminders_add")
async def callback_reminders_add(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Назад", callback_data="reminders")
    ]])
    await callback.message.edit_text(
        "➕ <b>Добавить напоминание</b>\n\n"
        "Отправь в формате:\n"
        "<code>Текст напоминания | Дата</code>\n\n"
        "Пример:\n"
        "<code>Экзамен по математике | 25.12.2024</code>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


# Обработчик callback для удаления напоминания
@dp.callback_query(F.data == "reminders_delete")
async def callback_reminders_delete(callback: CallbackQuery):
    user_id = callback.from_user.id
    reminders = user_reminders.get(user_id, [])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Назад", callback_data="reminders")
    ]])
    
    if not reminders:
        await callback.message.edit_text(
            "🗑️ <b>Удалить напоминание</b>\n\n"
            "Напоминаний нет!",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            "🗑️ <b>Удалить напоминание</b>\n\n"
            "Отправь номер напоминания для удаления.\n"
            "Или отправь: <code>Все</code> для очистки.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    await callback.answer()


# Обработчик callback для полезных ссылок
@dp.callback_query(F.data == "links")
async def callback_links(callback: CallbackQuery):
    try:
        keyboard = get_links_keyboard()
        await callback.message.edit_text(
            "📚 <b>Полезные ссылки</b>\n\n"
            "Быстрый доступ к важным ресурсам:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в callback_links: {e}", exc_info=True)
        # Попробуем отправить новое сообщение вместо редактирования
        try:
            keyboard = get_links_keyboard()
            await callback.message.answer(
                "📚 <b>Полезные ссылки</b>\n\n"
                "Быстрый доступ к важным ресурсам:",
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            await callback.answer()
        except Exception as e2:
            logger.error(f"Ошибка при отправке нового сообщения: {e2}")
            await callback.answer("Произошла ошибка", show_alert=True)


# Обработчик callback для информации о боте
@dp.callback_query(F.data == "about")
async def callback_about(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")
    ]])
    await callback.message.edit_text(
        "ℹ️ <b>О боте</b>\n\n"
        "🎓 Бот-помощник для студентов колледжа\n\n"
        "<b>Возможности:</b>\n"
        "• 📅 Управление расписанием\n"
        "• 📝 Отслеживание домашних заданий\n"
        "• 📌 Сохранение заметок\n"
        "• ⏰ Напоминания о важных событиях\n"
        "• 📚 Полезные ссылки\n\n"
        "<b>Версия:</b> 1.0\n"
        "<b>Разработчик:</b> Для колледжа\n\n"
        "Используй /help для списка команд",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


# Обработчик текстовых сообщений для добавления данных
@dp.message(F.text)
async def handle_text(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    # Проверяем, добавляется ли расписание
    if "|" in text and any(word in text.lower() for word in ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье", "пн", "вт", "ср", "чт", "пт", "сб", "вс"]):
        try:
            parts = [p.strip() for p in text.split("|")]
            if len(parts) >= 3:
                day = parts[0]
                time = parts[1]
                subject = parts[2]
                room = parts[3] if len(parts) > 3 else "Не указана"
                
                # Нормализуем день недели
                day_map = {
                    "пн": "Понедельник", "понедельник": "Понедельник",
                    "вт": "Вторник", "вторник": "Вторник",
                    "ср": "Среда", "среда": "Среда",
                    "чт": "Четверг", "четверг": "Четверг",
                    "пт": "Пятница", "пятница": "Пятница",
                    "сб": "Суббота", "суббота": "Суббота",
                    "вс": "Воскресенье", "воскресенье": "Воскресенье"
                }
                day = day_map.get(day.lower(), day)
                
                if user_id not in user_schedule:
                    user_schedule[user_id] = []
                
                user_schedule[user_id].append({
                    "day": day,
                    "time": time,
                    "subject": subject,
                    "room": room
                })
                
                await message.answer(
                    f"✅ Занятие добавлено!\n\n"
                    f"📅 {day}\n"
                    f"🕐 {time}\n"
                    f"📚 {subject}\n"
                    f"📍 {room}",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                        InlineKeyboardButton(text="📅 Расписание", callback_data="schedule")
                    ]])
                )
                return
        except Exception as e:
            pass
    
    # Проверяем, добавляется ли домашнее задание
    if "|" in text and any(word in text.lower() for word in ["математика", "физика", "химия", "история", "литература", "английский", "русский"]):
        try:
            parts = [p.strip() for p in text.split("|")]
            if len(parts) >= 2:
                subject = parts[0]
                task = parts[1]
                deadline = parts[2] if len(parts) > 2 else "Не указан"
                
                if user_id not in user_homework:
                    user_homework[user_id] = []
                
                user_homework[user_id].append({
                    "subject": subject,
                    "task": task,
                    "deadline": deadline,
                    "done": False
                })
                
                await message.answer(
                    f"✅ Задание добавлено!\n\n"
                    f"📚 {subject}\n"
                    f"📝 {task}\n"
                    f"📅 Дедлайн: {deadline}",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                        InlineKeyboardButton(text="📝 Задания", callback_data="homework")
                    ]])
                )
                return
        except Exception as e:
            pass
    
    # Проверяем, добавляется ли заметка
    if "|" in text or "\n" in text:
        try:
            if "|" in text:
                parts = text.split("|", 1)
                title = parts[0].strip()
                note_text = parts[1].strip() if len(parts) > 1 else ""
            else:
                lines = text.split("\n", 1)
                title = lines[0].strip()
                note_text = lines[1].strip() if len(lines) > 1 else title
            
            if user_id not in user_notes:
                user_notes[user_id] = []
            
            user_notes[user_id].append({
                "title": title,
                "text": note_text
            })
            
            await message.answer(
                f"✅ Заметка сохранена!\n\n"
                f"📌 {title}\n"
                f"{note_text[:100]}...",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="📌 Заметки", callback_data="notes")
                ]])
            )
            return
        except Exception as e:
            pass
    
    # Если не распознано, показываем главное меню
    keyboard = get_main_menu()
    await message.answer(
        "Не понял команду. Используй кнопки меню или команду /start",
        reply_markup=keyboard
    )


# Главная функция для polling (локальный запуск)
async def main():
    logger.info("Бот запущен!")
    try:
        # Запускаем polling
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
