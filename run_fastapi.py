import argparse
import asyncio
import os
from pathlib import Path

import MySQLdb
import aiohttp
import aioschedule
import urllib.parse


from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import KeyboardButton
from langchain.chains import SQLDatabaseSequentialChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain import OpenAI, SQLDatabase, SQLDatabaseChain, PromptTemplate

from sql import SQLConnection


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--telegram_token", help="Telegram bot token", type=str, required=True
    )

    return parser.parse_args()


os.environ['SQL_CONFIG_PATH'] = 'configs/sql_config.json'

args = parse_args()
bot = Bot(token=args.telegram_token) # args.telegram_token)
dispatcher = Dispatcher(bot)


RESTART_KEYBOARD = types.ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton('/start')]], resize_keyboard=True, one_time_keyboard=True
)


@dispatcher.message_handler(commands=["start"])
async def start(message: types.Message):
    await bot.send_chat_action(message.from_user.id, action=types.ChatActions.TYPING)

    await bot.send_message(
        message.from_user.id,
        text="Hello! Ask your question and I'll answer it!",
        reply_markup=RESTART_KEYBOARD
    )

    await asyncio.sleep(1)

@dispatcher.message_handler()
async def handle_message(message: types.Message) -> None:
    async with aiohttp.ClientSession() as session:
        # Example for MESSAGE_ENDPOINT
        async with session.post(
                "http://localhost:8000/api/ask",
                json={"user_id": message.from_user.id, "message": message.text, "attending_provider_id": None},
        ) as response:
            chatbot_response = await response.text()

    await bot.send_chat_action(message.from_user.id, action=types.ChatActions.TYPING)

    await bot.send_message(message.from_user.id, text=chatbot_response)


if __name__ == "__main__":
    executor.start_polling(dispatcher, skip_updates=False)
