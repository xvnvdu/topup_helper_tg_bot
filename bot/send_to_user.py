from aiogram import Bot, Router
from aiogram.types import Message
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from logger import logger
from .main_bot import SendToFriend
from .interface_language.core import phrases
from .bot_buttons import (try_again_amount_keyboard, step_back_keyboard, try_again_id_keyboard, 
                          skip_message_keyboard, confirm_sending_keyboard, try_again_message_keyboard)
from .main_bot import (id_generator, total_values, save_total, save_data, save_payments, 
                       users_payments_dict, users_data_dict, pending_sending_amount, pending_sending_id, 
                       pending_recieving_info, pending_sending_info, pending_sending_message, get_time)


router = Router()


''' ВВОД СУММЫ ПЕРЕВОДА '''

async def amount_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_amount = message.text.replace(',', '.')
    user_data = users_data_dict[user_id]
    balance = user_data['Balance']
    lang = user_data['Language']
    lang_settings = phrases(lang)
    
    logger.info(f'Пользователь {user_id} вводит сумму для перевода баланса.')
    
    try:
        amount = float(user_amount)
        amount = int(amount)
        await message.delete()
        if amount <= 0:
            await message.answer(lang_settings.less_than_zero, parse_mode='HTML', reply_markup=try_again_amount_keyboard(lang))
            await state.clear()
        elif int(balance) < amount:
            await message.answer(lang_settings.not_enough_funds, parse_mode='HTML', reply_markup=try_again_amount_keyboard(lang))
            await state.clear()
        else:
            pending_sending_amount[user_id] = amount
            await message.answer(lang_settings.send_to_friend_choose_id, parse_mode='HTML', reply_markup=step_back_keyboard(lang))
            await state.set_state(SendToFriend.id_input)

    except ValueError:
        await message.delete()
        await message.answer(lang_settings.incorrect_amount, parse_mode='HTML', reply_markup=try_again_amount_keyboard(lang))
        await state.clear()


''' ВВОД ID ПОЛУЧАТЕЛЯ '''

async def id_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = users_data_dict[user_id]
    lang = user_data['Language']
    lang_settings = phrases(lang)
    user_input = message.text

    logger.info(f'Пользователь {user_id} вводит ID для перевода баланса.')

    try:
        send_to = int(user_input)
        await message.delete()
        if send_to == user_id:
            await message.answer(lang_settings.transfer_to_yourself, parse_mode='HTML', reply_markup=try_again_id_keyboard(lang))
            await state.clear()
        elif send_to not in users_data_dict:
            await message.answer(lang_settings.user_not_found, parse_mode='HTML', reply_markup=try_again_id_keyboard(lang))
            await state.clear()
        elif not users_data_dict[send_to]['Is_verified']:
            await message.answer(lang_settings.user_not_authorized, parse_mode='HTML', reply_markup=try_again_id_keyboard(lang))
            await state.clear()
        else:
            pending_sending_id[user_id] = send_to
            await state.set_state(SendToFriend.message_input)
            await message.answer(lang_settings.send_to_friend_message_input, parse_mode='HTML', reply_markup=skip_message_keyboard(lang))
    except ValueError:
        await message.delete()
        await message.answer(lang_settings.incorrect_id, parse_mode='HTML', reply_markup=try_again_id_keyboard(lang))
        await state.clear()


''' ВВОД СООБЩЕНИЯ ДЛЯ ПОЛУЧАТЕЛЯ '''

async def message_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = users_data_dict[user_id]
    lang = user_data['Language']
    lang_settings = phrases(lang)
    user_input = message.text

    logger.info(f'Пользователь {user_id} вводит сообщение при перевода баланса.')

    if user_input is not None:
        try:
            send_message = str(user_input)
            pending_sending_message[user_id] = send_message
            await message.delete()
            await message.answer(f'{lang_settings.you_transfer} <code>{pending_sending_amount[user_id]}₽</code>\n'
                                 f'{lang_settings.to_user_with_id} <code>{pending_sending_id[user_id]}</code>\n'
                                 f'{lang_settings.your_message} {pending_sending_message[user_id]}\n\n'
                                 f'{lang_settings.do_you_confirm}', parse_mode='HTML', reply_markup=confirm_sending_keyboard(lang))
            
        except:
            await message.answer(lang_settings.incorrect_message, parse_mode='HTML', reply_markup=try_again_message_keyboard(lang))
            await state.clear()
    else:
        await message.delete()
        await message.answer(lang_settings.incorrect_message, parse_mode='HTML', reply_markup=try_again_message_keyboard(lang))
        await state.clear()
    await state.clear()


''' ПЕРЕВОД БАЛАНСА '''

async def send_to_user(call: CallbackQuery, bot: Bot, state: FSMContext):
    user_id = call.from_user.id
    user_data = users_data_dict[user_id]
        
    reciever_id = pending_sending_id[user_id]
    reciever_data = users_data_dict[reciever_id]
    
    lang = reciever_data['Language']
    lang_settings = phrases(lang)
    
    user_data['Balance'] = int(user_data['Balance'])
    reciever_data['Balance'] = int(reciever_data['Balance'])

    amount = pending_sending_amount[user_id]
    amount = int(amount)

    pending_sending_info[user_id] = f' Перевод баланса — ID: <code>{reciever_id}</code>'
    pending_recieving_info[reciever_id] = f' Пополнение баланса — ID: <code>{user_id}</code>'
    sender_info = pending_sending_info[user_id]
    reciever_info = pending_recieving_info[reciever_id]

    sender_payments = users_payments_dict[user_id]['Transactions']
    reciever_payments = users_payments_dict[reciever_id]['Transactions']

    if call.from_user.id in pending_sending_amount:
        trx_sender_id = await id_generator()
        trx_reciever_id = await id_generator()
        total_values['Total_transactions_count'] += 1
        trx_num = total_values['Total_transactions_count']
        user_data['Balance'] -= amount
        reciever_data['Balance'] += amount

        await save_total()
        await save_data()

        today, time_now = await get_time()
        if today not in sender_payments:
            sender_payments[today] = {time_now: {'RUB': amount,
                                                 'USD': None,
                                                 'transaction_num': trx_num,
                                                 'type': sender_info,
                                                 'explorer': None,
                                                'explorer_link': None,
                                                 'hash': None, 
                                                 'trx_id': trx_sender_id}}
            await save_payments()
        else:
            sender_payments[today][time_now] = {'RUB': amount,
                                                'USD': None,
                                                'transaction_num': trx_num,
                                                'type': sender_info, 
                                                'explorer': None,
                                                'explorer_link': None,
                                                'hash': None, 
                                                'trx_id': trx_sender_id}
            await save_payments()
        if today not in reciever_payments:
            reciever_payments[today] = {time_now: {'RUB': amount,
                                                   'USD': None,
                                                   'transaction_num': trx_num,
                                                   'type': reciever_info, 
                                                   'explorer': None,
                                                   'explorer_link': None,
                                                   'hash': None, 
                                                   'trx_id': trx_reciever_id}}
            await save_payments()
        else:
            reciever_payments[today][time_now] = {'RUB': amount,
                                                  'USD': None,
                                                  'transaction_num': trx_num,
                                                  'type': reciever_info, 
                                                  'explorer': None,
                                                  'explorer_link': None,
                                                  'hash': None, 
                                                  'trx_id': trx_reciever_id}
            await save_payments()

        if pending_sending_message[user_id] is not None:
            await bot.send_message(chat_id=reciever_id,
                                   text=f'{lang_settings.recieved_transfer}'
                                        f'{lang_settings.transfer_from_user_id} <code>{user_id}</code>\n{lang_settings.transfer_amount} '
                                        f'<code>{amount}₽</code>\n{lang_settings.message_from_user}\n\n{pending_sending_message[user_id]}',
                                   parse_mode='HTML')
        else:
            await bot.send_message(chat_id=reciever_id,
                                   text='{lang_settings.recieved_transfer}'
                                        f'{lang_settings.transfer_from_user_id} <code>{user_id}</code>\n{lang_settings.transfer_amount} '
                                        f'<code>{amount}₽</code>', parse_mode='HTML')

    logger.info(f'Пользователь {user_id} успешно совершил перевод для {reciever_id}.')
    logger.info(f'Пользователь {reciever_id} получил перевод от {user_id}.')

    del (pending_sending_amount[user_id], pending_sending_message[user_id], pending_sending_id[user_id],
         pending_sending_info[user_id], pending_recieving_info[reciever_id])
