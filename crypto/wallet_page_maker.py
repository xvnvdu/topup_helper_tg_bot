import asyncio
from decimal import Decimal, ROUND_DOWN

from logger import logger
from bot.main_bot import users_data_dict
from aiogram.handlers import CallbackQueryHandler

from .models import DefaultABIs, Networks, contracts
from .get_balance_func import get_token_balance, get_native_balance
from .price_parser import return_arb_price, return_eth_price, return_matic_price, return_op_price


abi = DefaultABIs.Token
decimals_18 = 10 ** 18
decimals_6 = 10 ** 6


async def get_balance_by_chain(call: CallbackQueryHandler, chain, chain_currency, chain_currency_name, stable1, stable2,
                               stable1_decimals, stable2_decimals, link, native_currency,
                               stable_name1, stable_name2, flag: False, chain_checker: False):

    user_id = call.from_user.id
    user_data = users_data_dict[user_id]

    rpc = Networks.networks[chain].rpc
    first_stablecoin = contracts[stable1]
    second_stablecoin = contracts[stable2]
    wallet_address = user_data['Wallet_address']

    main_chain_currency_balance = None
    main_in_usdt = None

    if chain_checker:
        main_chain_currency = contracts[chain_currency]
        main_chain_currency_balance = await get_token_balance(main_chain_currency, rpc, wallet_address, decimals_18)
        main_price = await return_op_price() if chain == 'Optimism' else await return_arb_price()
        main_in_usdt = round(main_chain_currency_balance * main_price, 2)

    native_balance, first_stablecoin_balance, second_stablecoin_balance, native_price = await asyncio.gather(
        get_native_balance(rpc, wallet_address, decimals_18),
        get_token_balance(first_stablecoin, rpc, wallet_address, stable1_decimals),
        get_token_balance(second_stablecoin, rpc, wallet_address, stable2_decimals),
        return_matic_price() if native_currency == 'POL' else return_eth_price()
    )

    try:
        native_in_usd = round(native_balance * native_price, 2)
        native_balance = Decimal(native_balance).quantize(Decimal("0.000000001"), rounding=ROUND_DOWN)
        
        if main_chain_currency_balance is not None:
            main_chain_currency_balance = Decimal(main_chain_currency_balance).quantize(Decimal("0.0001"), rounding=ROUND_DOWN)
            
        first_stablecoin_balance = Decimal(first_stablecoin_balance).quantize(Decimal("0.001"), rounding=ROUND_DOWN)
        second_stablecoin_balance = Decimal(second_stablecoin_balance).quantize(Decimal("0.001"), rounding=ROUND_DOWN)
        
    except Exception as e:
        logger.error(f'Произошла ошибка: {e}')

    if chain == 'Optimism' or chain == 'Arbitrum':
        page_text = (
            f'<strong>▫️<a href="{link}">{chain}</a></strong>\n'
            f'  ├ {native_currency}: <code>{f"{native_balance}".rstrip("0").rstrip(".")}</code> '
                                    f'<i>({f"{native_in_usd}".rstrip("0").rstrip(".")}$)</i>\n'
            f'  ├ {chain_currency_name}: <code>{f"{main_chain_currency_balance}".rstrip("0").rstrip(".")}</code> '
                                    f'<i>({f"{main_in_usdt}".rstrip("0").rstrip(".")}$)</i>\n'
            f'  ├ {stable_name1}: <code>{f"{first_stablecoin_balance}".rstrip("0").rstrip(".")}</code>\n'
            f'  └ {stable_name2}: <code>{f"{second_stablecoin_balance}".rstrip("0").rstrip(".")}</code>\n\n'
        )
    else:
        page_text = (
            f'<strong>▫️<a href="{link}">{chain}</a></strong>\n'
            f'  ├ {native_currency}: <code>{f"{native_balance}".rstrip("0").rstrip(".")}</code> '
                                    f'<i>({f"{native_in_usd}".rstrip("0").rstrip(".")}$)</i>\n'
            f'  ├ {stable_name1}: <code>{f"{first_stablecoin_balance}".rstrip("0").rstrip(".")}</code>\n'
            f'  └ {stable_name2}: <code>{f"{second_stablecoin_balance}".rstrip("0").rstrip(".")}</code>\n\n'
        )
    if not flag:
        return page_text
    else:
        total_balance = native_in_usd + float(first_stablecoin_balance) + float(second_stablecoin_balance)
        if main_in_usdt is not None:
            total_balance += main_in_usdt
        return total_balance


async def polygon_mainnet(call: CallbackQueryHandler):
    text = await get_balance_by_chain(call, chain='Polygon', chain_currency = None, chain_currency_name = None, 
                                      stable1='usdt_pol', stable2='usdc_pol',
                                      stable1_decimals=decimals_6, stable2_decimals=decimals_6,
                                      link='https://polygon.technology/', native_currency='POL',
                                      stable_name1='USDT', stable_name2='USDC', flag=False, chain_checker = False)
    return text

async def arbitrum_mainnet(call: CallbackQueryHandler):
    text = await get_balance_by_chain(call, chain='Arbitrum', chain_currency = 'arb_arb', chain_currency_name = 'ARB', 
                                      stable1='usdt_arb', stable2='usdc_arb',
                                      stable1_decimals=decimals_6, stable2_decimals=decimals_6,
                                      link='https://arbitrum.io/', native_currency='ETH',
                                      stable_name1='USDT', stable_name2='USDC', flag=False, chain_checker = True)
    return text

async def optimism_mainnet(call: CallbackQueryHandler):
    text = await get_balance_by_chain(call, chain='Optimism', chain_currency = 'op_op', chain_currency_name = 'OP', 
                                      stable1='usdt_op', stable2='usdc_op',
                                      stable1_decimals=decimals_6, stable2_decimals=decimals_6,
                                      link='https://www.optimism.io/', native_currency='ETH',
                                      stable_name1='USDT', stable_name2='USDC', flag=False, chain_checker = True)
    return text

async def base_mainnet(call: CallbackQueryHandler):
    text = await get_balance_by_chain(call, chain='Base', chain_currency = None, chain_currency_name = None, 
                                      stable1='usdc_base', stable2='dai_base',
                                      stable1_decimals=decimals_6, stable2_decimals=decimals_18,
                                      link='https://www.base.org/', native_currency='ETH',
                                      stable_name1='USDC', stable_name2='DAI', flag=False, chain_checker = False)
    return text



async def main_page(call: CallbackQueryHandler):
    user_id = call.from_user.id
    user_data = users_data_dict[user_id]
    address = user_data['Wallet_address']

    balances = await asyncio.gather(
        get_balance_by_chain(call, chain='Polygon', chain_currency = None, chain_currency_name = None, 
                             stable1='usdt_pol', stable2='usdc_pol',
                             stable1_decimals=decimals_6, stable2_decimals=decimals_6,
                             link=None, native_currency='POL', stable_name1=None,
                             stable_name2=None, flag=True, chain_checker = False),
        get_balance_by_chain(call, chain='Arbitrum', chain_currency = 'arb_arb', chain_currency_name = 'ARB', 
                             stable1='usdt_arb', stable2='usdc_arb',
                             stable1_decimals=decimals_6, stable2_decimals=decimals_6,
                             link=None, native_currency='ETH', stable_name1=None,
                             stable_name2=None, flag=True, chain_checker = True),
        get_balance_by_chain(call, chain='Optimism', chain_currency = 'op_op', chain_currency_name = 'OP', 
                             stable1='usdt_op', stable2='usdc_op',
                             stable1_decimals=decimals_6, stable2_decimals=decimals_6,
                             link=None, native_currency='ETH', stable_name1=None,
                             stable_name2=None, flag=True, chain_checker = True),
        get_balance_by_chain(call, chain='Base', chain_currency = None, chain_currency_name = None, 
                             stable1='usdc_base', stable2='dai_base',
                             stable1_decimals=decimals_6, stable2_decimals=decimals_18,
                             link=None, native_currency='ETH', stable_name1=None,
                             stable_name2=None, flag=True, chain_checker = False)
    )

    total_balance = round(sum(balances), 4)

    main_page_text = (f'<strong>📗 Мой адрес: <code>{address}</code>\n\n'
                      f'💸 Мои активы: <code>{total_balance}$</code></strong>\n\n'
                      f'<i>Данный EVM адрес был присвоен вам в момент регистрации, '
                      f'он статичен и никогда не изменится. Через бота вы можете '
                      f'совершать операции в четырех доступных вам блокчейнах, для '
                      f'этого воспользуйтесь кнопками ниже:\n\n</i>')

    return main_page_text