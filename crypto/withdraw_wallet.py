from web3 import Web3
from aiogram.types import Message
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.main_bot import id_generator, users_data_dict, users_payments_dict, total_values, save_data, save_total, save_payments
from bot.bot_buttons import (crypto_amount_to_withdraw, successful_wallet_withdrawal, try_again_withdraw_amount, change_withdraw_amount, 
                             try_again_address_input_keyboard, confirm_withdrawal)

from .models import Networks, Currencies
from .get_balance_func import get_native_balance, get_token_balance
from .main_crypto import (CryptoPayments, pending_crypto_withdraw_amount, pending_chain_withdraw, pending_withdrawal_trx, 
                          pending_currency_to_withdraw, pending_user_balance, withdraw_amount_to_show, withdraw_amount_usd_value, ok_to_withdraw, pending_withdraw_info, today, time_now)


async def withdraw_choice(call: CallbackQuery):
	user_id = call.from_user.id
	user_data = users_data_dict[user_id]
 
	chain = str(call.data).split('_')[1]
	currency = str(call.data).split('_')[2]
	wallet_address = user_data['Wallet_address']

	rpc_url = Networks.networks[chain].rpc
	decimals = Currencies.currencies[chain][currency].decimals
	contract = Currencies.currencies[chain][currency].contract
	coin_price = Currencies.currencies[chain][currency].return_price
 
	pending_currency_to_withdraw[user_id] = currency
	pending_chain_withdraw[user_id] = chain
	ok_to_withdraw[user_id] = False
 
	if contract is None:
		balance = await get_native_balance(rpc_url, wallet_address, decimals)
	else:
		balance = await get_token_balance(contract, rpc_url, wallet_address, decimals)

	pending_user_balance[user_id] = balance
	text = f'<strong>💸 Мои активы</strong> <i>{chain} — {currency}</i>: <code>{balance} {currency}</code>'

	if coin_price is not None:
		coin_price = await coin_price()
		usd_value = round(balance * coin_price, 2)
		text += f' <i>({usd_value}$)</i>'

	text += f'\n\n<i>Выберите сумму для вывода или введите ее вручную:</i>'

	await call.message.edit_text(text=text, parse_mode='HTML', reply_markup=crypto_amount_to_withdraw(chain, currency))


async def amount_to_withdraw(message: Message, state: FSMContext):
	user_id = message.from_user.id
	user_amount = message.text.replace(',', '.')	
	balance = pending_user_balance[user_id]

	ok_to_withdraw[user_id] = False
 
	chain = pending_chain_withdraw[user_id]
	currency = pending_currency_to_withdraw[user_id]
	pending_crypto_withdraw_amount[user_id] = user_amount
	coin_price = Currencies.currencies[chain][currency].return_price

	try: 
		await message.delete()
		amount = user_amount
		if len(str(amount)) > 9:
			amount = f'{(float(user_amount)):.7f}'
		withdraw_amount_to_show[user_id] = amount
  
		if float(amount) <= 0:
			await message.answer('<strong>⚠️ Сумма введена некорректно.</strong>\n<i>Нельзя вывести '
                                 'сумму отрицательную или равную нулю.</i>', parse_mode='HTML',
                                 reply_markup=try_again_withdraw_amount(chain, currency))
			await state.clear()

		elif float(balance) < float(amount):
			await message.answer('<strong>⚠️ У вас не хватает средств для вывода.</strong>\n<i>Уменьшите сумму '
                                 'или пополните баланс.</i>', parse_mode='HTML', reply_markup=try_again_withdraw_amount(chain, currency))
			await state.clear()
   
		else:
			text = f'<strong>📒 Введите адрес для пополнения</strong>\n\n<i>Вы переводите <code>{amount} {currency}</code></i>'
			if coin_price is not None:
				coin_price = await coin_price()
				usd_value = round(float(amount) * coin_price, 2)
				withdraw_amount_usd_value[user_id] = usd_value
				text += f' <i>({usd_value}$)</i>'
				if usd_value < 0.01:
					await message.answer('<strong>⚠️ Слишком маленькое значение.</strong>\n'
							'<i>Попробуйте увеличить сумму для вывода, она должна быть эквивалентна не менее 0.01$</i>', 
							parse_mode='HTML', reply_markup=try_again_withdraw_amount(chain, currency))
					await state.clear()
					return
			else:
				if float(amount) < 0.01:
					await message.answer('<strong>⚠️ Слишком маленькое значение.</strong>\n'
							'<i>Попробуйте увеличить сумму для вывода, она должна быть эквивалентна не менее 0.01$</i>', 
							parse_mode='HTML', reply_markup=try_again_withdraw_amount(chain, currency))
					await state.clear()
					return
			await message.answer(text, parse_mode='HTML', reply_markup=change_withdraw_amount(chain, currency))
			await state.set_state(CryptoPayments.address_withdraw_to)
    
	except ValueError:
		await message.answer('<strong>⚠️ Сумма введена некорректно, попробуйте еще раз.</strong>', 
                             parse_mode='HTML', reply_markup=try_again_withdraw_amount(chain, currency))
		await state.clear()


async def try_another_address(call: CallbackQuery):
	user_id = call.from_user.id
 
	chain = pending_chain_withdraw[user_id]
	amount = withdraw_amount_to_show[user_id]
	currency = pending_currency_to_withdraw[user_id]

	ok_to_withdraw[user_id] = False

	text = f'<strong>📒 Введите адрес для пополнения</strong>\n\n<i>Вы переводите <code>{amount} {currency}</code></i>'
 
	if user_id in withdraw_amount_usd_value:
		usd_value = withdraw_amount_usd_value[user_id]
		text += f' <i>({usd_value}$)</i>'

	await call.message.edit_text(text, parse_mode='HTML', reply_markup=change_withdraw_amount(chain, currency))


async def address_input(message: Message, state: FSMContext):
	user_id = message.from_user.id
	user_data = users_data_dict[user_id]

	reciever = message.text
	await message.delete()
	loading = await message.answer('🕓 <strong>Рассчитываю комиссию.</strong>\n'
                                '<i>Это может занять некоторое время...</i>', parse_mode='HTML')
 
	sender = user_data['Wallet_address']

	ok_to_withdraw[user_id] = False
 
	chain = pending_chain_withdraw[user_id]
	currency = pending_currency_to_withdraw[user_id]
	native_currency = Networks.networks[chain].coin_symbol
	amount = pending_crypto_withdraw_amount[user_id]
	usd_value = withdraw_amount_usd_value[user_id] if user_id in withdraw_amount_usd_value else None
	add_usd_value = '' if usd_value is None else f' <i>({usd_value}$)</i>'

	is_valid = Web3.is_address(reciever)

	rpc = Networks.networks[chain].rpc
	web3 = Web3(Web3.HTTPProvider(rpc))
	gas_price_wei = web3.eth.gas_price
	gas_price = web3.from_wei(gas_price_wei, 'gwei')
	max_priority_fee = web3.eth.max_priority_fee
 
	if is_valid:
		tx = {
		'nonce': web3.eth.get_transaction_count(sender),
		'from': sender,
		'to': reciever,
		'value': web3.to_wei(amount, 'ether'),
		'maxFeePerGas': gas_price_wei,
		'maxPriorityFeePerGas': max_priority_fee,
		'chainId': web3.eth.chain_id
	}

		try:
			estimated_gas = web3.eth.estimate_gas(tx)
			tx['gas'] = estimated_gas
	
		except Exception as e:
			await loading.edit_text('<strong>⚠️ Недостаточно средств для оплаты комиссии.</strong>\n'
						'<i>Уменьшите сумму вывода или попробуйте позже.</i>', 
								parse_mode='HTML', reply_markup=change_withdraw_amount(chain, currency))
			raise Exception(f'{today} | {time_now} | Ошибка при инициации транзакции: {e} | Пользователь {user_id}')
	
		pending_withdrawal_trx[user_id] = tx
		return_usd_fee = Currencies.currencies[chain][native_currency].return_price

		trx_fee = web3.from_wei(gas_price_wei * estimated_gas, "ether")
	
		trx_fee_usd = float(trx_fee) * await return_usd_fee()

		if reciever.lower() == sender.lower():
			await loading.edit_text('<strong>⚠️ Вы не можете перевести самому себе.</strong>', 
                             parse_mode='HTML', reply_markup=try_again_address_input_keyboard)
		else:
			ok_to_withdraw[user_id] = True
			await loading.edit_text(f'<strong>🌐 Сеть перевода: <code>{chain}</code>\n'
                        f'💸 Сумма перевода: <code>{amount} {currency}</code></strong>{add_usd_value}\n'
                        f'<strong>📒 Получатель: <code>{reciever}</code>\n\n'
                        f'⛽️ Цена газа: <code>{gas_price} GWei</code> \n'
                        f'💳 Комиссия: <code>{trx_fee} {native_currency}</code></strong> <i>({round(trx_fee_usd, 5)}$)</i>\n\n'
                        f'<strong>Подтверждаете?</strong>', parse_mode='HTML', reply_markup=confirm_withdrawal())
	else:
		await loading.edit_text('<strong>⚠️ Адрес введен некорректно.</strong>\n'
                       '<i>Проверьте указанный адрес и попробуйте еще раз.</i>', 
                             parse_mode='HTML', reply_markup=try_again_address_input_keyboard)
		await state.clear()
    

async def withdrawal_confirmed(call: CallbackQuery):
	user_id = call.from_user.id
	user_payments = users_payments_dict[user_id]['Transactions']

	amount_usd = withdraw_amount_usd_value[user_id]
	amount_crypto = pending_crypto_withdraw_amount[user_id]
	chain = pending_chain_withdraw[user_id]
	explorer = Networks.networks[chain].explorer
	exp_link = Networks.networks[chain].explorer_link
	coin = pending_currency_to_withdraw[user_id]

	try:
		trx_hash = await withdraw_crypto(call, chain=chain)
	except Exception as e:
		connected = True
		trx_hash = False
		await call.message.edit_text('⚠️ <strong>Произошла ошибка, попробуйте позже.</strong>', 
                               parse_mode='HTML', reply_markup=None)
		raise Exception(f'{today} | {time_now} | Ошибка при выводе средств: {e} | Пользователь {user_id}')

	if trx_hash:
		connected = True
		pending_withdraw_info[user_id] = (f' Перевод <a href ="{exp_link}/tx/{trx_hash}">{chain}</a> '
                                    f'— <code>{amount_crypto} {coin}</code>')

		trx_info = pending_withdraw_info[user_id]
		trx_id = await id_generator()
		total_values['Total_transactions_count'] += 1
		trx_num = total_values['Total_transactions_count']

		await save_total()
		await save_data()

		if today not in user_payments:
			user_payments[today] = {time_now: {'RUB': 0,
											'USD': amount_usd,
                                            'transaction_num': trx_num,
                                            'type': trx_info,
                                            'trx_id': trx_id}}
			await save_payments()
		else:
			user_payments[today][time_now] = {'RUB': 0,
											'USD': amount_usd,
                                            'transaction_num': trx_num,
                                            'type': trx_info,
                                            'trx_id': trx_id}
			await save_payments()

		await call.message.edit_text(f'🎉 <strong>Успешный перевод!</strong>\n'
                                        f'<i>Средства скоро поступят на адрес получателя.</i>\n\n'
                                        f'<strong>Хэш: <pre>{trx_hash}</pre></strong>',
                                        parse_mode='HTML', reply_markup=successful_wallet_withdrawal(exp_link, explorer, trx_hash), 
                                        disable_web_page_preview=True)
	if not connected:
		await  call.message.edit_text('⛔️ <strong>Произошла ошибка при инициализации транзакции!\n'
										'<i>Повторите попытку позже.</i></strong>', parse_mode='HTML')



async def withdraw_crypto(call: CallbackQuery, chain):
	user_id = call.from_user.id
	user_data = users_data_dict[user_id]

	rpc = Networks.networks[chain].rpc
	web3 = Web3(Web3.HTTPProvider(rpc))

	if not web3.is_connected():
		raise Exception(f'{today} | {time_now} | Ошибка подключения к сети {chain} | Пользователь: {user_id}')

	else:
		user_pk = user_data['Private_key']
		tx = pending_withdrawal_trx[user_id]
		chain = pending_chain_withdraw[user_id]
  
		signed = web3.eth.account.sign_transaction(tx, user_pk)

		tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)

		hash_hex = web3.to_hex(tx_hash)
		return hash_hex


async def withdrawal_declined(call: CallbackQuery):
    await  call.message.edit_text('⛔️ <strong>Данные транзакции устарели!</strong>\n'
                                          '<i>Попробуйте инициировать новую.</i>', parse_mode='HTML')