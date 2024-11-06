from aiogram.fsm.context import FSMContext
from uniswap import Uniswap
from aiogram.types import CallbackQuery, Message

from .amount_handler import choose_amount
from .models import Networks, Currencies
from .main_crypto import (pending_user_balance, ok_to_swap, pending_user_balance_in_usd, pending_chain_swap, pending_trx_id, 
                          pending_currency_to_swap, pending_crypto_swap_amount, pending_swap_amount_in_usd, pending_currency_swap_to)

from logger import logger
from bot.main_bot import users_data_dict, id_generator
from bot.bot_buttons import swap_choice_keyboard, swap_second_choice_keyboard, crypto_amount_swap, change_swap_amount, confirm_swap_keyboard


async def swap_choice(call: CallbackQuery, chain: str):
    user_id = call.from_user.id
    ok_to_swap[user_id] = False
    await call.message.edit_text('<b>♻️ Выберите монету, которую хотите обменять:</b>', 
                                 parse_mode='HTML', reply_markup=swap_choice_keyboard(chain))


async def swap_second_choice(call: CallbackQuery, chain: str, currency: str):
    user_id = call.from_user.id
    ok_to_swap[user_id] = False
    await call.message.edit_text('<b>♻️ Выберите монету, на которую хотите совершить обмен:</b>',
                                 parse_mode='HTML', reply_markup=swap_second_choice_keyboard(chain, currency))


async def amount_to_swap(call: CallbackQuery, chain: str, cur1: str, cur2: str):
	user_id = call.from_user.id
	user_data = users_data_dict[user_id]
	ok_to_swap[user_id] = False
 
	pending_currency_swap_to[user_id] = cur2
 
	wallet_address = user_data['Wallet_address']

	text = await choose_amount(user_id, chain, cur1, wallet_address, 'swap')
    
	await call.message.edit_text(text, parse_mode='HTML', reply_markup=crypto_amount_swap(chain, cur1, cur2))
 
 
async def choose_amount_to_swap(call: CallbackQuery):
	user_id = call.from_user.id
    
	percent = int(str(call.data).split('_')[0])
	chain = str(call.data).split('_')[3]
	cur1 = str(call.data).split('_')[4]
	cur2 = str(call.data).split('_')[5]
 
	balance = pending_user_balance[user_id]
	usd_balance = float(pending_user_balance_in_usd[user_id])
	coin_price = Currencies.currencies[chain][cur1].return_price
 
	trx_id = await id_generator()
	pending_trx_id[user_id] = trx_id
 
	ok_to_swap[user_id] = False

	user_amount = float(balance) * percent / 100
	amount_in_usd = usd_balance * percent / 100

	if amount_in_usd < 0.01:
		await call.message.edit_text(f'<strong>⚠️ Слишком маленькое значение.</strong>\n'
				f'<i>Сумма для вывода должна быть эквивалентна не менее 0.01$</i>', 
				parse_mode='HTML', reply_markup=change_swap_amount(chain, cur1, cur2))
		return

	if cur1 == Networks.networks[chain].coin_symbol:
		if percent == 100:
			withdraw_in_usd = usd_balance * (1 - 1 / (usd_balance * 100))
			user_amount = balance / usd_balance * withdraw_in_usd

	logger.info(f'Пользователь {user_id} выбрал {percent}% для свапа. Обмен {cur1} на {cur2}.')
 
	ok_to_swap[user_id] = True
 
	text = f'Обмен <code>{cur1}</code> на <code>{cur2}</code>\nСумма: <code>{user_amount} {cur1}</code>'
	if coin_price is not None:
		text += f' <i>({amount_in_usd}$)</i>'
  
	await call.message.edit_text(text, parse_mode='HTML', reply_markup=confirm_swap_keyboard(trx_id, chain, cur1, cur2))

 
async def input_swap_amount(message: Message, state: FSMContext):
	user_id = message.from_user.id
	user_amount = message.text.replace(',', '.')	
	balance = pending_user_balance[user_id]

	ok_to_swap[user_id] = False
 
	trx_id = await id_generator()
	pending_trx_id[user_id] = trx_id
 
	chain = pending_chain_swap[user_id]
	cur1 = pending_currency_to_swap[user_id]
	cur2 = pending_currency_swap_to[user_id]
	pending_crypto_swap_amount[user_id] = user_amount
	coin_price = Currencies.currencies[chain][cur1].return_price

	try: 
		await message.delete()
		amount = f'{(float(user_amount)):.12f}'.rstrip('0').rstrip('.')
		pending_crypto_swap_amount[user_id] = amount

		if float(amount) <= 0:
			logger.warning(f'Пользователь {user_id} ввел некорректную сумму во время свапа: {amount}.')
			await message.answer('<strong>⚠️ Сумма введена некорректно.</strong>\n<i>Нельзя обменять '
									'сумму отрицательную или равную нулю.</i>', parse_mode='HTML',
									reply_markup=change_swap_amount(chain, cur1, cur2))
			await state.clear()

		elif float(balance) < float(amount):
			logger.warning(f'У пользователя {user_id} недостаточно средств для свапа: {balance} - {amount}.')
			await message.answer('<strong>⚠️ У вас не хватает средств для обмена.</strong>\n<i>Уменьшите сумму '
									'или пополните баланс.</i>', parse_mode='HTML', reply_markup=change_swap_amount(chain, cur1, cur2))
			await state.clear()
	
		else:
			ok_to_swap[user_id] = True
			text = f'Обмен <code>{cur1}</code> на <code>{cur2}</code>\nСумма: <code>{user_amount} {cur1}</code>'
   
			if coin_price is not None:
				coin_price = await coin_price(cur1)
				usd_value = round(float(amount) * coin_price, 2)
				pending_swap_amount_in_usd[user_id] = usd_value
				text += f' <i>({usd_value}$)</i>'
    
				if usd_value < 0.01:
					logger.warning(f'Пользователь {user_id} попытался обменять менее 0.01$: {usd_value}.')
			
					await message.answer('<strong>⚠️ Слишком маленькое значение.</strong>\n'
							'<i>Попробуйте увеличить сумму для обмена, она должна быть эквивалентна не менее 0.01$</i>', 
							parse_mode='HTML', reply_markup=change_swap_amount(chain, cur1, cur2))
					await state.clear()
					return
			else:
				if float(amount) < 0.01:
					logger.warning(f'Пользователь {user_id} попытался обменять менее 0.01$: {amount}.')
		
					await message.answer('<strong>⚠️ Слишком маленькое значение.</strong>\n'
							'<i>Попробуйте увеличить сумму для обмена, она должна быть эквивалентна не менее 0.01$</i>', 
							parse_mode='HTML', reply_markup=change_swap_amount(chain, cur1, cur2))
					await state.clear()
					return

			await message.answer(text, parse_mode='HTML', reply_markup=confirm_swap_keyboard(trx_id, chain, cur1, cur2))
   
	except ValueError:
		logger.warning(f'Пользователь {user_id} ввел некорректную сумму во время свапа.')
		await message.answer('<strong>⚠️ Сумма введена некорректно, попробуйте еще раз.</strong>', 
                             parse_mode='HTML', reply_markup=change_swap_amount(chain, cur1, cur2))
		await state.clear()
  

async def swap_confirmed(call: CallbackQuery):
    await call.message.edit_text('Произошел свап')  
  

''' ПРОВЕРКА НА УСТАРЕВШИЕ ТРАНЗАКЦИИ '''

async def try_to_swap(call: CallbackQuery):
    user_id = call.from_user.id
    
    if ok_to_swap[user_id]:
        if f'{call.data}'.split('_')[3] == pending_trx_id[user_id]:
            await swap_confirmed(call)
        else:
            await swap_declined(call)
    else:
        await swap_declined(call)


''' УСТАРЕВШАЯ ТРАНЗАКЦИЯ '''

async def swap_declined(call: CallbackQuery):
    user_id = call.from_user.id
    
    logger.warning(f'Пользователь {user_id} воспользовался устаревшей транзакцией для свапа.')
    await  call.message.edit_text('⛔️ <strong>Данные транзакции устарели!</strong>\n'
                                          '<i>Попробуйте инициировать новую.</i>', parse_mode='HTML')