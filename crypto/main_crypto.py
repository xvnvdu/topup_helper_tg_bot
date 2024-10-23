from web3 import Web3
from typing import Any
from datetime import datetime
from aiogram.fsm.state import StatesGroup, State


ok_to_fund = {}
pending_fund_info = {}
pending_chain_fund = {}
pending_rub_amount = {}
pending_fund_trx_id = {}
pending_crypto_fund_amount = {}


ok_to_withdraw = {}
pending_user_balance = {}
pending_withdraw_info = {}
pending_chain_withdraw = {}
pending_withdrawal_trx = {}
pending_withdraw_trx_id = {}
withdraw_amount_to_show = {}
withdraw_amount_usd_value = {}
pending_user_balance_in_usd = {}
pending_address_to_withdraw = {}
pending_currency_to_withdraw = {}
pending_crypto_withdraw_amount = {}


async def get_time() -> Any:
    today = datetime.now().strftime('%d.%m.%Y')
    time_now = datetime.now().strftime('%H:%M:%S')
    return today, time_now


class CryptoPayments(StatesGroup):
    fund_wallet = State()
    amount_to_withdraw = State()
    address_withdraw_to = State()
    swap = State()
    bridge = State()


async def create_new_wallet() -> Any:
    wallet = Web3().eth.account.create()
    wallet_address = wallet.address
    private_key = wallet.key.hex()
    return wallet_address, private_key

