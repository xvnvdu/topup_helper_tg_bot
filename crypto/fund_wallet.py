import web3
from web3 import Web3
from typing import Any
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from logger import logger
from config import bot_wallet_pk as pk, bot_wallet_address as adr
from bot.main_bot import id_generator, save_data, save_payments, save_total, users_data_dict, total_values, users_payments_dict
from bot.bot_buttons import successful_wallet_fund, try_again_crypto_amount_keyboard, confirm_fund_wallet, back_to_chain_keyboard

from .models import Networks
from .price_parser import return_eth_price, return_matic_price, return_usd_price
from .main_crypto import (pending_chain_fund, pending_crypto_fund_amount, pending_fund_info, 
                          pending_rub_amount, ok_to_fund, pending_fund_trx_id, get_time)


''' ВВОД СУММЫ ПОПОЛНЕНИЯ КРИПТОКОШЕЛЬКА '''

async def fund(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_amount = message.text.replace(',', '.')
    
    await message.delete()

    user_data = users_data_dict[user_id]
    balance = user_data['Balance']
    chain = pending_chain_fund[user_id]
    native = Networks.networks[chain].coin_symbol
    
    usd_price = await return_usd_price()
    currency_price = round(((await return_matic_price() * usd_price if chain == 'Polygon' 
                      else await return_eth_price() * usd_price) * 1.05), 2)
        
    try:
        amount = float(user_amount)
        amount = int(amount)
        if amount <= 0:
            logger.warning(f'Пользователь {user_id} ввел некорректную сумму при пополнении криптокошелька: {amount}.')
            
            await message.answer('<strong>⚠️ Сумма введена некорректно.</strong>\n<i>Нельзя пополнить кошелек на '
                                 'сумму отрицательную или равную нулю.</i>', parse_mode='HTML',
                                 reply_markup=try_again_crypto_amount_keyboard(chain))
        elif int(balance) < amount:
            logger.warning(f'У пользователя {user_id} не хватает средств для пополнения криптокошелька: {balance} - {amount}.')
            
            await message.answer('<strong>⚠️ У вас не хватает средств для пополнения.</strong>\n<i>Уменьшите сумму '
                                 'или пополните баланс.</i>', parse_mode='HTML', reply_markup=try_again_crypto_amount_keyboard(chain))
        else:
            user_recieve = f'{(amount / currency_price):.7f}'
            pending_crypto_fund_amount[user_id] = user_recieve
            pending_rub_amount[user_id] = amount
            trx_id = await id_generator()
            pending_fund_trx_id[user_id] = trx_id
            
            ok_to_fund[user_id] = True
            
            logger.info(f'Пользователь {user_id} подтверждает пополнение криптокошелька на {user_recieve} {native}.')
            await message.answer(f'<strong>🌐 Пополняемая сеть: <code>{chain}</code>\n💳 Сумма пополнения: <code>{amount}₽</code>\n\n'
                                 f'📊 Курс: <code>1 {native} = {currency_price}₽</code>\nИтого к пополнению: <code>{user_recieve} {native}</code>\n\n'
                                 f'Подтверждаете?</strong>', parse_mode='HTML', reply_markup=confirm_fund_wallet(chain, trx_id))
    except ValueError:
        logger.warning(f'Пользователь {user_id} ввел некорректную сумму при пополнении криптокошелька.')
        await message.answer('<strong>⚠️ Сумма введена некорректно, попробуйте еще раз.</strong>', 
                             parse_mode='HTML', reply_markup=try_again_crypto_amount_keyboard(chain))
    await state.clear()


''' ПОПОЛНЕНИЕ КРИПТОКОШЕЛЬКА ПОДТВЕРЖДЕНО '''

async def wallet_funding_confirmed(call: CallbackQuery) -> Any:
    user_id = call.from_user.id
    user_data = users_data_dict[user_id]
    user_payments = users_payments_dict[user_id]['Transactions']
    
    amount_rub = pending_rub_amount[user_id]
    amount_crypto = pending_crypto_fund_amount[user_id]
    chain = pending_chain_fund[user_id]
    explorer = Networks.networks[chain].explorer
    exp_link = Networks.networks[chain].explorer_link
    
    native = Networks.networks[chain].coin_symbol

    try:
        trx_hash = await send_crypto(call, chain=chain)
    except web3.exceptions.Web3RPCError:
        connected = True
        trx_hash = False
        
        logger.critical(f'На кошельке-хранилище недостаточно средств для пополнения. Сеть - {chain} | Сумма - {amount_crypto} {native}.')
        await call.message.edit_text('⚠️ <strong>Ошибка пополнения. Недостаточно средств.</strong>\n'
                                        '<i>На кошельке, с которого происходит вывод, недостаточно средств в '
                                        'выбранной вами сети. Попробуйте уменьшить сумму пополнения, либо '
                                        'обратитесь к администратору.</i>', parse_mode='HTML', reply_markup=back_to_chain_keyboard(chain))
    
    if trx_hash:
        connected = True
        pending_fund_info[user_id] = (f' Пополнение <a href="{exp_link}/tx/{trx_hash}">{chain}</a> '
                                        f'— <code>{amount_crypto} {native}</code>')
        trx_info = pending_fund_info[user_id]
        trx_id = pending_fund_trx_id[user_id]
        total_values['Total_transactions_count'] += 1
        trx_num = total_values['Total_transactions_count']
        user_data['Balance'] -= amount_rub

        await save_total()
        await save_data()

        today, time_now = await get_time()
        if today not in user_payments:
            user_payments[today] = {time_now: {'RUB': amount_rub,
                                               'USD': 0,
                                               'transaction_num': trx_num,
                                               'type': trx_info,
                                               'trx_id': trx_id}}
            await save_payments()
        else:
            user_payments[today][time_now] = {'RUB': amount_rub,
                                              'USD': 0,
                                              'transaction_num': trx_num,
                                              'type': trx_info,
                                              'trx_id': trx_id}
            await save_payments()

        logger.info(f'Пользователь {user_id} успешно пополнил криптокошелек. Сеть - {chain} | Сумма - {amount_crypto} {native}')
        await call.message.edit_text(f'🎉 <strong>Транзакция инициирована!</strong>\n'
                                        f'<i>Ожидайте поступления средств.</i>\n\n'
                                        f'<strong>Хэш: <pre>{trx_hash}</pre></strong>',
                                        parse_mode='HTML', reply_markup=successful_wallet_fund(exp_link, explorer, trx_hash), 
                                        disable_web_page_preview=True)
    if not connected:
        logger.error(f'Ошибка при инициализации транзакции пользователем {user_id}. Сеть - {chain} | Сумма - {amount_crypto} {native}')
        await  call.message.edit_text('⛔️ <strong>Произошла ошибка при инициализации транзакции!\n'
                                        '<i>Повторите попытку позже.</i></strong>', parse_mode='HTML')

    try:     
        del pending_rub_amount[user_id], pending_chain_fund[user_id], pending_crypto_fund_amount[user_id], pending_fund_info[user_id]
        ok_to_fund[user_id] = False
    except KeyError:
        pass


''' ПРОВЕРКА НА УСТАРЕВШИЕ ТРАНЗАКЦИИ '''

async def try_to_fund(call: CallbackQuery):
    user_id = call.from_user.id
    
    if ok_to_fund[user_id]:
        if f'{call.data}'.split('_')[3] == pending_fund_trx_id[user_id]:
            await wallet_funding_confirmed(call)
        else:
            await wallet_funding_declined(call)
    else:
        await wallet_funding_declined(call)


''' УСТАРЕВШАЯ ТРАНЗАКЦИЯ '''

async def wallet_funding_declined(call: CallbackQuery):
     user_id = call.from_user.id
    
     logger.warning(f'Пользователь {user_id} воспользовался устаревшей транзакцией для пополнения.')
     await  call.message.edit_text('⛔️ <strong>Данные транзакции устарели!</strong>\n'
                                          '<i>Попробуйте инициировать новую.</i>', parse_mode='HTML')


''' ПОПОЛНЕНИЕ ПОДТВЕРЖДЕНО '''

async def send_crypto(call: CallbackQuery, chain) -> Any:
    user_id = call.from_user.id
    user_data = users_data_dict[user_id]

    rpc = Networks.networks[chain].rpc
    web3 = Web3(Web3.HTTPProvider(rpc))

    if not web3.is_connected():
        today, time_now = await get_time()
        logger.error(f'Ошибка подключения к сети {chain}. Пользователь: {user_id}. RPC: {rpc}')
        raise Exception(f'{today} | {time_now} Ошибка подключения к сети {chain}. Пользователь: {user_id}')

    else:
        amount_crypto = pending_crypto_fund_amount[user_id]
        chain = pending_chain_fund[user_id]
    
        sender_adrress = adr
        sender_pk = pk

        recipient_address = user_data['Wallet_address']
        gas_price_wei = web3.eth.gas_price
        max_priority_fee = web3.eth.max_priority_fee

        tx = {
            'nonce': web3.eth.get_transaction_count(sender_adrress),
            'to': recipient_address,
            'value': web3.to_wei(amount_crypto, 'ether'),
            'maxFeePerGas': gas_price_wei,
            'maxPriorityFeePerGas': max_priority_fee,
            'chainId': web3.eth.chain_id
        }

        estimated_gas = web3.eth.estimate_gas(tx)
        tx['gas'] = estimated_gas
        
        signed = web3.eth.account.sign_transaction(tx, sender_pk)

        tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
        
        hash_hex = web3.to_hex(tx_hash)
        return hash_hex
    