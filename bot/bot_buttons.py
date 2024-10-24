from typing import Any
from crypto.models import Currencies
from aiogram.handlers import CallbackQueryHandler
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


menu_buttons = [
    [InlineKeyboardButton(text='👨‍💻 Мой аккаунт', callback_data='account'),
     InlineKeyboardButton(text='💳 Пополнить', callback_data='topup')],
    [InlineKeyboardButton(text='👛 Криптокошелек', callback_data='crypto')]
        ]
menu_keyboard = InlineKeyboardMarkup(inline_keyboard=menu_buttons)

account_buttons = [
    [InlineKeyboardButton(text='📝 Мои операции', callback_data='transactions'),
    InlineKeyboardButton(text='🙋‍♂️ Перевод другу', callback_data='send')],
    [InlineKeyboardButton(text='← Назад', callback_data='back')]
]
account_keyboard = InlineKeyboardMarkup(inline_keyboard=account_buttons)


send_buttons = [
    [InlineKeyboardButton(text='← Назад', callback_data='account')]
]
send_keyboard = InlineKeyboardMarkup(inline_keyboard=send_buttons)

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


zero_transactions_buttons = [
    [InlineKeyboardButton(text='🤑 Перейти к пополнению', callback_data='topup')],
    [InlineKeyboardButton(text='← Назад', callback_data='account')]
]
zero_transactions_keyboard = InlineKeyboardMarkup(inline_keyboard=zero_transactions_buttons)


payment_buttons = [
    [InlineKeyboardButton(text='🟣 ЮKassa', callback_data='YK')],
    [InlineKeyboardButton(text='⭐️ Telegram Stars', callback_data='stars')],
    [InlineKeyboardButton(text='← Назад', callback_data='back')]
        ]
payment_keyboard = InlineKeyboardMarkup(inline_keyboard=payment_buttons)


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
            [InlineKeyboardButton(text=f'Смотреть на {explorer}', url=f'{exp_link}/tx/{trx_hash}')]
        ]
    )


def withdraw_crypto(chain) -> Any:
    withdraw_buttons_list = []
    
    for cur in Currencies.currencies[chain]:
        withdraw_buttons_list.append(InlineKeyboardButton(text=f'{cur}', callback_data=f'withdraw_{chain}_{cur}'))

    if len(Currencies.currencies[chain]) % 2 != 0:
        withdraw_buttons = []
        ind = 0
        withdraw_buttons.append([withdraw_buttons_list[ind]])
        for i in range(int((len(Currencies.currencies[chain]) - 1) / 2)):
            ind += 1
            withdraw_buttons.append([withdraw_buttons_list[ind], withdraw_buttons_list[ind+1]])
            ind += 1
    else:
        withdraw_buttons = []
        ind = 0
        for i in range(int((len(Currencies.currencies[chain])) / 2)):
            withdraw_buttons.append([withdraw_buttons_list[ind], withdraw_buttons_list[ind+1]])
            ind += 2
        
    withdraw_buttons.append([InlineKeyboardButton(text='← Назад', callback_data=f'{chain}')])
    
    return InlineKeyboardMarkup(inline_keyboard=withdraw_buttons)


def crypto_amount_to_withdraw(chain, coin) -> Any:
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


def successful_wallet_withdrawal(exp_link, explorer, trx_hash) -> Any:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f'Смотреть на {explorer}', url=f'{exp_link}/tx/{trx_hash}')]
        ]
    )


stars_buttons = [
        [InlineKeyboardButton(text='100₽ (63 ⭐️)', callback_data='100_in_stars'),
         InlineKeyboardButton(text='200₽ (125 ⭐️)', callback_data='200_in_stars')],
        [InlineKeyboardButton(text='400₽ (250 ⭐️)', callback_data='400_in_stars'),
         InlineKeyboardButton(text='500₽ (313 ⭐️)', callback_data='500_in_stars')],
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


async def log_buttons(call: CallbackQueryHandler, page_text, current_page: int, total_pages: int):
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
