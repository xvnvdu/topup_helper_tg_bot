from typing import Any
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .interface_language.core import phrases

from crypto.models import Currencies
from bot.main_bot import users_payments_dict


''' КНОПКИ РАЗДЕЛА МЕНЮ '''

def menu_keyboard(language: str):
    lang = phrases(language)
    menu_buttons = [
        [InlineKeyboardButton(text=lang.my_account, callback_data='account'),
        InlineKeyboardButton(text=lang.topup, callback_data='topup')],
        [InlineKeyboardButton(text=lang.cryptowallet, callback_data='crypto')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=menu_buttons)


''' КНОПКИ РАЗДЕЛА АККАУНТ '''

def account_keyboard(language: str):
    lang = phrases(language)
    account_buttons = [
        [InlineKeyboardButton(text=lang.my_transactions, callback_data='transactions'),
        InlineKeyboardButton(text=lang.send_to_friend, callback_data='send')],
        [InlineKeyboardButton(text=lang.support, callback_data='support')],
        [InlineKeyboardButton(text='🇷🇺 Язык | 🇺🇸 Language', callback_data='language')],
        [InlineKeyboardButton(text=lang.back, callback_data='back')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=account_buttons)

def back_to_account_keyboard(language: str):
    lang = phrases(language)
    back_to_account = [
        [InlineKeyboardButton(text=lang.back, callback_data='account')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=back_to_account)


''' КНОПКИ РАЗДЕЛА ПОДДЕРЖКИ '''

def back_to_support_keyboard(language: str):
    lang = phrases(language)
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=lang.back, callback_data='support')]],
    )

def support_keyboard(language: str):
    lang = phrases(language)
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=lang.write_to_support, callback_data='message_to_support')],
                        [InlineKeyboardButton(text=lang.support_rules, callback_data='support_rules')],
                        [InlineKeyboardButton(text=lang.back, callback_data='account')]]
    )

def answer_message_keyboard(user_id, number, today, time_now, language) -> Any:
    lang = phrases(language)
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=lang.answer_message, callback_data=f'answer_message_{user_id}_{number}_{today}_{time_now}')]],
    )

def cancel_answer_keyboard(user_id, number, today, time_now, language) -> Any:
    lang = phrases(language)
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=lang.do_not_answer, callback_data=f'cancel_answer_{user_id}_{number}_{today}_{time_now}')]],
    )

def continue_application_keyboard(user_id, number, today, time_now, language) -> Any:
    lang = phrases(language)
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=lang.answer_message, callback_data=f'continue_application_{user_id}_{number}_{today}_{time_now}')]],
    )

def cancel_application_keyboard(user_id, number, today, time_now, language) -> Any:
    lang = phrases(language)
    return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=lang.do_not_answer, callback_data=f'cancel_application_{user_id}_{number}_{today}_{time_now}')]],
        )


''' КНОПКИ РАЗДЕЛА ПЕРЕВОДА БАЛАНСА '''

def try_again_amount_keyboard(language: str):
    lang = phrases(language)
    return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=lang.send_to_friend, callback_data='send')]]
        )

def try_again_id_keyboard(language: str):
    lang = phrases(language)
    return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=lang.enter_id, callback_data='choose_id')]]
        )

def try_again_message_keyboard(language: str):
    lang = phrases(language)
    return InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=lang.write_a_message, callback_data='message_input')]]
        )

def step_back_keyboard(language: str):
    lang = phrases(language)
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=lang.change_amount, callback_data='send')]]
    )

def confirm_sending_keyboard(language: str):
    lang = phrases(language)
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=lang.no, callback_data='send'),
                        InlineKeyboardButton(text=lang.yes, callback_data='sending_confirmed')]]
    )

def skip_message_keyboard(language: str):
    lang = phrases(language)
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=lang.skip, callback_data='confirm_sending')]]
    )


''' КНОПКИ ЖУРНАЛА ТРАНЗАКЦИЙ '''

def zero_transactions_keyboard(language: str):
    lang = phrases(language)
    zero_transactions_buttons = [
        [InlineKeyboardButton(text=lang.proceed_to_funding, callback_data='topup')],
        [InlineKeyboardButton(text=lang.back, callback_data='account')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=zero_transactions_buttons)


async def log_buttons(call: CallbackQuery, page_text, current_page: int, total_pages: int, language: str):
    lang = phrases(language)
    trx_log_buttons = [[InlineKeyboardButton(text=lang.back, callback_data='account')]]
    if current_page == 0 and total_pages > 1:
        trx_log_buttons = [
            [InlineKeyboardButton(text=' ', callback_data='None'),
            InlineKeyboardButton(text='>', callback_data='next_page')],
            [InlineKeyboardButton(text=lang.back, callback_data='account')]
        ]
    elif 0 < current_page < total_pages - 1:
        trx_log_buttons = [
            [InlineKeyboardButton(text='<', callback_data='prev_page'),
             InlineKeyboardButton(text='>', callback_data='next_page')],
            [InlineKeyboardButton(text=lang.back, callback_data='account')]
        ]
    elif total_pages == 1:
        trx_log_buttons = [
            [InlineKeyboardButton(text=lang.back, callback_data='account')]
        ]
    elif current_page == total_pages - 1:
        trx_log_buttons = [
            [InlineKeyboardButton(text='<', callback_data='prev_page'),
            InlineKeyboardButton(text=' ', callback_data='None')],
            [InlineKeyboardButton(text=lang.back, callback_data='account')]
        ]

    trx_log_keyboard = InlineKeyboardMarkup(inline_keyboard=trx_log_buttons)
    await call.message.edit_text(text=page_text, parse_mode='HTML', reply_markup=trx_log_keyboard, disable_web_page_preview=True)


''' КНОПКИ РАЗДЕЛА ПОПОЛНЕНИЕ БАЛАНСА '''

def payment_keyboard(language: str):
    lang = phrases(language)
    payment_buttons = [
        [InlineKeyboardButton(text=lang.yookassa, callback_data='YK')],
        [InlineKeyboardButton(text='⭐️ Telegram Stars', callback_data='stars')],
        [InlineKeyboardButton(text=lang.back, callback_data='back')]
            ]
    return InlineKeyboardMarkup(inline_keyboard=payment_buttons)

def stars_keyboard(language: str):
    lang = phrases(language)
    stars_buttons = [
            [InlineKeyboardButton(text='100₽ (67 ⭐️)', callback_data='100_in_stars'),
            InlineKeyboardButton(text='200₽ (134 ⭐️)', callback_data='200_in_stars')],
            [InlineKeyboardButton(text='400₽ (267 ⭐️)', callback_data='400_in_stars'),
            InlineKeyboardButton(text='500₽ (334 ⭐️)', callback_data='500_in_stars')],
            [InlineKeyboardButton(text=lang.back, callback_data='topup')]
        ]
    return InlineKeyboardMarkup(inline_keyboard=stars_buttons)

def yk_payment_keyboard(language: str):
    lang = phrases(language)
    yk_payment_buttons = [
            [InlineKeyboardButton(text='100₽ 💵', callback_data='100_in_rub'),
            InlineKeyboardButton(text='200₽ 💵', callback_data='200_in_rub')],
            [InlineKeyboardButton(text='400₽ 💵', callback_data='400_in_rub'),
            InlineKeyboardButton(text='500₽ 💵', callback_data='500_in_rub')],
            [InlineKeyboardButton(text=lang.back, callback_data='topup')]
        ]
    return InlineKeyboardMarkup(inline_keyboard=yk_payment_buttons)


''' КНОПКИ РАЗДЕЛА КРИПТОКОШЕЛЕК '''

def crypto_keyboard(language: str):
    lang = phrases(language)
    crypto_buttons = [
        [InlineKeyboardButton(text='🟣 Polygon', callback_data='Polygon'),
        InlineKeyboardButton(text='🔵 Base', callback_data='Base')],
        [InlineKeyboardButton(text='🔴 Optimism', callback_data='Optimism'),
        InlineKeyboardButton(text='⚪️ Arbitrum', callback_data='Arbitrum')],
        [InlineKeyboardButton(text=lang.back, callback_data='back')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=crypto_buttons)

def chains_keyboard(chain, language) -> Any:
    lang = phrases(language)
    chains_buttons = [
        [InlineKeyboardButton(text=lang.deposit, callback_data=f'{chain}_fund'),
        InlineKeyboardButton(text=lang.withdraw, callback_data=f'{chain}_withdraw')],
        [InlineKeyboardButton(text=lang.swap, callback_data=f'{chain}_swap'),
        InlineKeyboardButton(text=lang.bridge, callback_data=f'{chain}_bridge')],
        [InlineKeyboardButton(text=lang.back, callback_data='crypto')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=chains_buttons)

def back_to_chain_keyboard(chain, language) -> Any:
    lang = phrases(language)
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=lang.back, callback_data=f'{chain}')]]
    )
    
def try_again_crypto_amount_keyboard(chain, language) -> Any:
    lang = phrases(language)
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=lang.deposit_funds, callback_data=f'{chain}_fund')]]
    )

def confirm_fund_wallet(chain, trx_id, language) -> Any:
    lang = phrases(language)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=lang.no, callback_data=f'{chain}_fund'),
            InlineKeyboardButton(text=lang.yes, callback_data=f'confirm_funding_id_{trx_id}')]
        ]
    )

def successful_wallet_fund(exp_link, explorer, trx_hash, language) -> Any:
    lang = phrases(language)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f'{lang.see_on} {explorer}', url=f'{exp_link}/tx/{trx_hash}')]
        ]
    )

def withdraw_crypto(chain, language) -> Any:
    lang = phrases(language)
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
        
    withdraw_buttons.append([InlineKeyboardButton(text=lang.back, callback_data=f'{chain}')])
    
    return InlineKeyboardMarkup(inline_keyboard=withdraw_buttons)

def crypto_amount_to_withdraw(chain: str, coin: str, language:str):
    lang = phrases(language)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='25%', callback_data=f'25_percent_withdraw_{chain}_{coin}'),
             InlineKeyboardButton(text='50%', callback_data=f'50_percent_withdraw_{chain}_{coin}')],
            [InlineKeyboardButton(text='75%', callback_data=f'75_percent_withdraw_{chain}_{coin}'),
             InlineKeyboardButton(text='100%', callback_data=f'100_percent_withdraw_{chain}_{coin}')],
            [InlineKeyboardButton(text=lang.back, callback_data=f'{chain}_withdraw')]
        ]
    )

def try_again_withdraw_amount(chain, currency, language) -> Any:
    lang = phrases(language)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=lang.change_crypto_amount, callback_data=f'withdraw_{chain}_{currency}')]
        ]
    )

def change_withdraw_amount(chain, currency, language) -> Any:
    lang = phrases(language)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=lang.change_withdraw_amount, callback_data=f'withdraw_{chain}_{currency}')]
        ]
    )

def try_again_address_input_keyboard(language: str):
    lang = phrases(language)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=lang.change_address, callback_data=f'change_withdraw_address')]
        ]
    )

def confirm_withdrawal(trx_id: str, language: str):
    lang = phrases(language)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=lang.no, callback_data='change_withdraw_address'),
            InlineKeyboardButton(text=lang.yes, callback_data=f'withdrawal_confirmed_id_{trx_id}')]
        ]
    )

def successful_wallet_withdrawal(exp_link: str, explorer: str, trx_hash: str, language: str):
    lang = phrases(language)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f'{lang.see_on} {explorer}', url=f'{exp_link}/tx/{trx_hash}')]
        ]
    )

def swap_choice_keyboard(chain: str, language: str):
    lang = phrases(language)
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
    
    swap_buttons.append([InlineKeyboardButton(text=lang.back, callback_data=f'{chain}')])
    
    return InlineKeyboardMarkup(inline_keyboard=swap_buttons)


def swap_second_choice_keyboard(chain: str, currency: str, language: str):
    lang = phrases(language)
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
    
    swap_buttons.append([InlineKeyboardButton(text=lang.back, callback_data=f'{chain}_swap')])
    
    return InlineKeyboardMarkup(inline_keyboard=swap_buttons)
    
    
def crypto_amount_swap(chain: str, cur1: str, cur2: str, language: str):
    lang = phrases(language)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='25%', callback_data=f'25_percent_swap_{chain}_{cur1}_{cur2}'),
             InlineKeyboardButton(text='50%', callback_data=f'50_percent_swap_{chain}_{cur1}_{cur2}')],
            [InlineKeyboardButton(text='75%', callback_data=f'75_percent_swap_{chain}_{cur1}_{cur2}'),
             InlineKeyboardButton(text='100%', callback_data=f'100_percent_swap_{chain}_{cur1}_{cur2}')],
            [InlineKeyboardButton(text=lang.back, callback_data=f'swap_{chain}_{cur1}')]
        ]
    )
    
def change_swap_amount(chain: str, cur1: str, cur2: str, language: str):
    lang = phrases(language)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=lang.change_swap_amount, callback_data=f'proceed_swap_{chain}_{cur1}_{cur2}')]
        ]
    )
    
def confirm_swap_keyboard(trx_id: str, chain: str, cur1: str, cur2: str, language: str):
    lang = phrases(language)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=lang.no, callback_data=f'proceed_swap_{chain}_{cur1}_{cur2}'),
            InlineKeyboardButton(text=lang.yes, callback_data=f'confirmed_swap_id_{trx_id}')]
        ]
    )
    
def allowance_handler_keyboard(chain: str, cur1: str, cur2: str, language: str):
    lang = phrases(language)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=lang.no, callback_data=f'proceed_swap_{chain}_{cur1}_{cur2}'),
            InlineKeyboardButton(text=lang.yes, callback_data=f'approve_allowance')]
        ]
    )

def successful_approve(exp_link: str, explorer: str, trx_hash: str | None, active_button: bool, today: str, time_now: str, language: str):
    lang = phrases(language)
    keyboard = [
            [InlineKeyboardButton(text=f'{lang.see_on} {explorer}', url=f'{exp_link}/tx/{trx_hash}')]
        ]
    if active_button:
        keyboard.append([InlineKeyboardButton(text=lang.proceed_to_swap, callback_data=f'go_to_swap_{today}_{time_now}')])
        
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def successful_swap(explorer: str, exp_link: str, trx_hash: str, language: str):
    lang = phrases(language)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f'{lang.see_on} {explorer}', url=f'{exp_link}/tx/{trx_hash}')]
        ]
    )
    