from math import ceil
from aiogram import Bot, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from config import yookassa_test_token
from .interface_language.core import phrases
from .main_bot import pending_payments, pending_payments_info
from aiogram.types import LabeledPrice, Message, InlineKeyboardButton, InlineKeyboardMarkup


router = Router()


''' ПОПОЛНЕНИЕ TG STARS '''

async def stars_payment(call: CallbackQuery, bot: Bot, language: str):
    lang = phrases(language)
    user_id = call.from_user.id
    amount_rub = int(call.data.split('_')[0])
    amount_stars = ceil(amount_rub / 1.5)

    link = await bot.create_invoice_link(
        title=f'пополнение на {amount_rub}₽',
        description='description',
        provider_token='',
        currency='XTR',
        prices=[LabeledPrice(label='Оплата', amount=amount_stars)],
        payload='invoice'
    )
    pending_payments[user_id] = amount_rub
    pending_payments_info[user_id] = 'Пополнение баланса — Stars'
    stars_payment_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'{lang.topup_for} {amount_rub}₽ ({amount_stars} ⭐️)', url=link)],
        [InlineKeyboardButton(text=lang.change_amount, callback_data='stars')]
    ])
    await call.message.edit_text(lang.stars_payment, parse_mode='HTML', reply_markup=stars_payment_keyboard)


async def stars_custom(message: Message, bot: Bot, state: FSMContext, language: str):
    user_id = message.from_user.id
    lang = phrases(language)
    
    pending_payments[user_id] = int(pending_payments[user_id])
    amount = pending_payments[user_id]
    pending_payments_info[user_id] = 'Пополнение баланса — Stars'
    
    stars_amount = ceil(amount/1.5)
    custom_stars_link = await bot.create_invoice_link(
        title=f'Пополнение баланса на {amount}₽',
        description=' ',
        provider_token=yookassa_test_token,
        currency='XTR',
        prices=[LabeledPrice(label='Оплата', amount=stars_amount)],
        payload='invoice'
    )
    custom_stars_payment = [
        [InlineKeyboardButton(text=f'{lang.topup_for} {amount}₽ ({stars_amount} ⭐️)', url=custom_stars_link)],
        [InlineKeyboardButton(text=lang.change_amount, callback_data='stars')]
    ]
    custom_stars_keyboard = InlineKeyboardMarkup(inline_keyboard=custom_stars_payment)
    await message.answer(lang.stars_payment, parse_mode='HTML', reply_markup=custom_stars_keyboard)


''' ПОПОЛНЕНИЕ ЮКАССА '''

async def rub_payment(call: CallbackQuery, bot: Bot, language: str):
    # user_id = call.from_user.id
    lang = phrases(language)
    # amount_rub = int(call.data.split('_')[0])
    
    # link = await bot.create_invoice_link(
    #     title=f'Пополнение баланса на {amount_rub}₽',
    #     description=' ',
    #     provider_token=yookassa_test_token,
    #     currency='RUB',
    #     prices=[LabeledPrice(label='Оплата', amount=100*100)],
    #     payload='invoice'
    # )
    # pending_payments[user_id] = amount_rub
    # pending_payments_info[user_id] = 'Пополнение баланса — ЮKassa'
    
    rub_payment_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        # [InlineKeyboardButton(text=f'Пополнить на {amount_rub}₽ 💵', url=link)],
        # [InlineKeyboardButton(text='Изменить сумму', callback_data='YK')]
        [InlineKeyboardButton(text=lang.back, callback_data='YK')]
    ])
    await call.message.edit_text(lang.yookassa_payment, parse_mode='HTML', reply_markup=rub_payment_keyboard)


async def rub_custom(message: Message, bot: Bot, state: FSMContext, language: str):
    user_id = message.from_user.id
    lang = phrases(language)
    pending_payments[user_id] = int(pending_payments[user_id])
    amount = pending_payments[user_id]
    pending_payments_info[user_id] = 'Пополнение баланса — ЮKassa'
    
    custom_rub_link = await bot.create_invoice_link(
        title=f'Пополнение баланса на {amount}₽',
        description=' ',
        provider_token=yookassa_test_token,
        currency='RUB',
        prices=[LabeledPrice(label='Оплата', amount=amount*100)],
        payload='invoice'
    )
    custom_rub_payment = [
        [InlineKeyboardButton(text=f'{lang.topup_for} {amount}₽ 💵', url=custom_rub_link)],
        [InlineKeyboardButton(text=lang.change_amount, callback_data='YK')]
    ]
    custom_rub_keyboard = InlineKeyboardMarkup(inline_keyboard=custom_rub_payment)
    await message.answer(lang.yookassa_payment, parse_mode='HTML', reply_markup=custom_rub_keyboard)
