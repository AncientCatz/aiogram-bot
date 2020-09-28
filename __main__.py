# -*- coding: utf-8 -*-
"""
This is a echo bot.
It echoes any incoming text messages.
"""

import itertools
import logging
import os
import time

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from otp_auth import (otpCode, otpVerify)
from loading_bar import progress
from wp_plus import warp_plus

API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


# Master
master = [
    '822518127',
]


# States
class Aiocatz(StatesGroup):
    auth = State()
    passed = State()
    warp = State()
# end class

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm Aiocatz!\nPowered by aiogram.")
# end def



@dp.message_handler(commands=['otp'])
async def get_otp(message: types.Message):
    otp = otpCode()
    if str(message.chat.id) not in master :
        await message.answer('Sorry you\'re not my master, you\'re not allowed to use this command')
    else:
        await message.reply(
            '%s' % otp
        )
    # end if
# end def



@dp.message_handler(commands=['give'])
async def give(message: types.Message):
    id = message.get_args()
    otp = otpCode()
    if str(message.chat.id) not in master :
        await message.answer('Sorry you\'re not my master, you\'re not allowed to use this command')
    else:
        await bot.send_message(
            id, '%s' % otp
        )
    # end if
# end def



@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    # end if

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled. Send /new to start a new session', reply_markup=types.ReplyKeyboardRemove())
# end def



@dp.message_handler(Command('new'))
async def greet(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)
    if str(message.chat.id) not in master :
        await Aiocatz.auth.set()

        await message.answer('Sorry you\'re not my master, send your ID:`{message.chat.id}` to my master to use our services. @AncientCatz')
        await message.answer(
            'Enter your OTP Code'
            'To cancel send /cancel'
        )
    else:
        await Aiocatz.passed.set()

        keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
        text_and_data = (
            ('WARP+ CloudFlare', 'warp'),
        )
        row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
        keyboard_markup.row(*row_btns)
        await message.answer('Welcome dear master', reply_markup=keyboard_markup)
    # end if
# end def

@dp.message_handler(lambda message: not message.text.isdigit(), state=Aiocatz.auth)
async def otp_verify_invalid(message: types.Message):
    await message.reply(
        'OTP Code gotta be a number (digits only).\n'
        'To cancel send /cancel.'
    )
# end def


@dp.message_handler(lambda message: message.text.isdigit(), state=Aiocatz.auth)
async def otp_verify(message: types.Message, state = FSMContext):
    otp = message.text
    if otpVerify(otp) == False:
        await message.reply(
            'Invalid OTP Code'
            'To cancel send /cancel'
        )
    elif otpVerify(otp) == True:
        await Aiocatz.next()

        keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
        text_and_data = (
            ('WARP+ CloudFlare', 'warp'),
        )
        row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
        keyboard_markup.row(*row_btns)
        await message.answer('Authenticated, you can use our service for one session.', reply_markup=keyboard_markup)
    # end if
# end def


@dp.callback_query_handler(state=Aiocatz.passed, text='warp')  # if cb.data == 'warp'
async def inline_kb_answer_callback_handler(query: types.CallbackQuery, state = FSMContext):
    answer_data = query.data
    # always answer callback queries, even if you have nothing to say
    await query.answer(f'Processing…')

    if answer_data == 'warp':
        text = 'Enter your ID'
        await Aiocatz.next()
    else:
        text = f'Unexpected callback data {answer_data!r}!'

    await bot.send_message(query.from_user.id, text)
# end def


@dp.message_handler(state=Aiocatz.warp)
async def warp(message: types.Message, state: FSMContext):
    referrer = message.text.strip()
    msg = await message.reply('Preparing…')
    i = 0
    for _ in itertools.repeat(None, 5):
        if i != 0:
            i = 0
        # end if
        g = 0
        b = 0
        ui = progress(i, 10, status='Processing…')
        while i <= 10:
            await msg.edit_text(f'Result: {g} Good {b} Bad\n{ui}')
            time.sleep(1)
            i += 1
        # end while
        if i != 0:
            i = 0
        # end if
        cd = 18
        if cd != 18:
            cd = 18
        # end if
        while i <= 18:
            result = warp_plus(referrer)
            if result == 200:
                g = g + 1
                cd = cd - 1
                await msg.edit_text(f'Result: {g} Good {b} Bad\nAfter {cd} seconds, a new request will be sent.')
                time.sleep(1)
            else:
                b = b + 1
                await msg.edit_text('Result: {g} Good {b} Bad\nError when connecting to server.')
        i = 0
            # end if
        # end while
    # end for
# end def
        


@dp.message_handler(commands=['loading'])
async def edit(message: types.Message):
    i = int(message.get_args().split()[:1][0])
    total = int(message.get_args().split()[1:][0])
    msg = await message.answer('Processing…')
    while i <= total:
        await msg.edit_text(progress(i, total, status='Loading...'))
        time.sleep(0.2)
        i += 1



@dp.message_handler(commands='inline_kb')
async def start_cmd_handler(message: types.Message):
    keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
    # default row_width is 3, so here we can omit it actually
    # kept for clearness

    text_and_data = (
        ('Yes!', 'yes'),
        ('No!', 'no'),
    )
    # in real life for the callback_data the callback data factory should be used
    # here the raw string is used for the simplicity
    row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)

    keyboard_markup.row(*row_btns)
    keyboard_markup.add(
        # url buttons have no callback data
        types.InlineKeyboardButton('aiogram source', url='https://github.com/aiogram/aiogram'),
    )

    await message.reply("Hi!\nDo you love aiogram?", reply_markup=keyboard_markup)

# Use multiple registrators. Handler will execute when one of the filters is OK
@dp.callback_query_handler(text='no')  # if cb.data == 'no'
@dp.callback_query_handler(text='yes')  # if cb.data == 'yes'
async def inline_kb_answer_callback_handler(query: types.CallbackQuery):
    answer_data = query.data
    # always answer callback queries, even if you have nothing to say
    await query.answer(f'You answered with {answer_data!r}')

    if answer_data == 'yes':
        text = 'Great, me too!'
    elif answer_data == 'no':
        text = 'Oh no...Why so?'
    else:
        text = f'Unexpected callback data {answer_data!r}!'

    await bot.send_message(query.from_user.id, text)

if __name__ == '__main__':
    print("Telegram bot online!")
    executor.start_polling(dp, skip_updates=True)