import time
from datetime import datetime
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.handlers import CallbackQueryHandler
from aiogram import F, Router, types, Bot
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, PreCheckoutQuery, CallbackQuery

from crypto.fund_wallet import fund
from crypto.wallet_page_maker import main_page
from crypto.withdraw_wallet import address_input, buttons_withdraw_handler, withdraw_choice, amount_to_withdraw
from crypto.main_crypto import create_new_wallet, CryptoPayments, pending_chain_fund, ok_to_fund, ok_to_withdraw

from .callbacks import main_callbacks
from .payments import rub_custom, stars_custom
from .send_to_user import amount_input, id_input, message_input
from .main_bot import (users_data, users_payments, users_data_dict, users_payments_dict,
                  save_data, save_payments, total_values, save_total, id_generator, CustomPaymentState, 
                  SendToFriend, pending_payments, pending_payments_info, get_time)
from .bot_buttons import (menu_keyboard, account_keyboard, payment_keyboard, crypto_keyboard, withdraw_crypto, back_to_chain_keyboard)


router = Router()


@router.message(Command('menu'))
async def command_menu(message: Message):
    user_id = message.from_user.id
    user_data = users_data_dict[user_id]
    print(f'Пользователь {user_id} воспользовался командой меню')
    if user_data['Is_verified']:
        await message.answer( '<strong>Выберите нужное действие:</strong>',
                         parse_mode='HTML', reply_markup=menu_keyboard)
    else:
        await confirm_phone(message)


@router.message(Command('account'))
async def command_account(message: Message):
    user_id = message.from_user.id
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
    print(f'Пользователь {user_id} воспользовался командой аккаунт')
    if user_data['Is_verified']:
        await message.answer(f'<strong>Мой аккаунт</strong>\n\n'
                             f'⚙️ <strong>ID:</strong> <code>{message.from_user.id}</code>\n'
                             f'🔒 <strong>Телефон:</strong> <code>{phone}****</code>\n'
                             f'🗓 <strong>Регистрация:</strong> <code>{registration_date} ({days_count} {days})</code>\n\n'
                             f'💵 <strong>Мой баланс: </strong><code>{balance}₽</code>\n'
                             f'💎 <strong>Мои пополнения за все время: </strong><code>{volume}₽</code>',
                             parse_mode='HTML', reply_markup=account_keyboard)
    else:
        await confirm_phone(message)


@router.message(Command('balance'))
async def command_balance(message: Message):
    user_id = message.from_user.id
    user_data = users_data_dict.get(user_id)
    print(f'Пользователь {user_id} воспользовался командой баланс')
    if user_data['Is_verified']:
        await message.answer('<strong>Выберите удобный способ пополнения баланса:</strong>', 
                             parse_mode='HTML', reply_markup=payment_keyboard)
    else:
        await confirm_phone(message)


@router.message(Command('crypto'))
async def command_crypto(message: Message, bot: Bot):
    user_id = message.from_user.id
    user_data = users_data_dict[user_id]
    print(f'Пользователь {user_id} воспользовался командой вывести')
    call = CallbackQuery(id='fake_id', from_user=message.from_user,
                         message=message, chat_instance='')
    if user_data['Is_verified']:
        start = time.perf_counter()
        connection_await = await message.answer('🌐 <strong>Подключение к блокчейну.</strong>\n'
                                                '<i>Это может занять некоторое время...</i>', parse_mode='HTML')
        text = await main_page(call)
        await bot.delete_message(chat_id=message.chat.id, message_id=connection_await.message_id)
        await message.answer(text, parse_mode='HTML', reply_markup=crypto_keyboard,
                             disable_web_page_preview=True)
        end = time.perf_counter()
        print(f'{end - start:.2f}')
    else:
        await confirm_phone(message)


@router.message(Command('start'))
async def start(message: Message):
    user_id = message.from_user.id
    user = {'ID': user_id, 'Name': message.from_user.first_name,
            'Surname': message.from_user.last_name,
            'Username': message.from_user.username, 'Phone': None,
            'Is_verified': False, 'Registration': None, 'Balance': 0,
            'Funding_volume': 0}
    user_payments = {'ID': user_id,
                     'Transactions': {}
    }
    print(f'Пользователь {user_id} воспользовался командой старт')
    if user_id not in users_data_dict:
        total_values['Total_users'] += 1
        await message.answer('Привет! 🤖\nКак ты мог заметить, с некоторых сайтов '
                             'пропало несколько, либо вообще все способы пополнения баланса, '
                             'кроме криптовалют.\nНе волнуйся, я создан, '
                             'чтобы помочь тебе с пополнением, в том случае, '
                             'если у тебя нет биржи или кошелька, с которых ты мог '
                             'бы пополнять баланс самостоятельно! 🤩')
        users_data.append(user)
        users_payments.append(user_payments)
        await save_data()
        await save_payments()
        await save_total()
        users_payments_dict[user_id] = user_payments
        users_data_dict[user_id] = user

    user_data = users_data_dict[user_id]

    if not user_data['Is_verified']:
        await confirm_phone(message)
    else:
        await command_menu(message)


@router.pre_checkout_query()
async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    user_id = message.from_user.id
    user_data = users_data_dict[user_id]
    user_payment = users_payments_dict[user_id]['Transactions']
    await message.answer('<strong>Оплата успешная 🎉</strong>\n<i>Примечание: '
                         'не используйте одну и ту же ссылку на пополнение дважды, '
                         'ваша оплата не будет засчитана!</i>', parse_mode='HTML')
    if message.from_user.id in pending_payments:
        amount = pending_payments[user_id]
        trx_type = pending_payments_info[user_id]
        trx_id = await id_generator()
        total_values['Total_topups_count'] += 1
        total_values['Total_topups_volume'] += amount
        total_values['Total_transactions_count'] += 1
        trx_num = total_values['Total_transactions_count']
        user_data['Balance'] += amount
        user_data['Funding_volume'] += amount
        
        await save_total()
        await save_data()
        
        today, time_now = await get_time()
        if today not in user_payment:
            user_payment[today] = {time_now: {'RUB': amount,
                                              'USD': 0,
                                              'transaction_num': trx_num,
                                              'type': trx_type, 'trx_id': trx_id}}
            await save_payments()
        else:
            user_payment[today][time_now] = {'RUB': amount,
                                             'USD': 0, 
                                             'transaction_num': trx_num, 
                                             'type': trx_type, 'trx_id': trx_id}
            await save_payments()
        del pending_payments_info[user_id]
        del pending_payments[user_id]


@router.message(F.contact)
async def check_contact(message: Message):
    user_id = message.from_user.id

    if message.contact is not None and message.contact.user_id == user_id:
        user_data = users_data_dict[user_id]
        user_data['Phone'] = message.contact.phone_number
        user_data['Is_verified'] = True
        user_data['Registration'] = time.strftime('%d.%m.%Y')
        (user_data['Wallet_address'],
         user_data['Private_key']) = await create_new_wallet()
        total_values['Total_verified_users'] += 1
        await save_total()
        await save_data()
        remove_button = types.ReplyKeyboardRemove()
        await message.answer('<b>Номер телефона успешно подтвержден!</b> 🎉\n'
                             'Вы можете пользоваться ботом.', parse_mode='HTML',
                             reply_markup=remove_button)
        await command_menu(message)
    else:
        await confirm_phone(message)


@router.callback_query(lambda call: call.data.endswith('_fund'))
async def callback_fund_crypto(call: CallbackQueryHandler, state: FSMContext):
    await state.set_state(CryptoPayments.fund_wallet)
    user_id = call.from_user.id
    user_data = users_data_dict[user_id]
    balance_rub = user_data["Balance"]
    
    ok_to_fund[user_id] = False

    chain = str(call.data).split('_')[0]
    pending_chain_fund[user_id] = chain
    await call.message.edit_text(f'<strong>💵 Мой баланс:</strong> <code>{balance_rub}₽</code>\n\n'
                                 f'<i>Обратите внимание, что в любой транзакции для оплаты комиссий '
                                 f'сети используется нативная монета этой сети, поэтому пополнение '
                                 f'кошелька в боте происходит только в нативных монетах. Для пополнения '
                                 f'введите сумму в рублях:</i>', parse_mode='HTML', reply_markup=back_to_chain_keyboard(chain))


@router.message(CryptoPayments.fund_wallet)
async def fund_handler(message: Message, state: FSMContext):
    await fund(message, state)
    

@router.callback_query(lambda call: call.data.endswith('_withdraw'))
async def callback_withdraw_crypto(call: CallbackQueryHandler):
    user_id = call.from_user.id
    
    ok_to_withdraw[user_id] = False
    
    chain = str(call.data).split('_')[0]
    await call.message.edit_text('💱 <strong>Выберите монету для вывода:</strong>',
                                 parse_mode='HTML', reply_markup=withdraw_crypto(chain))


@router.callback_query(lambda call: call.data.startswith('withdraw_'))
async def callback_currency_withdraw(call: CallbackQueryHandler, state: FSMContext):
    await state.set_state(CryptoPayments.amount_to_withdraw)
    await withdraw_choice(call)


@router.callback_query(lambda call: 'percent' in call.data)
async def callback_currency_withdraw(call: CallbackQueryHandler, state: FSMContext):
    await buttons_withdraw_handler(call)
    await state.set_state(CryptoPayments.address_withdraw_to)
    

@router.message(CryptoPayments.amount_to_withdraw)
async def withdraw_amount(message: Message, state: FSMContext):
    await amount_to_withdraw(message, state)


@router.message(CryptoPayments.address_withdraw_to)
async def withdraw_handler(message: Message, state: FSMContext):
    await address_input(message, state)


@router.callback_query(lambda call: call.data.endswith('_swap'))
async def callback_swap_crypto(call: CallbackQueryHandler):
    chain = str(call.data).split('_')[0]
    await call.message.edit_text('⚠️ Этот раздел находится в разработке...', reply_markup=back_to_chain_keyboard(chain))


@router.callback_query(lambda call: call.data.endswith('_bridge'))
async def callback_bridge_crypto(call: CallbackQueryHandler):
    chain = str(call.data).split('_')[0]
    await call.message.edit_text('⚠️ Этот раздел находится в разработке...', reply_markup=back_to_chain_keyboard(chain))



@router.callback_query()
async def callback_handler(call: CallbackQueryHandler, bot: Bot, state: FSMContext):
    await main_callbacks(call, bot, state)


@router.message(SendToFriend.amount_input)
async def amount_input_handler(message: Message, state: FSMContext):
    await amount_input(message, state)


@router.message(SendToFriend.id_input)
async def id_input_handler(message: Message, state: FSMContext):
    await id_input(message, state)


@router.message(SendToFriend.message_input)
async def message_input_handler(message: Message, state: FSMContext):
    await message_input(message, state)
    


@router.message(CustomPaymentState.waiting_for_custom_rub_amount)
async def process_custom_rub_amount(message: Message, bot: Bot, state: FSMContext):
    user_id = message.from_user.id
    user_input = message.text.replace(',', '.')
    try:
        amount = float(user_input)
        amount = int(amount)
        if amount >= 60:
            pending_payments[user_id] = amount
            pending_payments_info[user_id] = 'Пополнение баланса — ЮKassa'
            await message.delete()
            await rub_custom(message, bot, state)
        else:
            await message.delete()
            await message.answer('<strong>Выберите удобный способ пополнения баланса:</strong>',
                                 parse_mode='HTML', reply_markup=payment_keyboard)
    except ValueError:
        await message.delete()
        await message.answer('<strong>Выберите удобный способ пополнения баланса:</strong>',
                                     parse_mode='HTML', reply_markup=payment_keyboard)
    await state.clear()


@router.message(CustomPaymentState.waiting_for_custom_stars_amount)
async def process_custom_stars_amount(message: Message, bot: Bot, state: FSMContext):
    user_id = message.from_user.id
    user_input = message.text.replace(',', '.')
    try:
        amount = float(user_input)
        amount = int(amount)
        if amount > 0:
            pending_payments[user_id] = amount
            pending_payments_info[user_id] = 'Пополнение баланса — Stars'
            await message.delete()
            await stars_custom(message, bot, state)
        else:
            await message.delete()
            await message.answer('<strong>Выберите удобный способ пополнения баланса:</strong>',
                                 parse_mode='HTML', reply_markup=payment_keyboard)
    except ValueError:
        await message.delete()
        await message.answer('<strong>Выберите удобный способ пополнения баланса:</strong>',
                                     parse_mode='HTML', reply_markup=payment_keyboard)
    await state.clear()


@router.message()
async def any_message(message: Message, state: FSMContext):
    await command_menu(message)
    await state.clear()


@router.message()
async def confirm_phone(message: Message):
    user_id = message.from_user.id
    user_data = users_data_dict[user_id]

    if not user_data['Is_verified']:
        button_phone = [
            [KeyboardButton(text="✅ Подтвердить номер телефона", request_contact=True)]
            ]
        markup = ReplyKeyboardMarkup(keyboard=button_phone, resize_keyboard=True)
        await message.answer('☎️ <b>Номер телефона не подтвержден</b>\n\n'
                             'Вам необходимо подтвердить <b>номер телефона</b>'
                             ' для того, чтобы начать пользоваться ботом.\n\n'
                             'Для подтверждения нажмите кнопку ниже.',
                             parse_mode='HTML', reply_markup=markup)
    else:
        return
