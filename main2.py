# -*- coding: utf-8 -*-
import logging
import os

from aiogram import Bot, Dispatcher, executor, types
from state_manager import AiogramStateManager
from state_manager.routes.aiogram import AiogramMainRouter

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
main_state = AiogramMainRouter(dp)
main_state.install()

@main_state.message_handler()
async def home(msg: types.Message, state_manager: AiogramStateManager):
    await msg.answer("go to home2")
    await state_manager.set_next_state("home2")

@main_state.message_handler()
async def home2(msg: types.Message, state_manager: AiogramStateManager):
    await msg.answer("go to home")
    await state_manager.set_next_state("home")

executor.start_polling(dp, skip_updates=True)