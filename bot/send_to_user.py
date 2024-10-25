from aiogram import Bot, Router
from aiogram.types import Message
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from logger import logger
from .main_bot import SendToFriend
from .bot_buttons import (try_again_amount_keyboard, step_back_keyboard, try_again_id_keyboard, 
                          skip_message_keyboard, confirm_sending_keyboard, try_again_message_keyboard)
from .main_bot import (id_generator, total_values, save_total, save_data, save_payments, 
                       users_payments_dict, users_data_dict, pending_sending_amount, pending_sending_id, 
                       pending_recieving_info, pending_sending_info, pending_sending_message, get_time)


router = Router()


# ВВОД СУММЫ ПЕРЕВОДА
async def amount_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_amount = message.text.replace(',', '.')
    user_data = users_data_dict[user_id]
    balance = user_data['Balance']
    
    logger.info(f'Пользователь {user_id} вводит сумму для перевода баланса.')
    
    try:
        amount = float(user_amount)
        amount = int(amount)
        await message.delete()
        if amount <= 0:
            await message.answer('<strong>⚠️ Сумма введена некорректно.</strong>\n<i>Нельзя отправить сумму '
                                 'меньше или равную нулю.</i>', parse_mode='HTML', reply_markup=try_again_amount_keyboard)
            await state.clear()
        elif int(balance) < amount:
            await message.answer('<strong>⚠️ У вас не хватает средств для перевода.</strong>\n<i>Уменьшите сумму '
                                 'или пополните баланс.</i>', parse_mode='HTML', reply_markup=try_again_amount_keyboard)
            await state.clear()
        else:
            pending_sending_amount[user_id] = amount
            await message.answer('<strong>👤 Введите ID пользователя для перевода.</strong>\n\n<i>Вам нужно ввести '
                                 'ID пользователя в числовом формате ниже:</i>', parse_mode='HTML',
                                 reply_markup=step_back_keyboard)
            await state.set_state(SendToFriend.id_input)

    except ValueError:
        await message.delete()
        await message.answer('<strong>⚠️ Сумма введена некорректно, попробуйте еще раз.</strong>',
                             parse_mode='HTML', reply_markup=try_again_amount_keyboard)
        await state.clear()


# ВВОД ID ПОЛУЧАТЕЛЯ
async def id_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_input = message.text

    logger.info(f'Пользователь {user_id} вводит ID для перевода баланса.')

    try:
        send_to = int(user_input)
        await message.delete()
        if send_to == user_id:
            await message.answer(
                '<strong>❌ Вы не можете совершить перевод самому себе, попробуйте еще раз.</strong>',
                parse_mode='HTML', reply_markup=try_again_id_keyboard)
            await state.clear()
        elif send_to not in users_data_dict:
            await message.answer(
                '<strong>⚠️ Пользователь не найден.</strong>\n\n<i>Пригласите пользователя или проверьте '
                'корректность ID.</i>', parse_mode='HTML', reply_markup=try_again_id_keyboard)
            await state.clear()
        elif not users_data_dict[send_to]['Is_verified']:
            await message.answer('<strong>⚠️ Пользователь не авторизован.</strong>\n\n<i>Вы можете самостоятельно попросить '
                'пользователя пройти авторизацию.</i>', parse_mode='HTML', reply_markup=try_again_id_keyboard)
            await state.clear()
        else:
            pending_sending_id[user_id] = send_to
            await state.set_state(SendToFriend.message_input)
            await message.answer(f'📩 <strong>Вы можете ввести сообщение для пользователя.'
                                 f'</strong>\n<i>Обратите внимаение, что любые премиум-эмодзи, к сожалению, будут '
                                 f'преобразованы в обычные.</i>\n\n<i>Введите ваше текстовое сообщение ниже:</i>',
                                 parse_mode='HTML', reply_markup=skip_message_keyboard)
    except ValueError:
        await message.delete()
        await message.answer('<strong>⚠️ ID введен некорректно, попробуйте еще раз.</strong>',
                             parse_mode='HTML', reply_markup=try_again_id_keyboard)
        await state.clear()


# ВВОД СООБЩЕНИЯ ДЛЯ ПОЛУЧАТЕЛЯ
async def message_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_input = message.text

    logger.info(f'Пользователь {user_id} вводит сообщение при перевода баланса.')

    if user_input is not None:
        try:
            send_message = str(user_input)
            pending_sending_message[user_id] = send_message
            await message.delete()
            await message.answer(f'<strong>Вы переводите: <code>{pending_sending_amount[user_id]}₽</code>\nПользователю '
                                f'под ID: <code>{pending_sending_id[user_id]}</code>\nВаше сообщение:</strong> '
                                f'{pending_sending_message[user_id]}\n\n<strong>Подтверждаете?</strong>',
                                parse_mode='HTML', reply_markup=confirm_sending_keyboard)
            
        except:
            await message.answer('<strong>❌ Некорректное сообщение, попробуйте еще раз!</strong>', parse_mode='HTML',
                                reply_markup=try_again_message_keyboard)
            await state.clear()
    else:
        await message.delete()
        await message.answer('<strong>❌ Некорректное сообщение, попробуйте еще раз!</strong>', parse_mode='HTML',
                                reply_markup=try_again_message_keyboard)
        await state.clear()
    await state.clear()


# ПЕРЕВОД БАЛАНСА
async def send_to_user(call: CallbackQuery, bot: Bot, state: FSMContext):
    user_id = call.from_user.id
    user_data = users_data_dict[user_id]
    
    reciever_id = pending_sending_id[user_id]
    reciever_data = users_data_dict[reciever_id]
    
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
                                                 'USD': 0,
                                                 'transaction_num': trx_num,
                                                 'type': sender_info, 'trx_id': trx_sender_id}}
            await save_payments()
        else:
            sender_payments[today][time_now] = {'RUB': amount,
                                                'USD': 0,
                                                'transaction_num': trx_num,
                                                'type': sender_info, 'trx_id': trx_sender_id}
            await save_payments()
        if today not in reciever_payments:
            reciever_payments[today] = {time_now: {'RUB': amount,
                                                   'USD': 0,
                                                   'transaction_num': trx_num,
                                                   'type': reciever_info, 'trx_id': trx_reciever_id}}
            await save_payments()
        else:
            reciever_payments[today][time_now] = {'RUB': amount,
                                                  'USD': 0,
                                                  'transaction_num': trx_num,
                                                  'type': reciever_info, 'trx_id': trx_reciever_id}
            await save_payments()

        if pending_sending_message[user_id] is not None:
            await bot.send_message(chat_id=reciever_id,
                                   text=f'<strong>🎉 Пополнение баланса от другого пользователя!</strong>\n\n'
                                        f'<i>🥷 Перевод от пользователя под ID: <code>{user_id}</code>\n💰 Сумма перевода: '
                                        f'<code>{amount}₽</code>\n📨 Сообщение от пользователя:</i>\n\n{pending_sending_message[user_id]}',
                                   parse_mode='HTML')
        else:
            await bot.send_message(chat_id=reciever_id,
                                   text=f'<strong>🎉 Пополнение баланса от другого пользователя!</strong>\n\n'
                                        f'<i>🥷 Перевод от пользователя под ID: <code>{user_id}</code>\n💰 Сумма перевода: '
                                        f'<code>{amount}₽</code></i>', parse_mode='HTML')

    logger.info(f'Пользователь {user_id} успешно совершил перевод для {reciever_id}.')
    logger.info(f'Пользователь {reciever_id} получил перевод от {user_id}.')

    del (pending_sending_amount[user_id], pending_sending_message[user_id], pending_sending_id[user_id],
         pending_sending_info[user_id], pending_recieving_info[reciever_id])
