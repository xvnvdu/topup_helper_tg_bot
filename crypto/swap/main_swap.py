import requests

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from web3 import Web3

from .api_responses import GetData
from config import one_inch_token
from ..amount_handler import choose_amount
from ..models import Networks, Currencies
from ..main_crypto import (pending_user_balance, ok_to_swap, pending_user_balance_in_usd, pending_chain_swap, pending_trx_id, 
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
	cur1_price = Currencies.currencies[chain][cur1].return_price
	cur2_price = Currencies.currencies[chain][cur2].return_price
 
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
 
	text = (f'<b>🌐 Сеть свапа:</b> <code>{chain}</code>\n'
         f'<b>💸 Продаете:</b> <code>{user_amount} {cur1}</code>')
	if cur1_price is not None:
		text += f' <i>({round(amount_in_usd, 2)}$)</i>'
	text += (f'\n<b>💰 Покупаете:</b> <code>*неизвестно* {cur2}</code>')   # НАХОДИТЬ СТОИМОСТЬ ЧЕРЕЗ API
	if cur2_price is not None:
		text += f' <i>({round(amount_in_usd, 2)}$)</i>'                    # ИЗМЕНИТЬ НА СТОИМОСТЬ ВТОРОГО АКТИВА
	text += '\n\n<b>Подтверждаете?</b>'	
 
	await call.message.edit_text(text, parse_mode='HTML', reply_markup=confirm_swap_keyboard(trx_id, chain, cur1, cur2))

 
async def input_swap_amount(message: Message, state: FSMContext):
	user_id = message.from_user.id
	user_data = users_data_dict[user_id]
	user_amount = message.text.replace(',', '.')	
	balance = pending_user_balance[user_id]

	await message.delete()
	loading = await message.answer('🕓 <strong>Рассчитываю комиссию.</strong>\n'
                                '<i>Это может занять некоторое время...</i>', parse_mode='HTML')

	ok_to_swap[user_id] = False
 
	trx_id = await id_generator()
	pending_trx_id[user_id] = trx_id
 
	address = user_data['Wallet_address']
	chain = pending_chain_swap[user_id]
	cur1 = pending_currency_to_swap[user_id]
	cur2 = pending_currency_swap_to[user_id]
	pending_crypto_swap_amount[user_id] = user_amount
 
	contract1 = Currencies.currencies[chain][cur1].contract
	contract2 = Currencies.currencies[chain][cur2].contract

	decimals1 = Currencies.currencies[chain][cur1].decimals
	decimals2 = Currencies.currencies[chain][cur2].decimals
 
	cur1_price = Currencies.currencies[chain][cur1].return_price
	cur2_price = Currencies.currencies[chain][cur2].return_price

	rpc = Networks.networks[chain].rpc
	web3 = Web3(Web3.HTTPProvider(rpc))
	chain_id = Networks.networks[chain].chain_id
	native_currency = Networks.networks[chain].coin_symbol
	user_amount_wei = int(float(user_amount) * decimals1)
	
	if contract1 is None:
		if chain != 'Polygon':
			contract1 = '0x0000000000000000000000000000000000000000'
		else:
			contract1 = '0x0000000000000000000000000000000000001010'
	if contract2 is None:
		if chain != 'Polygon':
			contract2 = '0x0000000000000000000000000000000000000000'
		else:
			contract2 = '0x0000000000000000000000000000000000001010'
 
	# allowance = await GetData.check_allowance(chain_id, contract1, address)
	output_amount, gas = await GetData.get_output_amount(chain_id, contract1, contract2, user_amount_wei, decimals2)
	gas_price = web3.from_wei(gas, 'gwei')
	logger.info(output_amount)
	logger.info(gas)
	try: 
		amount = f'{(float(user_amount)):.12f}'.rstrip('0').rstrip('.')
		pending_crypto_swap_amount[user_id] = amount

		if float(amount) <= 0:
			logger.warning(f'Пользователь {user_id} ввел некорректную сумму во время свапа: {amount}.')
			await loading.edit_text('<strong>⚠️ Сумма введена некорректно.</strong>\n<i>Нельзя обменять '
									'сумму отрицательную или равную нулю.</i>', parse_mode='HTML',
									reply_markup=change_swap_amount(chain, cur1, cur2))
			await state.clear()

		elif float(balance) < float(amount):
			logger.warning(f'У пользователя {user_id} недостаточно средств для свапа: {balance} - {amount}.')
			await loading.edit_text('<strong>⚠️ У вас не хватает средств для обмена.</strong>\n<i>Уменьшите сумму '
									'или пополните баланс.</i>', parse_mode='HTML', reply_markup=change_swap_amount(chain, cur1, cur2))
			await state.clear()
	
		else:
			ok_to_swap[user_id] = True

			if cur2_price is not None:
				cur2_price = await cur2_price(cur2)
				cur2_usd_value = round(float(output_amount) * cur2_price, 2) # ЗАМЕНИТЬ AMOUNT НА КОЛИЧЕСТВО
   
			if cur1_price is not None:
				cur1_price = await cur1_price(cur1)
				cur1_usd_value = round(float(amount) * cur1_price, 2)
				pending_swap_amount_in_usd[user_id] = cur1_usd_value

    
				if cur1_usd_value < 0.01:
					logger.warning(f'Пользователь {user_id} попытался обменять менее 0.01$: {cur1_usd_value}.')
			
					await loading.edit_text('<strong>⚠️ Слишком маленькое значение.</strong>\n'
							'<i>Попробуйте увеличить сумму для обмена, она должна быть эквивалентна не менее 0.01$</i>', 
							parse_mode='HTML', reply_markup=change_swap_amount(chain, cur1, cur2))
					await state.clear()
					return
			else:
				if float(amount) < 0.01:
					logger.warning(f'Пользователь {user_id} попытался обменять менее 0.01$: {amount}.')
		
					await loading.edit_text('<strong>⚠️ Слишком маленькое значение.</strong>\n'
							'<i>Попробуйте увеличить сумму для обмена, она должна быть эквивалентна не менее 0.01$</i>', 
							parse_mode='HTML', reply_markup=change_swap_amount(chain, cur1, cur2))
					await state.clear()
					return

			text = (f'<b>🌐 Сеть свапа:</b> <code>{chain}</code>\n'
         			f'<b>💸 Продаете:</b> <code>{user_amount} {cur1}</code>')
			if cur1_price is not None:
				text += f' <i>({cur1_usd_value}$)</i>'
			text += (f'\n<b>💰 Покупаете:</b> <code>{output_amount} {cur2}</code>')
			if cur2_price is not None:
				text += f' <i>({cur2_usd_value}$)</i>'
			text += (f'\n\n<b>⛽️ Цена газа: <code>{f"{gas_price:.5f}".rstrip("0").rstrip(".")} GWei</code>\n'
					#  f'💳 Комиссия: <code>{f"{trx_fee:.9f}".rstrip("0")} {native_currency}</code></strong> '
					#  f'<i>({f"{trx_fee_usd:.5f}".rstrip("0")}$)</i>\n\n'
            		 f'Подтверждаете?</b>')

			await loading.edit_text(text, parse_mode='HTML', reply_markup=confirm_swap_keyboard(trx_id, chain, cur1, cur2))
   
	except ValueError:
		logger.warning(f'Пользователь {user_id} ввел некорректную сумму во время свапа.')
		await loading.edit_text('<strong>⚠️ Сумма введена некорректно, попробуйте еще раз.</strong>', 
                             parse_mode='HTML', reply_markup=change_swap_amount(chain, cur1, cur2))
		await state.clear()
  

async def swap_confirmed(call: CallbackQuery, message: Message, user_id: int, chain: str, contract1: str, contract2: str, amount: int, web3: None):
	user_data = users_data_dict[user_id]

# 	if call:
# 		loading = await call.message.edit_text('🕓 <strong>Рассчитываю комиссию.</strong>\n'
#                                 '<i>Это может занять некоторое время...</i>', parse_mode='HTML')
# 	if message:
# 		loading = await message.answer('🕓 <strong>Рассчитываю комиссию.</strong>\n'
#                                 '<i>Это может занять некоторое время...</i>', parse_mode='HTML')


# 	chain_id = Networks.networks[chain].chain_id
# 	rpc = Networks.networks[chain].rpc
# 	headers = { "Authorization": f"Bearer {one_inch_token}", "accept": "application/json" }
# 	address = user_data['Wallet_address']
# 	pk = user_data['Private_key']
 
# 	swap = {
# 		'src': contract1,
# 		'dst': contract2,
# 		'amount': amount,
# 		'from': address,
# 		'slippage': 1,
# 		'disableEstimate': False, 
#     	'allowPartialFill': False,
# }
 
	# try:
	# 	estimate_gas = web3.eth.estimate_gas(swap, from_address=address)
	# 	swap['gas'] = estimate_gas
	# except Exception as e:
	# 		await loading.edit_text('<strong>⚠️ Недостаточно средств для оплаты комиссии.</strong>\n'
	# 					'<i>Уменьшите сумму вывода или попробуйте позже.</i>', 
	# 							parse_mode='HTML', reply_markup=None)
	# 		logger.warning(f'У пользователя {user_id} недостаточно средств для оплаты комиссии: Сеть - {chain} | Ошибка - {e}.')
   

	await call.message.edit_text('Произошел свап')  
  

# async def estimate_gas(contract1: str, contract2: str, amount: int, address: str, ):
#     swap = {
# 		'src': contract1,
# 		'dst': contract2,
# 		'amount': amount,
# 		'from': address,
# 		'slippage': 1,
# 		'disableEstimate': False, 
#     	'allowPartialFill': False,
# }
    
#     try:
#         estimate_gas = web3.eth.estimate_gas(swap, from_address=address)
#         swap['gas'] = estimate_gas
#     except Exception as e:
#         await loading.edit_text('<strong>⚠️ Недостаточно средств для оплаты комиссии.</strong>\n'
# 						'<i>Уменьшите сумму вывода или попробуйте позже.</i>', parse_mode='HTML', reply_markup=None)
#         logger.warning(f'У пользователя {user_id} недостаточно средств для оплаты комиссии: Сеть - {chain} | Ошибка - {e}.')


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