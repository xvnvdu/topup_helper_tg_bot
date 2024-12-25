from ast import Pass
from typing import Any

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from web3 import Web3

from .api_responses import GetData
from ..amount_handler import choose_amount
from ..models import Networks, Currencies
from ..main_crypto import (pending_user_balance, ok_to_swap, pending_user_balance_in_usd, pending_chain_swap, pending_trx_id, pending_swap_details,
                          pending_currency_to_swap, pending_crypto_swap_amount, pending_swap_amount_in_usd, pending_currency_swap_to, pending_trx_data, get_time)

from logger import logger
from bot.main_bot import users_data_dict, id_generator, total_values, save_total, save_data, save_payments, users_payments_dict
from bot.bot_buttons import (swap_choice_keyboard, swap_second_choice_keyboard, crypto_amount_swap, successful_swap,
                             change_swap_amount, confirm_swap_keyboard, allowance_handler_keyboard, successful_approve)


''' ВЫБИРАЕМ INPUT '''

async def swap_choice(call: CallbackQuery, chain: str):
    user_id = call.from_user.id
    ok_to_swap[user_id] = False
    await call.message.edit_text('<b>♻️ Выберите монету, которую хотите обменять:</b>', 
                                 parse_mode='HTML', reply_markup=swap_choice_keyboard(chain))


''' ВЫБИРАЕМ OUTPUT '''

async def swap_second_choice(call: CallbackQuery, chain: str, currency: str):
    user_id = call.from_user.id
    ok_to_swap[user_id] = False
    await call.message.edit_text('<b>♻️ Выберите монету, на которую хотите совершить обмен:</b>',
                                 parse_mode='HTML', reply_markup=swap_second_choice_keyboard(chain, currency))


''' ВЫБИРАЕМ СУММУ '''

async def amount_to_swap(call: CallbackQuery, chain: str, cur1: str, cur2: str):
	user_id = call.from_user.id
	user_data = users_data_dict[user_id]
	ok_to_swap[user_id] = False
 
	pending_currency_swap_to[user_id] = cur2
 
	wallet_address = user_data['Wallet_address']

	text = await choose_amount(user_id, chain, cur1, wallet_address, 'swap')
    
	await call.message.edit_text(text, parse_mode='HTML', reply_markup=crypto_amount_swap(chain, cur1, cur2))
 
 
''' ОБРАБОТЧИК КНОПОК ВЫБОРА СУММЫ '''
 
async def choose_amount_to_swap(call: CallbackQuery):
	user_id = call.from_user.id
	user_data = users_data_dict[user_id]
    
	percent = int(str(call.data).split('_')[0])
	chain = str(call.data).split('_')[3]
	cur1 = str(call.data).split('_')[4]
	cur2 = str(call.data).split('_')[5]
 
	address = user_data['Wallet_address']
	balance = pending_user_balance[user_id]
	usd_balance = float(pending_user_balance_in_usd[user_id])
 
	rpc = Networks.networks[chain].rpc
	web3 = Web3(Web3.HTTPProvider(rpc))
	chain_id = Networks.networks[chain].chain_id
	native_currency = Networks.networks[chain].coin_symbol
 
	cur1_price = Currencies.currencies[chain][cur1].return_price
	cur2_price = Currencies.currencies[chain][cur2].return_price
 
	decimals1 = Currencies.currencies[chain][cur1].decimals
	decimals2 = Currencies.currencies[chain][cur2].decimals
 
	contract1 = Currencies.currencies[chain][cur1].contract
	contract2 = Currencies.currencies[chain][cur2].contract

	if contract1 is None:
		contract1 = '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
	if contract2 is None:
		contract2 = '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
 
	trx_id = await id_generator()
	pending_trx_id[user_id] = trx_id
 
	ok_to_swap[user_id] = False

	user_amount = float(balance) * percent / 100
	amount_in_usd = usd_balance * percent / 100
	user_amount_wei = int(user_amount * decimals1)

	if amount_in_usd < 0.01:
		await call.message.edit_text(f'<strong>⚠️ Слишком маленькое значение.</strong>\n'
				f'<i>Сумма для вывода должна быть эквивалентна не менее 0.01$</i>', 
				parse_mode='HTML', reply_markup=change_swap_amount(chain, cur1, cur2))
		return

	is_100_native = None
	if cur1_price is not None:
		cur1_price = await cur1_price(cur1)
		pending_swap_amount_in_usd[user_id] = amount_in_usd
  
		if cur1 == Networks.networks[chain].coin_symbol:
			if percent == 100:
				user_amount_wei = int(user_amount_wei * 0.5)
				is_100_native = True

	pending_swap_details[user_id] = {
				'contract1': contract1,
				'contract2': contract2,
				'decimals1': decimals1,
				'decimals2': decimals2,
				'cur1_price': cur1_price,
				'cur2_price': cur2_price,
				'native_currency': native_currency
			}
 
	pending_crypto_swap_amount[user_id] = f'{(float(user_amount)):.12f}'.rstrip('0').rstrip('.')
	logger.info(f'Пользователь {user_id} выбрал {percent}% для свапа. Обмен {cur1} на {cur2}.')

	loading = await call.message.edit_text('🕓 <strong>Проверка allowance...</strong>\n'
                                '<i>Это может занять некоторое время...</i>', parse_mode='HTML')
	await allowance_handler(call, None, chain_id, contract1, contract2, address, user_amount_wei, web3, loading, is_100_native)

 
''' ОБРАБОТЧИК ВВОДА СУММЫ ПОЛЬЗОВАТЕЛЕМ '''
 
async def input_swap_amount(message: Message, state: FSMContext):
	user_id = message.from_user.id
	user_data = users_data_dict[user_id]
	user_amount = message.text.replace(',', '.')	
	balance = pending_user_balance[user_id]

	await message.delete()
	loading = await message.answer('🕓 <strong>Проверка allowance...</strong>\n'
                                '<i>Это может занять некоторое время...</i>', parse_mode='HTML')

	ok_to_swap[user_id] = False
 
	trx_id = await id_generator()
	pending_trx_id[user_id] = trx_id
 
	address = user_data['Wallet_address']
	chain = pending_chain_swap[user_id]
	cur1 = pending_currency_to_swap[user_id]
	cur2 = pending_currency_swap_to[user_id]
 
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

	if contract1 is None:
		contract1 = '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
	if contract2 is None:
		contract2 = '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
 
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
			ok_to_swap[user_id] = False
   
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
 
			pending_swap_details[user_id] = {
				'contract1': contract1,
				'contract2': contract2,
				'decimals1': decimals1,
				'decimals2': decimals2,
				'cur1_price': cur1_price,
				'cur2_price': cur2_price,
				'native_currency': native_currency
			}
			user_amount_wei = int(float(user_amount) * decimals1)
			await allowance_handler(None, message, chain_id, contract1, contract2, address, user_amount_wei, web3, loading, None)
   
	except ValueError:
		logger.warning(f'Пользователь {user_id} ввел некорректную сумму во время свапа.')
		await loading.edit_text('<b>⚠️ Сумма введена некорректно, попробуйте еще раз.</b>', 
                             parse_mode='HTML', reply_markup=change_swap_amount(chain, cur1, cur2))
		await state.clear()


''' ПРОВЕРКА ALLOWANCE '''

async def allowance_handler(call: CallbackQuery | None, message: Message | None, chain_id: int, 
                            contract1: str, contract2: str, address: str, user_amount_wei: int, 
                            web3: Any, loading: Any, is_100_native: bool | None):
    action = call or message 
    user_id = action.from_user.id
        
    user_amount = pending_crypto_swap_amount[user_id]
    cur1 = pending_currency_to_swap[user_id]
    cur2 = pending_currency_swap_to[user_id]
    chain = pending_chain_swap[user_id]

    pending_trx_data[user_id] = {
				'web3': web3,
				'swap': {
					'tx': None,
					'params': {
						'src': contract1,
						'dst': contract2,
						'amount': user_amount_wei,
						'from': address,
						'origin': address,
						'slippage': 1
					}
          		},
				'allowance': None
			}
    
    allowance = await GetData.check_allowance(chain_id, contract1, address)
    if int(allowance) < int(user_amount_wei):
        data, gas_price_wei, token = await GetData.get_allowance_data(chain_id, contract1, user_amount_wei)
        allowance_params = {
            'from': address,
			'data': data,
			'value': 0,
			'to': Web3.to_checksum_address(token),
			'maxFeePerGas': int(gas_price_wei),
            'maxPriorityFeePerGas': int(gas_price_wei),
            'chainId': chain_id
		}
        
        try:
            estimated_gas = web3.eth.estimate_gas(allowance_params)
            allowance_params['gas'] = estimated_gas
            pending_trx_data[user_id]['allowance'] = allowance_params
            
            gas_price = web3.from_wei(int(gas_price_wei), 'gwei')
            trx_fee_wei = int(gas_price_wei) * int(estimated_gas)
            trx_fee = web3.from_wei(trx_fee_wei, 'ether')
            
            native_currency = Networks.networks[chain].coin_symbol
            return_usd_fee = Currencies.currencies[chain][native_currency].return_price
            trx_fee_usd = float(trx_fee) * await return_usd_fee(native_currency)
            
            text = (f'☑️ <b>Необходимо дать подтверждение контракту на взаимодействие с вашими токенами!</b>\n\n'
                    f'<i>Этой транзакцией вы позволите контракту управлять <code>{f"{float(user_amount):.5f}".rstrip("0").rstrip(".")}' 
                    f' {cur1}</code> с вашего кошелька.</i>\n\n'
					f'<b>⛽️ Цена газа: <code>{f"{float(gas_price):.5f}".rstrip("0").rstrip(".")} GWei</code>\n'
					f'💳 Комиссия: <code>{f"{float(trx_fee):.9f}".rstrip("0")} {native_currency}</code></b> '
					f'<i>({f"{float(trx_fee_usd):.5f}".rstrip("0").rstrip(".")}$)</i>\n\n'
					f'<b>Подтверждаете?</b>')
            await loading.edit_text(text, parse_mode='HTML', reply_markup=allowance_handler_keyboard(chain, cur1, cur2))                
        
        except Exception as e:
            logger.info(f'Сработало исключение в allowance_handler: {e}')
            await loading.edit_text('<strong>⚠️ Недостаточно средств для оплаты комиссии.</strong>\n'
						'<i>Пополните баланс или попробуйте позже.</i>', parse_mode='HTML', 
      					reply_markup=change_swap_amount(chain, cur1, cur2))
    
    else:
        if call is not None:
            await swap_details(call, None, True, loading, is_100_native)
        else:
            await swap_details(None, message, True, loading, None)


''' ДЕЛАЕМ APPROVE '''

async def tokens_approved(call: CallbackQuery):
    user_id = call.from_user.id
    user_data = users_data_dict[user_id]
    
    loading = await call.message.edit_text('🕓 <strong>Подписываем транзакцию...</strong>', parse_mode='HTML')
    
    address = user_data['Wallet_address']
    user_pk = user_data['Private_key']
    
    amount_crypto = pending_crypto_swap_amount[user_id]
    chain = pending_chain_swap[user_id]
    allowance_params = pending_trx_data[user_id]['allowance']
    web3 = pending_trx_data[user_id]['web3']
    cur1 = pending_currency_to_swap[user_id]
    
    trx_id = await id_generator()
    today, time_now = await get_time()
    
    try:
        allowance_params['nonce'] = web3.eth.get_transaction_count(address)
        signed_allowance = web3.eth.account.sign_transaction(allowance_params, user_pk)
        allowance_hash = web3.eth.send_raw_transaction(signed_allowance.rawTransaction)
        approve_hash_hex = web3.to_hex(allowance_hash)
        
        explorer = Networks.networks[chain].explorer
        exp_link = Networks.networks[chain].explorer_link
        
        await save_trx(user_id, 'approve', 0, explorer, exp_link, approve_hash_hex, chain, amount_crypto, cur1, None, trx_id, today, time_now)
        await loading.edit_text(f'✅ <strong>Подтверждение отправлено!</strong>\n\n'
                                f'<strong>Хэш approve: <pre>{approve_hash_hex}</pre></strong>\n\n'
                                f'<i>Теперь вы можете совершить обмен, используя кнопку ниже.</i>', parse_mode='HTML', 
                                reply_markup=successful_approve(exp_link, explorer, approve_hash_hex, True, today, time_now),
                                disable_web_page_preview=True)
        logger.info(f'Пользователь {user_id} дал подтверждение контракту. Хэш - {approve_hash_hex}')
    
    except Exception as e:
        logger.info(f'Произошла ошибка при подписании approve, пользователь {user_id}: {e}')
        await call.message.edit_text('<b>⚠️ Произошла ошибка при подписании транзакции, попробуйте еще раз.</b>', 
							parse_mode='HTML')


''' ПОЛУЧАЕМ И ВЫВОДИМ ДЕТАЛИ СВАПА '''

async def swap_details(call: CallbackQuery | None, message: Message | None, was_approved: bool, 
                       message_to_edit: Any, is_100_native: bool | None):
    action = call or message
    user_id = action.from_user.id
    user_data = users_data_dict[user_id]

    text = '🕓 <strong>Рассчитываю комиссию.</strong>\n<i>Это может занять некоторое время...</i>'
    
    method = message_to_edit.edit_text if was_approved else call.message.answer
    loading = await method(text, parse_mode='HTML')
    
    address = user_data['Wallet_address']

    balance = pending_user_balance[user_id]
    chain = pending_chain_swap[user_id]
    web3 = pending_trx_data[user_id]['web3']
    swap_params = pending_trx_data[user_id]['swap']['params']

    chain_id = chain_id = Networks.networks[chain].chain_id
    trx_id = pending_trx_id[user_id]
    
    cur1 = pending_currency_to_swap[user_id]
    cur2 = pending_currency_swap_to[user_id]
    user_amount = pending_crypto_swap_amount[user_id]

    cur1_price = pending_swap_details[user_id]['cur1_price']
    cur2_price = pending_swap_details[user_id]['cur2_price']

    decimals1 = int(pending_swap_details[user_id]['decimals1'])
    decimals2 = int(pending_swap_details[user_id]['decimals2'])
    native_currency = pending_swap_details[user_id]['native_currency']
    
    try:
        output_amount_wei, swap_contract, data, gas, gas_price_wei, value = await GetData.get_swap_data(chain_id, swap_params)
        trx_fee = web3.from_wei(gas * gas_price_wei, 'ether')
        output_amount = output_amount_wei / decimals2
		
        return_usd_fee = Currencies.currencies[chain][native_currency].return_price
        trx_fee_usd = float(trx_fee) * await return_usd_fee(native_currency)
        gas_price = web3.from_wei(gas_price_wei, 'gwei')

        if is_100_native:
            user_amount = float(balance) - (float(trx_fee) * 1.1)
            swap_params['amount'] = user_amount * decimals1
            value = int(value * 2)

        if cur1 == native_currency:
            if float(user_amount) + float(trx_fee) > float(balance):
                logger.warning(f'У пользователя {user_id} недостаточно средств для свапа: {balance} - {user_amount}.')
                await loading.edit_text('<strong>⚠️ У вас не хватает средств для обмена.</strong>\n<i>Уменьшите сумму '
										'или пополните баланс.</i>', parse_mode='HTML', reply_markup=change_swap_amount(chain, cur1, cur2))
                return

        text = (f'<b>🌐 Сеть свапа:</b> <code>{chain}</code>\n'
				f'<b>💸 Продаете:</b> <code>{user_amount} {cur1}</code>')

        if cur1_price is not None:
            cur1_usd_value = pending_swap_amount_in_usd[user_id]
            text += f' <i>({cur1_usd_value}$)</i>'
            
        text += (f'\n<b>💰 Покупаете:</b> <code>{f"{output_amount:.7f}".rstrip("0").rstrip(".")} {cur2}</code>')

        if cur2_price is not None:
            cur2_price = await cur2_price(cur2)
            cur2_usd_value = round(float(output_amount) * cur2_price, 2)
            text += f' <i>({cur2_usd_value}$)</i>'
            
        text += (f'\n\n<b>⛽️ Цена газа: <code>{f"{gas_price:.5f}".rstrip("0").rstrip(".")} GWei</code>\n'
					f'💳 Комиссия: <code>{f"{trx_fee:.9f}".rstrip("0")} {native_currency}</code></b> '
					f'<i>({f"{trx_fee_usd:.5f}".rstrip("0").rstrip(".")}$)</i>\n\n'
					f'<b>Подтверждаете?</b>')

        pending_trx_data[user_id]['swap']['tx'] = {
			'from': address,
			'to': Web3.to_checksum_address(swap_contract),
			'nonce': web3.eth.get_transaction_count(address),
			'data': data,
			'chainId': chain_id,
			'gas': int(gas),
			'maxFeePerGas': int(gas_price_wei),
			'maxPriorityFeePerGas': int(gas_price_wei),
			'value': value
		}

        ok_to_swap[user_id] = True
        
        await loading.edit_text(text, parse_mode='HTML', reply_markup=confirm_swap_keyboard(trx_id, chain, cur1, cur2))
        
    except Exception as e:
        logger.info('сработало исключение в swap_details')
        text = ('<strong>⚠️ Недостаточно средств для оплаты комиссии.</strong>\n'
                '<i>Пополните баланс или попробуйте позже.</i>')
        await loading.edit_text(text, parse_mode='HTML', reply_markup=change_swap_amount(chain, cur1, cur2))

        logger.warning(f'У пользователя {user_id} недостаточно средств для оплаты комиссии: Сеть - {chain} | Ошибка - {e}.')


''' ОТПРАВКА ТРАНЗАКЦИИ ПРИ ЕЕ ПОДТВЕРЖДЕНИИ '''

async def swap_confirmed(call: CallbackQuery):
    user_id = call.from_user.id
    user_data = users_data_dict[user_id]
    
    today, time_now = await get_time()
    trx_id = str(call.data).split('_')[3]
    
    user_pk = user_data['Private_key']
    
    web3 = pending_trx_data[user_id]['web3']
    swap = pending_trx_data[user_id]['swap']['tx']
    chain = pending_chain_swap[user_id]
    
    amount_crypto = pending_crypto_swap_amount[user_id]
    amount_usd = amount_crypto
    cur1 = pending_currency_to_swap[user_id]
    cur2 = pending_currency_swap_to[user_id]
    
    if user_id in pending_swap_amount_in_usd:
        amount_usd = pending_swap_amount_in_usd[user_id]
        
    try:
        explorer = Networks.networks[chain].explorer
        exp_link = Networks.networks[chain].explorer_link
        
        signed_swap = web3.eth.account.sign_transaction(swap, user_pk)
        swap_hash = web3.eth.send_raw_transaction(signed_swap.rawTransaction)
        swap_hash_hex = web3.to_hex(swap_hash)
        
        await save_trx(user_id, 'swap', amount_usd, explorer, exp_link, swap_hash_hex, chain, amount_crypto, cur1, cur2, trx_id, today, time_now)
        
        text = (f'🎉 <strong>Обмен успешно инициирован!</strong>\n\n'
                f'<strong>Хэш транзакции: <pre>{swap_hash_hex}</pre></strong>')
        await call.message.edit_text(text, parse_mode='HTML', reply_markup=successful_swap(explorer, exp_link, swap_hash_hex))
        try:
            await temp_delete(user_id)
        except Exception:
            pass
        ok_to_swap[user_id] = False
        logger.info(f'Пользователь {user_id} успешно совершил обмен. Хэш - {swap_hash_hex}')
        
    except Exception as e:
        logger.info(f'Произошла ошибка при выполнении свапа, пользователь {user_id}: {e}')
        await call.message.edit_text('<b>⚠️ Произошла ошибка при выполнении транзакции, попробуйте еще раз.</b>', 
                             parse_mode='HTML')


''' ЗАПИСЬ ТРАНЗАКЦИИ В ЛОГ '''

async def save_trx(user_id: int, trx_type: str, amount_usd: float | int, explorer: str, exp_link: str, trx_hash: str, 
                   chain: str, amount_crypto: str, cur1: str, cur2: str | None, trx_id: str, today: str, time_now: str):
    user_payments = users_payments_dict[user_id]['Transactions']
    
    total_values['Total_transactions_count'] += 1
    trx_num = total_values['Total_transactions_count']
    
    if trx_type == 'swap':
        total_values['Total_swaps_count'] += 1
        total_values['Total_swaps_volume_usd'] += float(amount_usd)
        trx_info = (f' Обмен <a href = "{exp_link}/tx/{trx_hash}">{chain}</a> '
                    f'— <code>{cur1}/{cur2}</code>')
    else:
        trx_info = (f' Approve <a href = "{exp_link}/tx/{trx_hash}">{chain}</a> '
                    f'— <code>{f"{amount_crypto:.6f}".rstrip("0").rstrip(".")} {cur1}</code>')
    
    await save_total()
    await save_data()
    
    if today not in user_payments:
        user_payments[today] = {time_now: {'RUB': None,
                                      	   'USD': amount_usd,
									  	   'transaction_num': trx_num,
									  	   'type': trx_info,
										   'explorer': explorer,
                                           'explorer_link': exp_link,
										   'hash': trx_hash,
									  	   'trx_id': trx_id}}
        await save_payments()
    else:
        user_payments[today][time_now] = {'RUB': None,
                                          'USD': amount_usd,
										  'transaction_num': trx_num,
										  'type': trx_info,
            							  'explorer': explorer,
                                          'explorer_link': exp_link,
										  'hash': trx_hash,
										  'trx_id': trx_id}
        await save_payments()



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


''' НАЙДЕНА УСТАРЕВШАЯ ТРАНЗАКЦИЯ '''

async def swap_declined(call: CallbackQuery):
    user_id = call.from_user.id
    
    logger.warning(f'Пользователь {user_id} воспользовался устаревшей транзакцией для свапа.')
    await  call.message.edit_text('⛔️ <strong>Данные транзакции устарели!</strong>\n'
                                          '<i>Попробуйте инициировать новую.</i>', parse_mode='HTML')


''' УДАЛЕНИЕ ВРЕМЕННЫХ ХРАНИЛИЩ '''

async def temp_delete(user_id: int):
    del (pending_trx_data[user_id],
         pending_chain_swap[user_id], 
         pending_swap_details[user_id], 
         pending_currency_swap_to[user_id],
         pending_currency_to_swap[user_id], 
         pending_swap_amount_in_usd[user_id], 
         pending_crypto_swap_amount[user_id]) 