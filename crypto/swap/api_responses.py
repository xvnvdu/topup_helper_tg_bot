import requests

from config import one_inch_token


class GetData:
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
    
    def get_data(self) -> dict:
        response = requests.get(self.api_url, headers=self.headers, params=self.params)
        response.raise_for_status()
        return response.json()

    @staticmethod
    async def check_allowance(chain_id: int, contract1: str, address: str) -> int:
        json_response = GetData(
            chain_id=chain_id,
            link='approve/allowance',
            body='',
            params={
                'tokenAddress': contract1,
                'walletAddress': address
            }
        )
        allowance = json_response.get_data()['allowance']
        return int(allowance)

    @staticmethod
    async def get_output_amount(chain_id: int, contract1: str, contract2: str, user_amount: str, decimals: int):
        json_response = GetData(
            chain_id=chain_id,
            link='quote',
            body='',
            params={
				'src': contract1,
				'dst': contract2,
				'amount': user_amount,
				'includeTokensInfo': True,
				'includeGas': True
			}
        ).get_data()
        
        amount = int(json_response['dstAmount']) / decimals
        gas = json_response['gas']
        return amount, gas

    
