"""
This is a echo bot.
It echoes any incoming text messages.
"""

import logging
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from otp_auth import (otpCode, otpVerify)

API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


# Master
master = [
    # '822518127',
]


# States
class Aiocatz(StatesGroup):
    auth = State()
    passed = State()
# end class

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")
# end def



@dp.message_handler(Command('otp'))
async def get_otp(message: types.Message):
    otp = otpCode()
    await message.reply(otp)
# end def



@dp.message_handler(Command('new'))
async def greet(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)
    if str(message.chat.id) not in master :
        await message.answer('Sorry you\'re not my master, contact my master to use our services. @AncientCatz')
        await message.answer('Enter your OTP Code')
        await Aiocatz.auth.set()
    else:
        await message.answer('Welcome dear master')
        await Aiocatz.passed.set()
    # end if
# end def

@dp.message_handler(lambda message: not message.text.isdigit(), state=Aiocatz.auth)
async def otp_verify_invalid(message: types.Message):
    await message.reply('OTP Code gotta be a number (digits only)')
# end def

@dp.message_handler(lambda message: message.text.isdigit(), state=Aiocatz.auth)
async def otp_verify(message: types.Message, state = FSMContext):
    otp = message.text
    if otpVerify(otp) == False:
        await message.reply('Invalid OTP Code')
    elif otpVerify(otp) == True:
        await message.answer('Authenticated, you can use our service for one session')
        await Aiocatz.next()
    # end if
# end def

@dp.message_handler(state=Aiocatz.passed)
async def passed(message: types.Message, state = FSMContext):
    await message.answer('Coming soon!')
    await state.finish()
# end def


if __name__ == '__main__':
    print("Telegram bot online!")
    executor.start_polling(dp, skip_updates=True)