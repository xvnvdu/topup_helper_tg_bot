import math
import time
from aiogram import Bot
from datetime import datetime
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from logger import logger
from crypto.fund_wallet import try_to_fund
from crypto.main_crypto import CryptoPayments
from crypto.withdraw_wallet import try_another_address, try_to_withdraw
from crypto.wallet_page_maker import main_page, polygon_mainnet, arbitrum_mainnet, optimism_mainnet, base_mainnet

from . import payments
from .send_to_user import send_to_user
from .transactions_log import sorted_payments
from .support.admin_side import cancel_answer
from .support.user_side import cancel_application, bot_support
from .main_bot import (users_data_dict, CustomPaymentState, SendToFriend, pending_sending_amount, Support, 
                       pending_sending_id, pending_sending_message, pending_payments, pending_payments_info)
from .bot_buttons import (menu_keyboard, account_keyboard, payment_keyboard, crypto_keyboard, back_to_support_keyboard, 
                         stars_keyboard, yk_payment_keyboard, zero_transactions_keyboard, skip_message_keyboard,
                         log_buttons, back_to_account_keyboard, step_back_keyboard, confirm_sending_keyboard, chains_keyboard)



async def main_callbacks(call: CallbackQuery, bot: Bot, state: FSMContext):
    user_id = call.from_user.id
    user_data = users_data_dict[user_id]

    phone = int(user_data['Phone']) // 10**4
    balance = user_data['Balance']
    registration_date = user_data['Registration']
    volume = user_data['Funding_volume']

    days_count = (datetime.now() - datetime.strptime(registration_date, '%d.%m.%Y')).days
    if days_count % 10 == 1 and days_count % 100 != 11:
        days = 'день'
    elif days_count % 10 in [2, 3, 4] and not (11 <= days_count % 100 <= 19):
        days = 'дня'
    else:
        days = 'дней'

    current_page = await state.get_data()
    current_page = current_page.get('current_page', 0)
    trx_log = await sorted_payments(call)
    total_pages = math.ceil((len(trx_log)-1) / 15)
    first_page_line = current_page * 15
    last_page_line = first_page_line + 15
    page_text = '\n'.join(trx_log[first_page_line:last_page_line])

    if call.data == 'account':
        logger.info(f'Пользователь {user_id} вошел в аккаунт.')
        await call.message.edit_text(f'<strong>Мой аккаунт</strong>\n\n'
                                     f'⚙️ <strong>ID:</strong> <code>{call.from_user.id}</code>\n'
                                     f'🔒 <strong>Телефон:</strong> <code>{phone}****</code>\n'
                                     f'🗓 <strong>Регистрация:</strong> <code>{registration_date} ({days_count} {days})</code>\n\n'
                                     f'💵 <strong>Мой баланс: </strong><code>{balance}₽</code>\n'
                                     f'💎 <strong>Мой объем пополнений: </strong><code>{volume}₽</code>',
                                     parse_mode='HTML', reply_markup=account_keyboard)
    elif call.data == 'support':
        logger.info(f'Пользователь {user_id} вошел в поддержку.')
        await bot_support(call)
        await state.clear()
        
    elif call.data == 'message_to_support':
        await call.message.edit_text('📢 <b>Опишите вашу проблему ниже.</b>\n'
                                 '<s><i>Вы также можете прикрепить фото к своему сообщению:</i></s>', 
                                 parse_mode='HTML', reply_markup=back_to_support_keyboard)
        await state.set_state(Support.message_to_support)
        
    elif 'cancel_answer' in call.data:
        await cancel_answer(call, state)
        
    elif 'cancel_application' in call.data:
        await cancel_application(call, state)
    
    elif call.data == 'transactions':
        logger.info(f'Пользователь {user_id} вошел в лог транзакций.')
        if users_data_dict[user_id]['Balance'] == 0:
            await call.message.edit_text('<strong>💔 Вы еще не совершили ни одной транзакции.</strong>',
                                         parse_mode='HTML', reply_markup=zero_transactions_keyboard)
        else:
            current_page = 0
            await state.update_data(current_page=current_page)
            await log_buttons(call, page_text, current_page, total_pages)
            
    elif call.data == 'next_page':
        current_page += 1
        await state.update_data(current_page=current_page)
        first_page_line = current_page * 15
        last_page_line = first_page_line + 15
        page_text = '\n'.join(trx_log[first_page_line:last_page_line])
        await log_buttons(call, page_text, current_page, total_pages)
        
    elif call.data == 'prev_page':
        current_page -= 1
        await state.update_data(current_page=current_page)
        first_page_line = current_page * 15
        last_page_line = first_page_line + 15
        page_text = '\n'.join(trx_log[first_page_line:last_page_line])
        await log_buttons(call, page_text, current_page, total_pages)
        
    elif call.data == 'send':
        logger.info(f'Пользователь {user_id} вошел в перевод баланса.')
        await call.message.edit_text('🎁 В этом разделе ты можешь <strong>отправить деньги</strong> со своего '
                                     'баланса другу, на свой второй аккаунт или любому другому пользователю, '
                                     'который <strong>уже пользуется ботом!</strong>\n\n<i>Просто введите сумму для '
                                     'отправки ниже:</i>', parse_mode='HTML', reply_markup=back_to_account_keyboard)
        await state.set_state(SendToFriend.amount_input)
        
    elif call.data == 'choose_id':
        logger.info(f'Пользователь {user_id} вводит ID для перевода баланса.')
        await call.message.edit_text('<strong>👤 Введите ID пользователя для перевода.</strong>\n\n<i>Вам нужно ввести '
                                 'ID пользователя в числовом формате ниже:</i>', parse_mode='HTML', reply_markup=step_back_keyboard)
        await state.set_state(SendToFriend.id_input)
        
    elif call.data == 'message_input':
        logger.info(f'Пользователь {user_id} вводит сообщение при перевода баланса.')
        await state.set_state(SendToFriend.message_input)
        await call.message.edit_text(f'📩 <strong>Вы можете ввести сообщение для пользователя.'
                                     f'</strong>\n<i>Обратите внимаение, что любые премиум-эмодзи, к сожалению, будут '
                                     f'преобразованы в обычные.</i>\n\n<i>Введите ваше текстовое сообщение ниже:</i>',
                                     parse_mode='HTML', reply_markup=skip_message_keyboard)
        
    elif call.data == 'confirm_sending':
        logger.info(f'Пользователь {user_id} собирается сделать перевод баланса.')
        await state.clear()
        pending_sending_message[user_id] = None
        await call.message.answer(f'<strong>Вы переводите: <code>{pending_sending_amount[user_id]}₽</code>\nПользователю '
                             f'под ID: <code>{pending_sending_id[user_id]}</code>\n\nПодтверждаете?</strong>',
                             parse_mode='HTML', reply_markup=confirm_sending_keyboard)
        
    elif call.data == 'sending_confirmed':
        logger.info(f'Пользователь {user_id} успешно перевел баланс.')
        await send_to_user(call, bot, state)
        await call.message.edit_text('<strong>🎁 Перевод успешно отправлен!</strong>\n\n<i>Получателю придет уведомление с '
                                     'суммой перевода, вашим ID и сообщением, которое вы отправили.</i>', 
                                     parse_mode='HTML', reply_markup=back_to_account_keyboard)
        
    elif call.data == 'topup':
        logger.info(f'Пользователь {user_id} вошел в пополнение баланса.')
        await call.message.edit_text('<strong>Выберите удобный способ пополнения баланса:</strong>',
                                     parse_mode='HTML', reply_markup=payment_keyboard)
        
    elif call.data == 'crypto':
        start = time.perf_counter()
        logger.info(f'Пользователь {user_id} вошел в криптокошелек.')
        await call.message.edit_text('🌐 <strong>Подключение к блокчейну.</strong>\n'
                                     '<i>Это может занять некоторое время...</i>', parse_mode='HTML')
        text = await main_page(call)
        await call.message.edit_text(text, parse_mode='HTML', reply_markup=crypto_keyboard,
                                     disable_web_page_preview=True)
        end = time.perf_counter()
        logger.info(f'Получение данных блокчейна для пользователя {user_id} заняло {end - start:.2f} сек.')
        
    elif call.data == 'Polygon':
        logger.info(f'Пользователь {user_id} выбрал сеть - {call.data}.')
        await state.clear()
        text = await polygon_mainnet(call)
        await call.message.edit_text(text, parse_mode='HTML', reply_markup=chains_keyboard('Polygon'),
                                     disable_web_page_preview=True)
        
    elif call.data == 'Arbitrum':
        logger.info(f'Пользователь {user_id} выбрал сеть - {call.data}.')
        await state.clear()
        text = await arbitrum_mainnet(call)
        await call.message.edit_text(text, parse_mode='HTML', reply_markup=chains_keyboard('Arbitrum'),
                                     disable_web_page_preview=True)
        
    elif call.data == 'Optimism':
        logger.info(f'Пользователь {user_id} выбрал сеть - {call.data}.')
        await state.clear()
        text = await optimism_mainnet(call)
        await call.message.edit_text(text, parse_mode='HTML', reply_markup=chains_keyboard('Optimism'),
                                     disable_web_page_preview=True)
        
    elif call.data == 'Base':
        logger.info(f'Пользователь {user_id} выбрал сеть - {call.data}.')
        await state.clear()
        text = await base_mainnet(call)
        await call.message.edit_text(text, parse_mode='HTML', reply_markup=chains_keyboard('Base'),
                                     disable_web_page_preview=True)
        
    elif 'confirm_funding_id' in call.data:
        await call.message.edit_text('🕓 <strong>Ожидание...</strong>', parse_mode='HTML')
        await try_to_fund(call)
        
    elif call.data == 'change_withdraw_address':
        logger.info(f'Пользователь {user_id} меняет адрес для вывода.')
        await state.set_state(CryptoPayments.address_withdraw_to)
        await try_another_address(call)
        
    elif 'withdrawal_confirmed_id' in call.data:
        await call.message.edit_text('🕓 <strong>Ожидание...</strong>', parse_mode='HTML')
        await try_to_withdraw(call)
        
    elif call.data == 'back':
        await call.message.edit_text('<strong>Выберите нужное действие:</strong>',
                                     parse_mode='HTML', reply_markup=menu_keyboard)
        
    elif call.data == 'YK':
        logger.info(f'Пользователь {user_id} вошел в пополнение ЮКасса')
        if user_id in pending_payments:
            del pending_payments[user_id]
            del pending_payments_info[user_id]
        await call.message.edit_text('<s><strong>Выберите сумму для оплаты или введите ее вручную:</strong>\n'
                                     '<i>Минимальная сумма для пополнения через ЮKassa — 60₽</i></s>\n\n'
                                     '<i>⛔️ На данный момент оплата этим способом недоступна! </i>',
                                     parse_mode='HTML', reply_markup=yk_payment_keyboard)
        # await state.set_state(CustomPaymentState.waiting_for_custom_rub_amount)
        
    elif call.data == 'stars':
        logger.info(f'Пользователь {user_id} вошел в пополнение Stars')
        if user_id in pending_payments:
            del pending_payments[user_id], pending_payments_info[user_id]
        await call.message.edit_text('<strong>Выберите сумму для оплаты или введите ее вручную:</strong>',
                                     parse_mode='HTML', reply_markup=stars_keyboard)
        await state.set_state(CustomPaymentState.waiting_for_custom_stars_amount)
    
    elif 'in_stars' in call.data:
        await payments.stars_payment(call, bot)
        
    elif 'in_rub' in call.data:
        await payments.rub_payment(call, bot)

