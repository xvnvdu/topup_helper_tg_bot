import aiohttp
import asyncio

from typing import Any
from aiocache import cached
from config import usd_parser_token


''' API АКТИВОВ '''

class GetPrice:
    def __init__(self,
                 url: str,
                 get_data: Any
) -> None:
        self.url = url
        self.get_data = get_data
    
    @classmethod
    def apis(cls, asset) -> Any:
        if asset == 'USD':
            return {
                asset: cls(
                    url = f'https://v6.exchangerate-api.com/v6/{usd_parser_token}/latest/{asset}',
                    get_data = 'conversion_rates'
                )
            }
        else:
            return {
                asset: cls(
                    url = f'https://api.binance.com/api/v3/ticker/price?symbol={asset}USDT',
                    get_data = 'price'
                )
            }


''' ИЗВЛЕЧЕНИЕ СТОИМОСТИ ЧЕРЕЗ API '''

async def get_price(session, asset: str):
    asset_info = GetPrice.apis(asset)[asset]
    url = asset_info.url
    async with session.get(url) as responce:
        data = await responce.json()
        if asset == 'USD':
            price = data[asset_info.get_data]['RUB']
        else:
            price = data[asset_info.get_data]
        return float(price)


''' ОБРАБОТКА ИЗВЛЕЧЕННОЙ СТОИМОСТИ '''

async def return_asset_price(asset: str):
    async with aiohttp.ClientSession() as session:
        asset = get_price(session, asset)
        asset_price = await asyncio.gather(asset)
        return asset_price[0]

@cached(ttl=14400)
async def return_usd_price() -> Any:
    async with aiohttp.ClientSession() as session:
        price = await get_price(session, 'USD')
        return price
        