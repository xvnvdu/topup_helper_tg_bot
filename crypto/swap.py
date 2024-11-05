from aiogram.types import CallbackQuery

from .amount_handler import choose_amount
from .main_crypto import pending_user_balance

from bot.main_bot import users_data_dict
from bot.bot_buttons import swap_choice_keyboard, swap_second_choice_keyboard, crypto_amount_swap


async def swap_choice(call: CallbackQuery, chain: str):
    await call.message.edit_text('<b>♻️ Выберите монету, которую хотите обменять:</b>', 
                                 parse_mode='HTML', reply_markup=swap_choice_keyboard(chain))


async def swap_second_choice(call: CallbackQuery, chain: str, currency: str):
    await call.message.edit_text('<b>♻️ Выберите монету, на которую хотите совершить обмен:</b>',
                                 parse_mode='HTML', reply_markup=swap_second_choice_keyboard(chain, currency))


async def amount_to_swap(call: CallbackQuery, chain: str, cur1: str, cur2: str):
	pass

 