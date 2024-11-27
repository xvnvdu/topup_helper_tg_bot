import asyncio
import requests
import time

from config import one_inch_token


''' КЛАСС ДЛЯ ОБРАЩЕНИЯ К API И ИЗВЛЕЧЕНИЯ ДАННЫХ '''

class GetData:
    _rate_limit_lock = asyncio.Lock()
    _last_request_time = 0
    
    def __init__(self, 
                 chain_id: int, 
                 link: str, 
                 body: str, 
                 params: dict
) -> None:
        self.chain_id = chain_id
        self.link = link
        self.body = body
        self.params = params
        self.api_url = f'https://api.1inch.dev/swap/v6.0/{chain_id}/{link}'
        self.headers = {
            'Authorization': f'Bearer {one_inch_token}'
        }
    
    async def get_data(self) -> dict:
        async with GetData._rate_limit_lock:
            elapsed_time = time.monotonic() - GetData._last_request_time
            if elapsed_time < 1: 
                await asyncio.sleep(1 - elapsed_time)
            
            response = requests.get(self.api_url, headers=self.headers, params=self.params)
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def check_allowance(chain_id: int, contract1: str, address: str) -> int:
        time.sleep(1)
        json_response = await GetData(
            chain_id = chain_id,
            link = 'approve/allowance',
            body = '',
            params = {
                'tokenAddress': contract1,
                'walletAddress': address
            }
        ).get_data()
        
        allowance = json_response['allowance']
        return int(allowance)

    @staticmethod
    async def get_output_amount(chain_id: int, contract1: str, contract2: str, user_amount: str, decimals: int):
        time.sleep(1)
        json_response = await GetData(
            chain_id = chain_id,
            link = 'quote',
            body = '',
            params = {
				'src': contract1,
				'dst': contract2,
				'amount': user_amount,
				'includeTokensInfo': True,
				'includeGas': True
			}
        ).get_data()
        
        amount = int(json_response['dstAmount']) / decimals
        return amount

    @staticmethod
    async def get_allowance_data(chain_id: int, contract1: str, user_amount_wei: int):
        time.sleep(1)
        json_response = await GetData(
            chain_id = chain_id,
            link = 'approve/transaction',
            body = '',
            params = {
                'tokenAddress': contract1,
                'amount': user_amount_wei
            }
        ).get_data()

        data = json_response['data']
        gas_price = json_response['gasPrice']
        token = json_response['to']
        return data, gas_price, token
    
    @staticmethod
    async def get_swap_data(chain_id: int, swap_params: dict):
        time.sleep(1)
        json_response = await GetData(
            chain_id = chain_id,
            link = 'swap',
            body = '',
            params = swap_params
        ).get_data()

        output_amount_wei = int(json_response['dstAmount'])
        swap_contract = json_response['tx']['to']
        data = json_response['tx']['data']
        gas = int(json_response['tx']['gas'])
        gas_price_wei = int(json_response['tx']['gasPrice'])
        value = int(json_response['tx']['value'])
        return output_amount_wei, swap_contract, data, gas, gas_price_wei, value
    
