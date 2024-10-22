import asyncio
import logging
from sqlalchemy.exc import IntegrityError, OperationalError
from aiogram import Dispatcher, Bot, F
from aiogram.filters import CommandStart
from aiogram.types import Message
import os
from dotenv import load_dotenv
# from sqlmodel.ext.asyncio.session import AsyncSession
from DataBase.models import UsersForBot
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import logging_config

logger_debug = logging.getLogger('log_debug')
logger_error = logging.getLogger('log_error')

load_dotenv()
NAME_DB = os.getenv('NAME_DB')
DATABASE_URL = f"sqlite+aiosqlite:///./{NAME_DB}"
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker (engine, class_= AsyncSession, expire_on_commit=False)

load_dotenv()
TOKEN = os.getenv("TG_TOKEN")
bot = Bot(TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Добрый день. Как вас зовут?")

@dp.message(F.text)
async def user_answer(message: Message):
    model = UsersForBot
    new_record = model(name=message.text, id_chat=str(message.chat.id))
    async with AsyncSessionLocal() as session:
        try:
            model.model_validate(new_record)
            logger_debug.debug("verification is sucess")
        except ValueError as e:
            logger_error.error(f"User validation failed: {e}")
        try:
            session.add(new_record)
            await session.commit()
            await session.refresh(new_record)
            await message.answer("Данные сохранены в базе данных.")
        except (IntegrityError, OperationalError) as e:
            await session.rollback()
            logger_error.error(f"Failed to add user: {e}")
            await message.answer("Невозможно зарегистрировать. Такое имя или пароль уже существуют.")

# async def main():
#     await dp.start_polling(bot)
#
# if __name__ == "__main__":
#     asyncio.run(main())
# Асинхронная функция для запуска бота
async def run_bot():
    await dp.start_polling(bot)