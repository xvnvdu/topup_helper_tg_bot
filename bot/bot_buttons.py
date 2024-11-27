from typing import Any
from crypto.models import Currencies
from aiogram.types import CallbackQuery
from bot.main_bot import users_payments_dict
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


''' КНОПКИ РАЗДЕЛА МЕНЮ '''

menu_buttons = [
    [InlineKeyboardButton(text='👨‍💻 Мой аккаунт', callback_data='account'),
     InlineKeyboardButton(text='💳 Пополнить', callback_data='topup')],
    [InlineKeyboardButton(text='👛 Криптокошелек', callback_data='crypto')]
        ]
menu_keyboard = InlineKeyboardMarkup(inline_keyboard=menu_buttons)


''' КНОПКИ РАЗДЕЛА АККАУНТ '''

account_buttons = [
    [InlineKeyboardButton(text='📝 Мои операции', callback_data='transactions'),
    InlineKeyboardButton(text='🙋‍♂️ Перевод другу', callback_data='send')],
    [InlineKeyboardButton(text='🆘 Поддержка', callback_data='support')],
    [InlineKeyboardButton(text='← Назад', callback_data='back')]
]
account_keyboard = InlineKeyboardMarkup(inline_keyboard=account_buttons)

back_to_account = [
    [InlineKeyboardButton(text='← Назад', callback_data='account')]
]
back_to_account_keyboard = InlineKeyboardMarkup(inline_keyboard=back_to_account)


''' КНОПКИ РАЗДЕЛА ПОДДЕРЖКИ '''

back_to_support_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='← Назад', callback_data='support')]],
)

support_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='📢 Написать в поддержку', callback_data='message_to_support')],
                     [InlineKeyboardButton(text='⭕️ Правила и требования к обращеням', callback_data='support_rules')],
                     [InlineKeyboardButton(text='← Назад', callback_data='account')]]
)

def answer_message_keyboard(user_id, number, today, time_now) -> Any:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='Ответить на сообщение', callback_data=f'answer_message_{user_id}_{number}_{today}_{time_now}')]],
    )

def cancel_answer_keyboard(user_id, number, today, time_now) -> Any:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='Не отвечать', callback_data=f'cancel_answer_{user_id}_{number}_{today}_{time_now}')]],
    )

def continue_application_keyboard(user_id, number, today, time_now) -> Any:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='Ответить на сообщение', callback_data=f'continue_application_{user_id}_{number}_{today}_{time_now}')]],
    )

def cancel_application_keyboard(user_id, number, today, time_now) -> Any:
    return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='Не отвечать', callback_data=f'cancel_application_{user_id}_{number}_{today}_{time_now}')]],
        )


''' КНОПКИ РАЗДЕЛА ПЕРЕВОДА БАЛАНСА '''

try_again_amount_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='🙋‍♂️ Перевод другу', callback_data='send')]]
    )

try_again_id_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='🥷 Ввести ID', callback_data='choose_id')]]
    )

try_again_message_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='✉️ Написать сообщение', callback_data='message_input')]]
    )

step_back_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='← Изменить сумму', callback_data='send')]]
)

confirm_sending_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='❌ Нет', callback_data='send'),
                      InlineKeyboardButton(text='✅ Да', callback_data='sending_confirmed')]]
)

skip_message_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Пропустить →', callback_data='confirm_sending')]]
)


''' КНОПКИ ЖУРНАЛА ТРАНЗАКЦИЙ '''

zero_transactions_buttons = [
    [InlineKeyboardButton(text='🤑 Перейти к пополнению', callback_data='topup')],
    [InlineKeyboardButton(text='← Назад', callback_data='account')]
]
zero_transactions_keyboard = InlineKeyboardMarkup(inline_keyboard=zero_transactions_buttons)

async def log_buttons(call: CallbackQuery, page_text, current_page: int, total_pages: int):
    trx_log_buttons = [[InlineKeyboardButton(text='← Назад', callback_data='account')]]
    if current_page == 0 and total_pages > 1:
        trx_log_buttons = [
            [InlineKeyboardButton(text=' ', callback_data='None'),
            InlineKeyboardButton(text='>', callback_data='next_page')],
            [InlineKeyboardButton(text='← Назад', callback_data='account')]
        ]
    elif 0 < current_page < total_pages - 1:
        trx_log_buttons = [
            [InlineKeyboardButton(text='<', callback_data='prev_page'),
             InlineKeyboardButton(text='>', callback_data='next_page')],
            [InlineKeyboardButton(text='← Назад', callback_data='account')]
        ]
    elif total_pages == 1:
        trx_log_buttons = [
            [InlineKeyboardButton(text='← Назад', callback_data='account')]
        ]
    elif current_page == total_pages - 1:
        trx_log_buttons = [
            [InlineKeyboardButton(text='<', callback_data='prev_page'),
            InlineKeyboardButton(text=' ', callback_data='None')],
            [InlineKeyboardButton(text='← Назад', callback_data='account')]
        ]

    trx_log_keyboard = InlineKeyboardMarkup(inline_keyboard=trx_log_buttons)
    await call.message.edit_text(text=page_text, parse_mode='HTML', reply_markup=trx_log_keyboard, disable_web_page_preview=True)


''' КНОПКИ РАЗДЕЛА ПОПОЛНЕНИЕ БАЛАНСА '''

payment_buttons = [
    [InlineKeyboardButton(text='🟣 ЮKassa', callback_data='YK')],
    [InlineKeyboardButton(text='⭐️ Telegram Stars', callback_data='stars')],
    [InlineKeyboardButton(text='← Назад', callback_data='back')]
        ]
payment_keyboard = InlineKeyboardMarkup(inline_keyboard=payment_buttons)

stars_buttons = [
        [InlineKeyboardButton(text='100₽ (67 ⭐️)', callback_data='100_in_stars'),
         InlineKeyboardButton(text='200₽ (134 ⭐️)', callback_data='200_in_stars')],
        [InlineKeyboardButton(text='400₽ (267 ⭐️)', callback_data='400_in_stars'),
         InlineKeyboardButton(text='500₽ (334 ⭐️)', callback_data='500_in_stars')],
        [InlineKeyboardButton(text='← Назад', callback_data='topup')]
    ]
stars_keyboard = InlineKeyboardMarkup(inline_keyboard=stars_buttons)

yk_payment_buttons = [
        [InlineKeyboardButton(text='100₽ 💵', callback_data='100_in_rub'),
         InlineKeyboardButton(text='200₽ 💵', callback_data='200_in_rub')],
        [InlineKeyboardButton(text='400₽ 💵', callback_data='400_in_rub'),
         InlineKeyboardButton(text='500₽ 💵', callback_data='500_in_rub')],
        [InlineKeyboardButton(text='← Назад', callback_data='topup')]
    ]
yk_payment_keyboard = InlineKeyboardMarkup(inline_keyboard=yk_payment_buttons)


''' КНОПКИ РАЗДЕЛА КРИПТОКОШЕЛЕК '''

crypto_buttons = [
    [InlineKeyboardButton(text='🟣 Polygon', callback_data='Polygon'),
    InlineKeyboardButton(text='🔵 Base', callback_data='Base')],
    [InlineKeyboardButton(text='🔴 Optimism', callback_data='Optimism'),
    InlineKeyboardButton(text='⚪️ Arbitrum', callback_data='Arbitrum')],
    [InlineKeyboardButton(text='← Назад', callback_data='back')]
]
crypto_keyboard = InlineKeyboardMarkup(inline_keyboard=crypto_buttons)

def chains_keyboard(chain) -> Any:
    chains_buttons = [
        [InlineKeyboardButton(text='📈 Внести', callback_data=f'{chain}_fund'),
        InlineKeyboardButton(text='📉 Вывести', callback_data=f'{chain}_withdraw')],
        [InlineKeyboardButton(text='🔄 Обмен', callback_data=f'{chain}_swap'),
        InlineKeyboardButton(text='🔀 Мост', callback_data=f'{chain}_bridge')],
        [InlineKeyboardButton(text='← Назад', callback_data='crypto')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=chains_buttons)

def back_to_chain_keyboard(chain) -> Any:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='← Назад', callback_data=f'{chain}')]]
    )
    
def try_again_crypto_amount_keyboard(chain) -> Any:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='📈 Внести средства', callback_data=f'{chain}_fund')]]
    )

def confirm_fund_wallet(chain, trx_id) -> Any:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='❌ Нет', callback_data=f'{chain}_fund'),
            InlineKeyboardButton(text='✅ Да', callback_data=f'confirm_funding_id_{trx_id}')]
        ]
    )

def successful_wallet_fund(exp_link, explorer, trx_hash) -> Any:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f'🌐 Смотреть на {explorer}', url=f'{exp_link}/tx/{trx_hash}')]
        ]
    )

def withdraw_crypto(chain) -> Any:
    withdraw_buttons_list = []
    
    for cur in Currencies.currencies[chain]:
        withdraw_buttons_list.append(InlineKeyboardButton(text=f'{cur}', callback_data=f'withdraw_{chain}_{cur}'))

    if len(Currencies.currencies[chain]) % 2 != 0:
        withdraw_buttons = []
        index = 0
        withdraw_buttons.append([withdraw_buttons_list[index]])
        for i in range(int((len(Currencies.currencies[chain]) - 1) / 2)):
            index += 1
            withdraw_buttons.append([withdraw_buttons_list[index], withdraw_buttons_list[index+1]])
            index += 1
    else:
        withdraw_buttons = []
        index = 0
        for i in range(int((len(Currencies.currencies[chain])) / 2)):
            withdraw_buttons.append([withdraw_buttons_list[index], withdraw_buttons_list[index+1]])
            index += 2
        
    withdraw_buttons.append([InlineKeyboardButton(text='← Назад', callback_data=f'{chain}')])
    
    return InlineKeyboardMarkup(inline_keyboard=withdraw_buttons)

def crypto_amount_to_withdraw(chain: str, coin: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='25%', callback_data=f'25_percent_withdraw_{chain}_{coin}'),
             InlineKeyboardButton(text='50%', callback_data=f'50_percent_withdraw_{chain}_{coin}')],
            [InlineKeyboardButton(text='75%', callback_data=f'75_percent_withdraw_{chain}_{coin}'),
             InlineKeyboardButton(text='100%', callback_data=f'100_percent_withdraw_{chain}_{coin}')],
            [InlineKeyboardButton(text='← Назад', callback_data=f'{chain}_withdraw')]
        ]
    )

def try_again_withdraw_amount(chain, currency) -> Any:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='✏️ Изменить сумму', callback_data=f'withdraw_{chain}_{currency}')]
        ]
    )

def change_withdraw_amount(chain, currency) -> Any:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Изменить сумму вывода', callback_data=f'withdraw_{chain}_{currency}')]
        ]
    )

try_again_address_input_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='✏️ Изменить адрес', callback_data=f'change_withdraw_address')]
    ]
)

def confirm_withdrawal(trx_id: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='❌ Нет', callback_data='change_withdraw_address'),
            InlineKeyboardButton(text='✅ Да', callback_data=f'withdrawal_confirmed_id_{trx_id}')]
        ]
    )

def successful_wallet_withdrawal(exp_link: str, explorer: str, trx_hash: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f'🌐 Смотреть на {explorer}', url=f'{exp_link}/tx/{trx_hash}')]
        ]
    )

def swap_choice_keyboard(chain: str):
    swap_buttons_list = []

    for cur in Currencies.currencies[chain]:
        swap_buttons_list.append(InlineKeyboardButton(text=f'{cur}', callback_data=f'swap_{chain}_{cur}'))
    
    if len(Currencies.currencies[chain]) % 2 != 0:
        swap_buttons = []
        index = 0
        swap_buttons.append([swap_buttons_list[index]])
        for i in range(int((len(Currencies.currencies[chain]) - 1) / 2)):
            index += 1
            swap_buttons.append([swap_buttons_list[index], swap_buttons_list[index+1]])
            index += 1
    else:
        swap_buttons = []
        index = 0
        for i in range(int((len(Currencies.currencies[chain])) / 2)):
            swap_buttons.append([swap_buttons_list[index], swap_buttons_list[index+1]])
            index += 2
    
    swap_buttons.append([InlineKeyboardButton(text='← Назад', callback_data=f'{chain}')])
    
    return InlineKeyboardMarkup(inline_keyboard=swap_buttons)


def swap_second_choice_keyboard(chain: str, currency: str):
    swap_buttons_list = []
    
    for cur in Currencies.currencies[chain]:
        if cur != currency:
            swap_buttons_list.append(
                InlineKeyboardButton(text=f'{cur}', callback_data=f'proceed_swap_{chain}_{currency}_{cur}')
            )
    
    if (len(Currencies.currencies[chain]) - 1) % 2 != 0:
        swap_buttons = []
        index = 0
        swap_buttons.append([swap_buttons_list[index]])
        for i in range(int((len(Currencies.currencies[chain]) - 1) / 2)):
            index += 1
            swap_buttons.append([swap_buttons_list[index], swap_buttons_list[index+1]])
            index += 1
    else:
        swap_buttons = []
        index = 0
        for i in range(int((len(Currencies.currencies[chain])) / 2)):
            swap_buttons.append([swap_buttons_list[index], swap_buttons_list[index+1]])
            index += 2
    
    swap_buttons.append([InlineKeyboardButton(text='← Назад', callback_data=f'{chain}_swap')])
    
    return InlineKeyboardMarkup(inline_keyboard=swap_buttons)
    
    
def crypto_amount_swap(chain: str, cur1: str, cur2: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='25%', callback_data=f'25_percent_swap_{chain}_{cur1}_{cur2}'),
             InlineKeyboardButton(text='50%', callback_data=f'50_percent_swap_{chain}_{cur1}_{cur2}')],
            [InlineKeyboardButton(text='75%', callback_data=f'75_percent_swap_{chain}_{cur1}_{cur2}'),
             InlineKeyboardButton(text='100%', callback_data=f'100_percent_swap_{chain}_{cur1}_{cur2}')],
            [InlineKeyboardButton(text='← Назад', callback_data=f'swap_{chain}_{cur1}')]
        ]
    )
    
def change_swap_amount(chain: str, cur1: str, cur2: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='✏️ Изменить сумму свапа', callback_data=f'proceed_swap_{chain}_{cur1}_{cur2}')]
        ]
    )
    
def confirm_swap_keyboard(trx_id: str, chain: str, cur1: str, cur2: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='❌ Нет', callback_data=f'proceed_swap_{chain}_{cur1}_{cur2}'),
            InlineKeyboardButton(text='✅ Да', callback_data=f'confirmed_swap_id_{trx_id}')]
        ]
    )
    
def allowance_handler_keyboard(chain: str, cur1: str, cur2: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='❌ Нет', callback_data=f'proceed_swap_{chain}_{cur1}_{cur2}'),
            InlineKeyboardButton(text='✅ Да', callback_data=f'approve_allowance')]
        ]
    )

def successful_approve(exp_link: str, explorer: str, trx_hash: str | None, active_button: bool, today: str, time_now: str):
    keyboard = [
            [InlineKeyboardButton(text=f'🌐 Смотреть на {explorer}', url=f'{exp_link}/tx/{trx_hash}')]
        ]
    if active_button:
        keyboard.append([InlineKeyboardButton(text=f'🔄 Перейти к обмену', callback_data=f'go_to_swap_{today}_{time_now}')])
        
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def successful_swap(explorer: str, exp_link: str, trx_hash: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f'🌐 Смотреть на {explorer}', url=f'{exp_link}/tx/{trx_hash}')]
        ]
    )
    