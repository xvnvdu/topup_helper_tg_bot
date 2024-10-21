import aiohttp
import asyncio

from typing import Any
from aiocache import cached
from config import usd_parser_token


async def get_matic_price(session) -> Any:
    url = 'https://api.binance.com/api/v3/ticker/price?symbol=POLUSDT'
    async with session.get(url) as responce:
        data = await responce.json()
        price = data['price']
        return float(price)


async def get_eth_price(session) -> Any:
    url = 'https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT'
    async with session.get(url) as responce:
        data = await responce.json()
        price = data['price']
        return float(price)


async def get_op_price(session) -> Any:
    url = 'https://api.binance.com/api/v3/ticker/price?symbol=OPUSDT'
    async with session.get(url) as responce:
        data = await responce.json()
        price = data['price']
        return float(price)

    
async def get_arb_price(session) -> Any:
    url = 'https://api.binance.com/api/v3/ticker/price?symbol=ARBUSDT'
    async with session.get(url) as responce:
        data = await responce.json()
        price = data['price']
        return float(price)


async def get_usd_price(session) -> Any:
    url = f'https://v6.exchangerate-api.com/v6/{usd_parser_token}/latest/USD'
    async with session.get(url) as responce:
        data = await responce.json()
        price = data['conversion_rates']['RUB']
        return price


async def return_matic_price() -> Any:
    async with aiohttp.ClientSession() as session:
        matic = get_matic_price(session)
        matic_price = await asyncio.gather(matic)
        return matic_price[0]


async def return_eth_price() -> Any:
    async with aiohttp.ClientSession() as session:
        eth = get_eth_price(session)
        eth_price = await asyncio.gather(eth)
        return eth_price[0]

    
async def return_op_price() -> Any:
    async with aiohttp.ClientSession() as session:
        op = get_op_price(session)
        op_price = await asyncio.gather(op)
        return op_price[0]

    
async def return_arb_price() -> Any:
    async with aiohttp.ClientSession() as session:
        arb = get_arb_price(session)
        arb_price = await asyncio.gather(arb)
        return arb_price[0]


@cached(ttl=14400)
async def return_usd_price() -> Any:
    async with aiohttp.ClientSession() as session:
        usd = get_usd_price(session) 
        usd_price = await asyncio.gather(usd)
        return usd_price[0]