from web3 import Web3
from aiogram.types import Message
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from logger import logger
from bot.main_bot import id_generator, users_data_dict, users_payments_dict, total_values, save_data, save_total, save_payments
from bot.bot_buttons import (crypto_amount_to_withdraw, successful_wallet_withdrawal, try_again_withdraw_amount, change_withdraw_amount, 
                             try_again_address_input_keyboard, confirm_withdrawal)

from .models import Networks, Currencies, DefaultABIs
from .amount_handler import choose_amount
from .main_crypto import (CryptoPayments, pending_crypto_withdraw_amount, pending_chain_withdraw, pending_withdrawal_trx, 
                          pending_currency_to_withdraw, pending_user_balance, withdraw_amount_to_show, withdraw_amount_usd_value, ok_to_withdraw, pending_withdraw_info, pending_user_balance_in_usd, pending_withdraw_trx_id, get_time)


''' ВЫБОР МОНЕТЫ ДЛЯ ВЫВОДА '''

async def withdraw_choice(call: CallbackQuery):
	user_id = call.from_user.id
	user_data = users_data_dict[user_id]
 
	chain = str(call.data).split('_')[1]
	currency = str(call.data).split('_')[2]
	wallet_address = user_data['Wallet_address']

	logger.info(f'Пользователь {user_id} выбирает сумму для вывода. Сеть - {chain} | Монета - {currency}')

	text = await choose_amount(user_id, chain, currency, wallet_address, 'вывода')

	await call.message.edit_text(text=text, parse_mode='HTML', reply_markup=crypto_amount_to_withdraw(chain, currency))


''' ВЫБОР СУММЫ ДЛЯ ВЫВОДА '''

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
		amount = f'{(float(user_amount)):.12f}'.rstrip('0').rstrip('.')
		withdraw_amount_to_show[user_id] = amount
  
		if float(amount) <= 0:
			logger.warning(f'Пользователь {user_id} ввел некорректную сумму при выводе крипты: {amount}.')
			await message.answer('<strong>⚠️ Сумма введена некорректно.</strong>\n<i>Нельзя вывести '
                                 'сумму отрицательную или равную нулю.</i>', parse_mode='HTML',
                                 reply_markup=try_again_withdraw_amount(chain, currency))
			await state.clear()

		elif float(balance) < float(amount):
			logger.warning(f'У пользователя {user_id} недостаточно средств для вывода крипты: {balance} - {amount}.')
			await message.answer('<strong>⚠️ У вас не хватает средств для вывода.</strong>\n<i>Уменьшите сумму '
                                 'или пополните баланс.</i>', parse_mode='HTML', reply_markup=try_again_withdraw_amount(chain, currency))
			await state.clear()
   
		else:
			text = f'<strong>📒 Введите адрес для пополнения</strong>\n\n<i>Вы переводите <code>{amount} {currency}</code></i>'
			if coin_price is not None:
				coin_price = await coin_price(currency)
				usd_value = round(float(amount) * coin_price, 2)
				withdraw_amount_usd_value[user_id] = usd_value
				text += f' <i>({usd_value}$)</i>'
				if usd_value < 0.01:
					logger.warning(f'Пользователь {user_id} попытался вывести менее 0.01$: {usd_value}.')
           
					await message.answer('<strong>⚠️ Слишком маленькое значение.</strong>\n'
							'<i>Попробуйте увеличить сумму для вывода, она должна быть эквивалентна не менее 0.01$</i>', 
							parse_mode='HTML', reply_markup=try_again_withdraw_amount(chain, currency))
					await state.clear()
					return
			else:
				if float(amount) < 0.01:
					logger.warning(f'Пользователь {user_id} попытался вывести менее 0.01$: {amount}.')
     
					await message.answer('<strong>⚠️ Слишком маленькое значение.</strong>\n'
							'<i>Попробуйте увеличить сумму для вывода, она должна быть эквивалентна не менее 0.01$</i>', 
							parse_mode='HTML', reply_markup=try_again_withdraw_amount(chain, currency))
					await state.clear()
					return
 
			await message.answer(text, parse_mode='HTML', reply_markup=change_withdraw_amount(chain, currency))
			await state.set_state(CryptoPayments.address_withdraw_to)
    
	except ValueError:
		logger.warning(f'Пользователь {user_id} ввел некорректную сумму для вывода крипты.')
		await message.answer('<strong>⚠️ Сумма введена некорректно, попробуйте еще раз.</strong>', 
                             parse_mode='HTML', reply_markup=try_again_withdraw_amount(chain, currency))
		await state.clear()


''' ПОВТОРНЫЙ ВВОД АДРЕСА ПОЛУЧАТЕЛЯ '''

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

	logger.info(f'Пользователь {user_id} повторно указывает адрес для вывода крипты.')
	await call.message.edit_text(text, parse_mode='HTML', reply_markup=change_withdraw_amount(chain, currency))


''' ВВОД АДРЕСА И РАССЧЕТ КОМИССИИ '''

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
	amount = float(pending_crypto_withdraw_amount[user_id])
	amount_to_show = withdraw_amount_to_show[user_id]
	usd_value = withdraw_amount_usd_value[user_id] if user_id in withdraw_amount_usd_value else None
	add_usd_value = '' if Currencies.currencies[chain][currency].return_price is None else f' <i>({usd_value}$)</i>'

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
		'maxFeePerGas': gas_price_wei,
		'maxPriorityFeePerGas': max_priority_fee,
		'chainId': web3.eth.chain_id
	}

		if currency != native_currency:
			try:
				logger.info(f'Пользователь {user_id} выводит ненативную монету: Сеть - {chain} | Монета - {currency}.')
    
				abi = DefaultABIs.Token
				contract_address = Currencies.currencies[chain][currency].contract
				decimals = Currencies.currencies[chain][currency].decimals
				contract = web3.eth.contract(address=contract_address, abi=abi)
				value = int(amount * decimals)

				transfer_func = contract.functions.transfer(reciever, value)
				tx = transfer_func.build_transaction(tx)
    
			except Exception as e:
				logger.error(f'Произошла ошибка при создании транзакции для ERC20 токена: {e}.')
   
		else:
			try:
				logger.info(f'Пользователь {user_id} выводит нативную монету: Сеть - {chain} | Монета - {currency}.')
				tx['to'] = reciever
				tx['value'] = web3.to_wei(amount, 'ether')

			except Exception as e:
				logger.error(f'Произошла ошибка при создании транзакции для ERC20 токена: {e}.')

		try:
			estimated_gas = web3.eth.estimate_gas(tx)
			tx['gas'] = estimated_gas
	
		except Exception as e:
			await loading.edit_text('<strong>⚠️ Недостаточно средств для оплаты комиссии.</strong>\n'
						'<i>Уменьшите сумму вывода или попробуйте позже.</i>', 
								parse_mode='HTML', reply_markup=change_withdraw_amount(chain, currency))
   
			logger.warning(f'У пользователя {user_id} недостаточно средств для оплаты комиссии: Сеть - {chain} | Ошибка - {e}.')
	
		pending_withdrawal_trx[user_id] = tx
		return_usd_fee = Currencies.currencies[chain][native_currency].return_price

		trx_fee = web3.from_wei(gas_price_wei * estimated_gas, "ether")
	
		trx_id = await id_generator()
		pending_withdraw_trx_id[user_id] = trx_id
  
		trx_fee_usd = float(trx_fee) * await return_usd_fee(native_currency)

		if reciever.lower() == sender.lower():
			await loading.edit_text('<strong>⚠️ Вы не можете перевести самому себе.</strong>', 
                             parse_mode='HTML', reply_markup=try_again_address_input_keyboard)
			logger.warning(f'Пользователь {user_id} попытался вывести крипту сам себе: Сеть - {chain} | Монета - {currency}.')
   
		else:
			ok_to_withdraw[user_id] = True
			await loading.edit_text(f'<strong>🌐 Сеть перевода: <code>{chain}</code>\n'
                        f'💸 Сумма перевода: <code>{amount_to_show} {currency}</code></strong>{add_usd_value}\n'
                        f'<strong>📒 Получатель: <code>{reciever}</code>\n\n'
                        f'⛽️ Цена газа: <code>{f"{gas_price:.5f}".rstrip("0").rstrip(".")} GWei</code> \n'
                        f'💳 Комиссия: <code>{f"{trx_fee:.9f}".rstrip("0")} {native_currency}</code></strong> '
                        f'<i>({f"{trx_fee_usd:.5f}".rstrip("0")}$)</i>\n\n'
                        f'<strong>Подтверждаете?</strong>', parse_mode='HTML', reply_markup=confirm_withdrawal(trx_id))
   
			logger.info(f'Пользователь {user_id} подтверждает вывод крипты: Сеть - {chain} | Сумма - {amount_to_show} {currency} | Газ - {gas_price}.')
	else:
		await loading.edit_text('<strong>⚠️ Адрес введен некорректно.</strong>\n'
                       '<i>Проверьте указанный адрес и попробуйте еще раз.</i>', 
                             parse_mode='HTML', reply_markup=try_again_address_input_keyboard)
		logger.warning(f'Пользователь {user_id} ввел некорректный адрес вывода: {reciever}.')
		await state.clear()
    

''' ПОДТВЕРЖДЕНИЕ ВЫВОДА '''

async def withdrawal_confirmed(call: CallbackQuery):
	user_id = call.from_user.id
	user_payments = users_payments_dict[user_id]['Transactions']

	logger.info(f'Пользователь {user_id} подтвердил вывод средств.')

	today, time_now = await get_time()
	
	if user_id in withdraw_amount_usd_value:
		amount_usd = withdraw_amount_usd_value[user_id]
	else:
		amount_usd = pending_crypto_withdraw_amount[user_id]
  
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
		logger.critical(f'Ошибка при выводе средств: {e} | Пользователь {user_id}.')

	if trx_hash:
		connected = True
		pending_withdraw_info[user_id] = (f' Перевод <a href ="{exp_link}/tx/{trx_hash}">{chain}</a> '
                                    f'— <code>{amount_crypto} {coin}</code>')

		trx_info = pending_withdraw_info[user_id]
		trx_id = pending_withdraw_trx_id[user_id]
		total_values['Total_transactions_count'] += 1
		total_values['Total_withdrawals_count'] += 1
		total_values['Total_withdrawals_volume_usd'] += amount_usd
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
		logger.info(f'Пользователь {user_id} успешно осуществил вывод средств. Хэш - {trx_hash}')
  
	if not connected:
		logger.critical(f'Произошла ошибка при инициализации транзакции! | Пользователь {user_id}.')
		await  call.message.edit_text('⛔️ <strong>Произошла ошибка при инициализации транзакции!\n'
										'<i>Повторите попытку позже.</i></strong>', parse_mode='HTML')


'''ИНИЦИАЦИЯ ВЫВОДА '''

async def withdraw_crypto(call: CallbackQuery, chain):
	user_id = call.from_user.id
	user_data = users_data_dict[user_id]

	rpc = Networks.networks[chain].rpc
	web3 = Web3(Web3.HTTPProvider(rpc))

	if not web3.is_connected():
		logger.critical(f'Ошибка подключения к сети {chain}. RPC - {rpc} | Пользователь: {user_id}.')

	else:
		user_pk = user_data['Private_key']
		tx = pending_withdrawal_trx[user_id]
		chain = pending_chain_withdraw[user_id]
  
		signed = web3.eth.account.sign_transaction(tx, user_pk)

		tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)

		hash_hex = web3.to_hex(tx_hash)
		return hash_hex


''' ВВОД СУММЫ ЧЕРЕЗ КНОПКИ '''

async def buttons_withdraw_handler(call: CallbackQuery, state: FSMContext):
	user_id = call.from_user.id

	percent = int(str(call.data).split('_')[0])
	balance = pending_user_balance[user_id]
	chain = pending_chain_withdraw[user_id]
	currency = pending_currency_to_withdraw[user_id]
	usd_balance = float(pending_user_balance_in_usd[user_id])
	coin_price = Currencies.currencies[chain][currency].return_price
  
	ok_to_withdraw[user_id] = False

	user_amount = float(balance) * percent / 100
	amount_in_usd = usd_balance * percent / 100

	if amount_in_usd < 0.01:
		await call.message.edit_text(f'<strong>⚠️ Слишком маленькое значение.</strong>\n'
				f'<i>Сумма для вывода должна быть эквивалентна не менее 0.01$</i>', 
				parse_mode='HTML', reply_markup=change_withdraw_amount(chain, currency))
		await state.clear()
		return

	if currency == Networks.networks[chain].coin_symbol:
		if percent == 100:
			withdraw_in_usd = usd_balance * (1 - 1 / (usd_balance * 100))
			user_amount = balance / usd_balance * withdraw_in_usd

	logger.info(f'Пользователь {user_id} выбрал {percent}% для вывода. Сумма - {user_amount} {currency}.')
	pending_crypto_withdraw_amount[user_id] = user_amount
	withdraw_amount_to_show[user_id] = user_amount

	text = f'<strong>📒 Введите адрес для пополнения</strong>\n\n<i>Вы переводите <code>{user_amount} {currency}</code></i>'
	if coin_price is not None:
		coin_price = await coin_price(currency)
		usd_value = round(float(user_amount) * coin_price, 2)
		withdraw_amount_usd_value[user_id] = usd_value
		text += f' <i>({usd_value}$)</i>'

	await call.message.edit_text(text, parse_mode='HTML', reply_markup=change_withdraw_amount(chain, currency))


''' ПРОВЕРКА НА УСТАРЕВШИЕ ТРАНЗАКЦИИ '''

async def try_to_withdraw(call: CallbackQuery):
    user_id = call.from_user.id
    
    if ok_to_withdraw[user_id]:
        if f'{call.data}'.split('_')[3] == pending_withdraw_trx_id[user_id]:
            await withdrawal_confirmed(call)
        else:
            await withdrawal_declined(call)
    else:
        await withdrawal_declined(call)


''' УСТАРЕВШАЯ ТРАНЗАКЦИЯ '''

async def withdrawal_declined(call: CallbackQuery):
    user_id = call.from_user.id
    
    logger.warning(f'Пользователь {user_id} воспользовался устаревшей транзакцией для вывода.')
    await  call.message.edit_text('⛔️ <strong>Данные транзакции устарели!</strong>\n'
                                          '<i>Попробуйте инициировать новую.</i>', parse_mode='HTML')
    