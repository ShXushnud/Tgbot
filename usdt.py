import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

# Настройки
TOKEN = "8144381126:AAEPKV-zIxpgn8CLVKsdcDHaLMYezHrTxS8"
ADMIN_CHAT_ID = "4667403126"
ADMIN_USERNAME = "OnCrystal"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

# Подключение к базе данных
conn = sqlite3.connect("referrals.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        balance REAL DEFAULT 0,
        referrer_id INTEGER,
        referrals INTEGER DEFAULT 0,
        second_level_refs INTEGER DEFAULT 0,
        language TEXT DEFAULT 'ru'
    )
""")
conn.commit()

# Клавиатура выбора языка
lang_kb = ReplyKeyboardMarkup(resize_keyboard=True)
lang_kb.add("🇷🇺 Русский", "🇬🇧 English")

# Основная клавиатура
main_kb = {
    "ru": ReplyKeyboardMarkup(resize_keyboard=True).add(
        "📎 Моя реферальная ссылка", "💰 Баланс"
    ).add(
        "📤 Запросить вывод", "📊 Статистика"
    ).add(
        "🎁 Бонусы", "🏆 Топ-рефоводов", "💼 Задания за деньги"
    ),
    "en": ReplyKeyboardMarkup(resize_keyboard=True).add(
        "📎 My Referral Link", "💰 Balance"
    ).add(
        "📤 Request Withdrawal", "📊 Statistics"
    ).add(
        "🎁 Bonuses", "🏆 Top Referrers", "💼 Paid Tasks"
    )
}

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username

    cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()
        await message.answer("Выберите язык / Choose your language", reply_markup=lang_kb)
    else:
        lang = user[0] if user[0] else "ru"
        await message.answer(
            "Привет! Вот твоя панель управления:" if lang == "ru" else "Hello! Here is your control panel:",
            reply_markup=main_kb[lang]
        )

    await bot.send_message(ADMIN_CHAT_ID, f"Новый пользователь: @{username} (ID: {user_id})")

@dp.message_handler(lambda message: message.text in ["🇷🇺 Русский", "🇬🇧 English"])
async def set_language(message: types.Message):
    user_id = message.from_user.id
    lang = "ru" if message.text == "🇷🇺 Русский" else "en"
    
    cursor.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang, user_id))
    conn.commit()
    
    await message.answer(
        "Язык установлен: Русский" if lang == "ru" else "Language set: English",
        reply_markup=main_kb[lang]
    )

@dp.message_handler()
async def log_all_messages(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Без имени"
    
    await bot.send_message(ADMIN_CHAT_ID, f"🔔 {username} ({user_id}) отправил сообщение: {message.text}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
