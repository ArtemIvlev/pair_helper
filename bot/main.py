import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher()

# URL веб-приложения
WEBAPP_URL = os.getenv("TELEGRAM_WEBAPP_URL", "http://localhost:3000")


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Открыть Pair Helper",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])
    
    await message.answer(
        "Привет! 👋\n\n"
        "Добро пожаловать в Pair Helper - приложение для пар!\n\n"
        "Здесь вы можете:\n"
        "• Отвечать на ежедневные вопросы\n"
        "• Отмечать настроение дня\n"
        "• Вести общий календарь\n"
        "• Создавать ритуалы\n"
        "• И многое другое!\n\n"
        "Нажмите кнопку ниже, чтобы открыть приложение:",
        reply_markup=keyboard
    )


@dp.message(Command("invite"))
async def cmd_invite(message: types.Message):
    """Обработчик команды /invite"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Открыть Pair Helper",
            web_app=WebAppInfo(url=f"{WEBAPP_URL}/invite")
        )]
    ])
    
    await message.answer(
        "Создать приглашение для партнёра:\n\n"
        "Откройте приложение, чтобы сгенерировать код-приглашение.",
        reply_markup=keyboard
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = """
🤖 Pair Helper Bot - Помощник для пар

📋 Доступные команды:
/start - Запустить приложение
/invite - Создать приглашение для партнёра
/help - Показать эту справку

💡 Основные функции:
• Ежедневные вопросы для пар
• Отслеживание настроения
• Общий календарь событий
• Ритуалы и привычки
• Признания и благодарности

🔗 Откройте приложение командой /start
    """
    
    await message.answer(help_text)


@dp.message(Command("menu"))
async def cmd_menu(message: types.Message):
    """Обработчик команды /menu"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Открыть Pair Helper",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])
    
    await message.answer(
        "Главное меню Pair Helper:",
        reply_markup=keyboard
    )


@dp.message(Command("open"))
async def cmd_open(message: types.Message):
    """Обработчик команды /open"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Открыть Pair Helper",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])
    
    await message.answer(
        "Открываю Pair Helper...",
        reply_markup=keyboard
    )


@dp.message()
async def echo_message(message: types.Message):
    """Обработчик всех остальных сообщений"""
    # В групповых чатах бот молчит по умолчанию
    if message.chat.type in ["group", "supergroup"]:
        return
    
    # В личных сообщениях предлагаем открыть приложение
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Открыть Pair Helper",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])
    
    await message.answer(
        "Используйте команду /start для запуска приложения или /help для справки.",
        reply_markup=keyboard
    )


async def main():
    """Основная функция"""
    logging.info("Запуск Pair Helper Bot...")
    
    # Проверяем наличие токена
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        logging.error("TELEGRAM_BOT_TOKEN не установлен!")
        return
    
    # Запускаем бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
