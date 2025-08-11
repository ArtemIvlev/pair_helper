import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Информация о билде
BUILD_DATE = os.getenv("BUILD_DATE", "unknown")
BUILD_ID = os.getenv("BUILD_ID", "unknown") 
BUILD_MARKER = os.getenv("BUILD_MARKER", "unknown")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher()

# URL веб-приложения
WEBAPP_URL = os.getenv("TELEGRAM_WEBAPP_URL", "http://localhost:3000")


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    # Логируем входящую команду
    logging.info(f"Получена команда /start от пользователя {message.from_user.id} (username: {message.from_user.username})")
    logging.info(f"Полный текст команды: {message.text}")
    
    # Проверяем, есть ли параметр приглашения
    args = message.text.split()
    webapp_url = WEBAPP_URL
    logging.info(f"Все аргументы: {args}")
    
    if len(args) > 1 and args[1].startswith("invite_"):
        invite_code = args[1].replace("invite_", "")
        webapp_url = f"{WEBAPP_URL}?invite={invite_code}"
        logging.info(f"✅ Обнаружен код приглашения: {invite_code}")
        logging.info(f"🔗 URL с приглашением: {webapp_url}")
    else:
        logging.info("❌ Параметр приглашения не найден")
    
    if len(args) > 1 and args[1].startswith("invite_"):
        # Если есть приглашение, показываем специальное сообщение
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="Открыть Пульс ваших отношений",
                web_app=WebAppInfo(url=webapp_url)
            )]
        ])
        
        await message.answer(
            f"🎉 Вы приглашены в пару!\n\n"
            f"Код приглашения: `{invite_code}`\n\n"
            f"Нажмите кнопку ниже, чтобы открыть приложение и зарегистрироваться.\n"
            f"После регистрации вы автоматически станете партнерами!",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    else:
        # Если нет приглашения, показываем основное меню
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="Открыть Пульс ваших отношений",
                web_app=WebAppInfo(url=webapp_url)
            )]
        ])
        
        await message.answer(
            "Привет! 👋\n\n"
            "Добро пожаловать в Пульс ваших отношений - приложение для пар!\n\n"
            "Здесь вы можете:\n"
            "• Отвечать на ежедневные вопросы\n"
            "• Поделиться своим настроением\n"
            "• Пройти викторину о знании друг друга\n\n"
            "Нажмите кнопку ниже, чтобы открыть приложение:",
            reply_markup=keyboard
        )


@dp.message(Command("invite"))
async def cmd_invite(message: types.Message):
    """Обработчик команды /invite"""
    import httpx
    
    logging.info(f"Получена команда /invite от пользователя {message.from_user.id} (username: {message.from_user.username})")
    
    try:
        # Генерируем приглашение через API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{os.getenv('API_BASE_URL', 'http://192.168.2.228:8000')}/api/v1/invitations/generate",
                params={"inviter_telegram_id": message.from_user.id}
            )
            
            if response.status_code == 200:
                invitation_data = response.json()
                invite_code = invitation_data["code"]
                invite_link = f"https://t.me/PulseOfPair_Bot/pulse_of_pair?startapp=invite_{invite_code}"
                
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(
                        text="Открыть Пульс ваших отношений",
                        web_app=WebAppInfo(url=WEBAPP_URL)
                    )]
                ])
                
                await message.answer(
                    f"🎉 Ваша ссылка для приглашения готова!\n\n"
                    f"Отправьте эту ссылку вашему партнеру:\n"
                    f"`{invite_link}`\n\n"
                    f"Ссылка действительна 7 дней.",
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
            else:
                await message.answer(
                    "❌ Ошибка при создании приглашения. Убедитесь, что вы зарегистрированы в приложении."
                )
                
    except Exception as e:
        logging.error(f"Ошибка при создании приглашения: {e}")
        await message.answer("❌ Произошла ошибка при создании приглашения.")


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = """
🤖 Пульс ваших отношений Bot - Помощник для пар

📋 Доступные команды:
/start - Запустить приложение
/invite - Создать приглашение для партнёра
/help - Показать эту справку

💡 Основные функции:
• Ежедневные вопросы для пар
• Поделиться своим настроением
• Викторина о знании друг друга

🔗 Откройте приложение командой /start
    """
    
    await message.answer(help_text)


@dp.message(Command("menu"))
async def cmd_menu(message: types.Message):
    """Обработчик команды /menu"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Открыть Пульс ваших отношений",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])
    
    await message.answer(
        "Главное меню Пульс ваших отношений:",
        reply_markup=keyboard
    )


@dp.message(Command("open"))
async def cmd_open(message: types.Message):
    """Обработчик команды /open"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Открыть Пульс ваших отношений",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])
    
    await message.answer(
        "Открываю Пульс ваших отношений...",
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
            text="Открыть Пульс ваших отношений",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])
    
    await message.answer(
        "Используйте команду /start для запуска приложения или /help для справки.",
        reply_markup=keyboard
    )


async def main():
    """Основная функция"""
    logger.info("🤖 Пульс ваших отношений Bot запускается...")
    logger.info(f"📦 Build ID: {BUILD_ID}")
    logger.info(f"📅 Build Date: {BUILD_DATE}")
    logger.info(f"🏷️  {BUILD_MARKER}")
    
    # Проверяем наличие токена
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        logger.error("TELEGRAM_BOT_TOKEN не установлен!")
        return
    
    # Запускаем бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
