from web3 import Web3
from typing import Any
from aiocache import cached

from .models import DefaultABIs


@cached(ttl=60)
async def get_token_balance(contract_address, rpc_url, wallet_address, decimals) -> Any:
    contract_address = Web3.to_checksum_address(contract_address)
    rpc_url = Web3(Web3.HTTPProvider(rpc_url))
    token_contract = rpc_url.eth.contract(address=contract_address, abi=DefaultABIs.Token)
    return round(token_contract.functions.balanceOf(wallet_address).call() / decimals, 5)


@cached(ttl=60)
async def get_native_balance(rpc_url, wallet_address, decimals) -> Any:
    rpc_url = Web3(Web3.HTTPProvider(rpc_url))
    return round(rpc_url.eth.get_balance(wallet_address) / decimals, 9)



