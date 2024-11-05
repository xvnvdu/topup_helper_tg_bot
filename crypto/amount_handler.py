from aiogram.types import CallbackQuery
from decimal import Decimal, ROUND_DOWN

from .models import Networks, Currencies
from .get_balance_func import get_native_balance, get_token_balance
from .main_crypto import (pending_chain_withdraw, pending_currency_to_withdraw, 
                          pending_user_balance, ok_to_withdraw, pending_user_balance_in_usd)


async def choose_amount(user_id: int, chain: str, currency: str, wallet_address: str, action_type: str):
	rpc_url = Networks.networks[chain].rpc
	decimals = Currencies.currencies[chain][currency].decimals
	contract = Currencies.currencies[chain][currency].contract
	coin_price = Currencies.currencies[chain][currency].return_price

	pending_currency_to_withdraw[user_id] = currency
	pending_chain_withdraw[user_id] = chain
	ok_to_withdraw[user_id] = False

	if contract is None:
		balance = await get_native_balance(rpc_url, wallet_address, decimals)
		digits = '0.000000001'
	else:
		balance = await get_token_balance(contract, rpc_url, wallet_address, decimals)
		if coin_price is not None:
			digits = '0.0001'
		else:
			digits = '0.001'

	balance = Decimal(balance).quantize(Decimal(digits), rounding=ROUND_DOWN)
	pending_user_balance[user_id] = float(f'{balance}'.rstrip('0').rstrip('.'))
	text = (f'<strong>💸 Мои активы</strong> <i>{chain} — {currency}</i>: '
			f'<code>{f"{balance}".rstrip("0").rstrip(".")} {currency}</code>')

	if coin_price is not None:
		coin_price = await coin_price(currency)
		usd_value = round(float(balance) * coin_price, 2)
		pending_user_balance_in_usd[user_id] = usd_value
		text += f' <i>({usd_value}$)</i>'
	else:
		pending_user_balance_in_usd[user_id] = balance

	text += f'\n\n<i>Выберите сумму для {action_type} или введите ее вручную:</i>'
 
	return text


	
	