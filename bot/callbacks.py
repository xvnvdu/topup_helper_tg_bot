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
from crypto.swap.main_swap import try_to_swap, tokens_approved, swap_details
from crypto.wallet_page_maker import main_page, polygon_mainnet, arbitrum_mainnet, optimism_mainnet, base_mainnet

from . import payments
from .send_to_user import send_to_user
from .support.rules import support_rules
from .transactions_log import sorted_payments
from .support.admin_side import cancel_answer
from .support.user_side import cancel_application, bot_support
from .interface_language.core import select_language, change_language, phrases
from .main_bot import (users_data_dict, users_payments_dict, CustomPaymentState, SendToFriend, pending_sending_amount, 
                       Support, pending_sending_id, pending_sending_message, pending_payments, pending_payments_info, change_user_data)
from .bot_buttons import (menu_keyboard, account_keyboard, payment_keyboard, crypto_keyboard, back_to_support_keyboard, stars_keyboard, 
                          yk_payment_keyboard, zero_transactions_keyboard, skip_message_keyboard, log_buttons, back_to_account_keyboard, 
                          step_back_keyboard, confirm_sending_keyboard, chains_keyboard, successful_approve)


''' ОСНОВНЫЕ КОЛЛБЭКИ ОТ КНОПОК '''

async def main_callbacks(call: CallbackQuery, bot: Bot, state: FSMContext):
    user_id = call.from_user.id
    user_data = users_data_dict[user_id]
    lang = user_data['Language']
    lang_settings = phrases(lang)

    await change_user_data(None, call, user_data)

    current_page = await state.get_data()
    current_page = current_page.get('current_page', 0)
    trx_log = await sorted_payments(call, lang)
    total_pages = math.ceil((len(trx_log)-1) / 15)
    first_page_line = current_page * 15
    last_page_line = first_page_line + 15
    page_text = '\n'.join(trx_log[first_page_line:last_page_line])

    if call.data == 'account':
        logger.info(f'Пользователь {user_id} вошел в аккаунт.')
        
        phone = int(user_data['Phone']) // 10**4
        balance = user_data['Balance']
        registration_date = user_data['Registration']
        volume = user_data['Funding_volume']

        days_count = (datetime.now() - datetime.strptime(registration_date, '%d.%m.%Y')).days
        if days_count % 10 == 1 and days_count % 100 != 11:
            days = 'день' if lang == 'RU' else 'days'
        elif days_count % 10 in [2, 3, 4] and not (11 <= days_count % 100 <= 19):
            days = 'дня' if lang == 'RU' else 'days'
        else:
            days = 'дней' if lang == 'RU' else 'days'
            
        await call.message.edit_text(f'{lang_settings.my_profile}\n\n'
                                     f'⚙️ <strong>ID:</strong> <code>{call.from_user.id}</code>\n'
                                     f'🔒 {lang_settings.phone} <code>{phone}****</code>\n'
                                     f'🗓 {lang_settings.registration} <code>{registration_date} ({days_count} {days})</code>\n\n'
                                     f'💵 {lang_settings.my_balance} <code>{balance}₽</code>\n'
                                     f'💎 {lang_settings.my_funding_volume} <code>{volume}₽</code>',
                                     parse_mode='HTML', reply_markup=account_keyboard(lang))
        
    elif call.data == 'language':
        logger.info(f'Пользователь {user_id} вошел в смену языка.')
        await select_language(call, lang)
        
    elif call.data == 'lang_ru':
        logger.info(f'Пользователь {user_id} изменил язык на русский.')
        await call.message.edit_text('<b>✅ Готово!</b>\n\n<i>🇷🇺 Язык интерфейса изменен на русский.</i>', parse_mode='HTML')
        await change_language(call, 'RU')
        await call.message.answer('<b>Выберите нужное действие:</b>', parse_mode='HTML', reply_markup=menu_keyboard('RU'))
    
    elif call.data == 'lang_en':
        logger.info(f'Пользователь {user_id} изменил язык на английский.')
        await call.message.edit_text('✅ Done!\n\n<i>🇺🇸 Interface language changed to English</i>', parse_mode='HTML')
        await change_language(call, 'EN')
        await call.message.answer('<b>Choose an option:</b>', parse_mode='HTML', reply_markup=menu_keyboard('EN'))
        
    elif call.data == 'support':
        logger.info(f'Пользователь {user_id} вошел в поддержку.')
        await bot_support(call)
        await state.clear()
        
    elif call.data == 'message_to_support':
        logger.info(f'Пользователь {user_id} собирается отправить сообщение в поддержку.')
        await call.message.edit_text(lang_settings.describe_problem, parse_mode='HTML', reply_markup=back_to_support_keyboard(lang))
        await state.set_state(Support.message_to_support)
        
    elif call.data == 'support_rules':
        logger.info(f'Пользователь {user_id} вошел в правила поддержки.')
        await support_rules(call, lang)
    
    elif 'cancel_answer' in call.data:
        await cancel_answer(call, state)
        
    elif 'cancel_application' in call.data:
        await cancel_application(call, state)
    
    elif call.data == 'transactions':
        logger.info(f'Пользователь {user_id} вошел в лог транзакций.')
        if not users_payments_dict[user_id]['Transactions']:
            await call.message.edit_text(lang_settings.no_transactions_yet,
                                         parse_mode='HTML', reply_markup=zero_transactions_keyboard(lang))
        else:
            current_page = 0
            await state.update_data(current_page=current_page)
            await log_buttons(call, page_text, current_page, total_pages, lang)
            
    elif call.data == 'next_page':
        current_page += 1
        await state.update_data(current_page=current_page)
        first_page_line = current_page * 15
        last_page_line = first_page_line + 15
        page_text = '\n'.join(trx_log[first_page_line:last_page_line])
        await log_buttons(call, page_text, current_page, total_pages, lang)
        
    elif call.data == 'prev_page':
        current_page -= 1
        await state.update_data(current_page=current_page)
        first_page_line = current_page * 15
        last_page_line = first_page_line + 15
        page_text = '\n'.join(trx_log[first_page_line:last_page_line])
        await log_buttons(call, page_text, current_page, total_pages, lang)
        
    elif call.data == 'send':
        logger.info(f'Пользователь {user_id} вошел в перевод баланса.')
        await call.message.edit_text(lang_settings.send_to_friend_main_page, parse_mode='HTML', reply_markup=back_to_account_keyboard(lang))
        await state.set_state(SendToFriend.amount_input)
        
    elif call.data == 'choose_id':
        logger.info(f'Пользователь {user_id} вводит ID для перевода баланса.')
        await call.message.edit_text(lang_settings.send_to_friend_choose_id, parse_mode='HTML', reply_markup=step_back_keyboard(lang))
        await state.set_state(SendToFriend.id_input)
        
    elif call.data == 'message_input':
        logger.info(f'Пользователь {user_id} вводит сообщение при перевода баланса.')
        await state.set_state(SendToFriend.message_input)
        await call.message.edit_text(lang_settings.send_to_friend_message_input, parse_mode='HTML', reply_markup=skip_message_keyboard(lang))
        
    elif call.data == 'confirm_sending':
        logger.info(f'Пользователь {user_id} собирается сделать перевод баланса.')
        await state.clear()
        pending_sending_message[user_id] = None
        await call.message.answer(f'{lang_settings.you_transfer} <code>{pending_sending_amount[user_id]}₽</code>\n'
                             f'{lang_settings.to_user_with_id} <code>{pending_sending_id[user_id]}</code>\n\n'
                             f'{lang_settings.do_you_confirm}', parse_mode='HTML', reply_markup=confirm_sending_keyboard(lang))
        
    elif call.data == 'sending_confirmed':
        logger.info(f'Пользователь {user_id} успешно перевел баланс.')
        await send_to_user(call, bot, state)
        await call.message.edit_text(lang_settings.send_to_friend_sending_confirmed,  
                                     parse_mode='HTML', reply_markup=back_to_account_keyboard(lang))
        
    elif call.data == 'topup':
        logger.info(f'Пользователь {user_id} вошел в пополнение баланса.')
        await call.message.edit_text(lang_settings.choose_topup_method, parse_mode='HTML', reply_markup=payment_keyboard(lang))
        
    elif call.data == 'crypto':
        start = time.perf_counter()
        logger.info(f'Пользователь {user_id} вошел в криптокошелек.')
        await call.message.edit_text(lang_settings.connecting_to_blockchain, parse_mode='HTML')
        text = await main_page(call, lang)
        await call.message.edit_text(text, parse_mode='HTML', reply_markup=crypto_keyboard(lang),
                                     disable_web_page_preview=True)
        end = time.perf_counter()
        logger.info(f'Получение данных блокчейна для пользователя {user_id} заняло {end - start:.2f} сек.')
        
    elif call.data == 'Polygon':
        logger.info(f'Пользователь {user_id} выбрал сеть - {call.data}.')
        await state.clear()
        text = await polygon_mainnet(call)
        await call.message.edit_text(text, parse_mode='HTML', reply_markup=chains_keyboard('Polygon', lang),
                                     disable_web_page_preview=True)
        
    elif call.data == 'Arbitrum':
        logger.info(f'Пользователь {user_id} выбрал сеть - {call.data}.')
        await state.clear()
        text = await arbitrum_mainnet(call)
        await call.message.edit_text(text, parse_mode='HTML', reply_markup=chains_keyboard('Arbitrum', lang),
                                     disable_web_page_preview=True)
        
    elif call.data == 'Optimism':
        logger.info(f'Пользователь {user_id} выбрал сеть - {call.data}.')
        await state.clear()
        text = await optimism_mainnet(call)
        await call.message.edit_text(text, parse_mode='HTML', reply_markup=chains_keyboard('Optimism', lang),
                                     disable_web_page_preview=True)
        
    elif call.data == 'Base':
        logger.info(f'Пользователь {user_id} выбрал сеть - {call.data}.')
        await state.clear()
        text = await base_mainnet(call)
        await call.message.edit_text(text, parse_mode='HTML', reply_markup=chains_keyboard('Base', lang),
                                     disable_web_page_preview=True)
        
    elif 'confirm_funding_id' in call.data:
        await call.message.edit_text(lang_settings.waiting, parse_mode='HTML')
        await try_to_fund(call)
        
    elif call.data == 'change_withdraw_address':
        logger.info(f'Пользователь {user_id} меняет адрес для вывода.')
        await state.set_state(CryptoPayments.address_withdraw_to)
        await try_another_address(call)
        
    elif 'withdrawal_confirmed_id' in call.data:
        await call.message.edit_text(lang_settings.waiting, parse_mode='HTML')
        await try_to_withdraw(call)
        
    elif call.data == 'approve_allowance':
        await tokens_approved(call)
        
    elif call.data.startswith('go_to_swap'):
        today = str(call.data).split('_')[3]
        time_now = str(call.data).split('_')[4]
        trx_hash = users_payments_dict[user_id]['Transactions'][today][time_now]['hash']
        explorer = users_payments_dict[user_id]['Transactions'][today][time_now]['explorer']
        exp_link = users_payments_dict[user_id]['Transactions'][today][time_now]['explorer_link']
        
        await call.message.edit_text(f'{lang_settings.approve_sent}\n\n'
                                f'{lang_settings.hash_approve} <pre>{trx_hash}</pre>', parse_mode='HTML', 
                                reply_markup=successful_approve(exp_link, explorer, None, False, today, time_now, lang),
                                disable_web_page_preview=True)
        await swap_details(call, None, False, None, None)
    
    elif 'confirmed_swap_id' in call.data:
        await call.message.edit_text(lang_settings.waiting, parse_mode='HTML')
        await try_to_swap(call)
    
    elif call.data == 'back':
        await call.message.edit_text(lang_settings.choose_an_option, parse_mode='HTML', reply_markup=menu_keyboard(lang))
        
    elif call.data == 'YK':
        logger.info(f'Пользователь {user_id} вошел в пополнение ЮКасса')
        if user_id in pending_payments:
            del pending_payments[user_id]
            del pending_payments_info[user_id]
        await call.message.edit_text(lang_settings.choose_yookassa_amount, parse_mode='HTML', reply_markup=yk_payment_keyboard(lang))
        # await state.set_state(CustomPaymentState.waiting_for_custom_rub_amount)
        
    elif call.data == 'stars':
        logger.info(f'Пользователь {user_id} вошел в пополнение Stars')
        if user_id in pending_payments:
            del pending_payments[user_id], pending_payments_info[user_id]
        await call.message.edit_text(lang_settings.choose_stars_amount, parse_mode='HTML', reply_markup=stars_keyboard(lang))
        await state.set_state(CustomPaymentState.waiting_for_custom_stars_amount)
    
    elif 'in_stars' in call.data:
        await payments.stars_payment(call, bot, lang)
        
    elif 'in_rub' in call.data:
        await payments.rub_payment(call, bot, lang)

