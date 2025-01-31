import requests
from web3 import Web3

from logger import logger
from .price_parser import return_asset_price


''' АДРЕСА КОНТРАКТОВ ERC20 '''

contracts = {
    'usdt_pol': '0xc2132D05D31c914a87C6611C10748AEb04B58e8F',
    'usdc_pol': '0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359',
    'arb_arb': '0x912CE59144191C1204E64559FE8253a0e49E6548',
    'usdt_arb': '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',
    'usdc_arb': '0xaf88d065e77c8cC2239327C5EDb3A432268e5831',
    'op_op': '0x4200000000000000000000000000000000000042',
    'usdt_op': '0x94b008aA00579c1307B0EF2c499aD98a8ce58e58',
    'usdc_op': '0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85',
    'usdc_base': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
    'dai_base': '0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb',
}


''' ABI ДЛЯ ERC20 '''

class DefaultABIs:
    Token = [
        {
            'constant': True,
            'inputs': [],
            'name': 'name',
            'outputs': [{'name': '', 'type': 'string'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': True,
            'inputs': [],
            'name': 'symbol',
            'outputs': [{'name': '', 'type': 'string'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': True,
            'inputs': [],
            'name': 'totalSupply',
            'outputs': [{'name': '', 'type': 'uint256'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': True,
            'inputs': [],
            'name': 'decimals',
            'outputs': [{'name': '', 'type': 'uint256'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': True,
            'inputs': [{'name': 'account', 'type': 'address'}],
            'name': 'balanceOf',
            'outputs': [{'name': '', 'type': 'uint256'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': True,
            'inputs': [{'name': 'owner', 'type': 'address'}, {'name': 'spender', 'type': 'address'}],
            'name': 'allowance',
            'outputs': [{'name': 'remaining', 'type': 'uint256'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': False,
            'inputs': [{'name': 'spender', 'type': 'address'}, {'name': 'value', 'type': 'uint256'}],
            'name': 'approve',
            'outputs': [],
            'payable': False,
            'stateMutability': 'nonpayable',
            'type': 'function'
        },
        {
            'constant': False,
            'inputs': [{'name': 'to', 'type': 'address'}, {'name': 'value', 'type': 'uint256'}],
            'name': 'transfer',
            'outputs': [], 'payable': False,
            'stateMutability': 'nonpayable',
            'type': 'function'
        }]


''' ШАБЛОН ДЛЯ СЕТЕЙ '''

class Network:
    def __init__(self, 
                 name: str,
                 rpc: str,
                 chain_id: int,
                 coin_symbol: str,
                 explorer: str,
                 explorer_link: str
) -> None:
        self.name = name
        self.rpc = rpc
        self.chain_id = chain_id
        self.coin_symbol = coin_symbol
        self.explorer = explorer
        self.explorer_link = explorer_link
        
        if not self.chain_id:
            try:
                self.chain_id = Web3(Web3.HTTPProvider(self.rpc)).eth.chain_id
            except Exception as e:
                logger.critical(f'Не удалось получить id сети: {e}')

        if not self.coin_symbol:
            try:
                responce = requests.get('https://chainid.network/chains.json').json()
                for network in responce:
                    if network['chainId'] == self.chain_id:
                        self.coin_symbol = network['nativeCurrency']['symbol']
                        break
            except Exception as e:
                logger.critical(f'Не удалось получить символ монеты: {e}')

        if self.coin_symbol:
            self.coin_symbol = self.coin_symbol.upper()


''' ДАННЫЕ ПО СЕТЯМ '''

class Networks:
    networks = {
        'Polygon': Network(
            name = 'Polygon',
            rpc = 'https://polygon-bor-rpc.publicnode.com',
            chain_id = 137,
            coin_symbol = 'POL',
            explorer = 'Polygonscan.com',
            explorer_link = 'https://polygonscan.com/'
        ),

        'Optimism': Network(
            name = 'Optimism',
            rpc = 'https://optimism-rpc.publicnode.com',
            chain_id = 10,
            coin_symbol = 'ETH',
            explorer = 'Optimistic.etherscan.io',
            explorer_link = 'https://optimistic.etherscan.io/'
        ),

        'Arbitrum': Network(
            name = 'Arbitrum',
            rpc = 'https://arbitrum-one-rpc.publicnode.com',
            chain_id = 42161,
            coin_symbol = 'ETH',
            explorer = 'Arbiscan.io',
            explorer_link = 'https://arbiscan.io/'
        ),          

        'Base': Network(
            name = 'Base',
            rpc = 'https://base.meowrpc.com',
            chain_id = 8453,
            coin_symbol = 'ETH',
            explorer = 'Basescan.org',
            explorer_link = 'https://basescan.org/'
        )
    }


''' ШАБЛОН ДЛЯ МОНЕТ '''

class Currency:
    def __init__(self,
                 decimals: int,
                 contract: str,
                 return_price: int | None
) -> None:
        self.decimals = decimals
        self.contract = contract
        self.return_price = return_price


''' ДАННЫЕ ПО МОНЕТАМ В КАЖДОЙ СЕТИ '''

class Currencies:
    currencies = {
            'Polygon':
                {
                    'POL': Currency(
                            decimals = 10 ** 18,
                            contract = None,
                            return_price = return_asset_price
                        ),
                    'USDT': Currency(
                            decimals = 10 ** 6,
                            contract = contracts['usdt_pol'],
                            return_price = None
                        ),
                    'USDC': Currency(
                            decimals = 10 ** 6,
                            contract = contracts['usdc_pol'],
                            return_price = None
                        )
            },
                
            'Optimism':
                {
                    'ETH': Currency(
                            decimals = 10 ** 18,
                            contract = None,
                            return_price = return_asset_price
                        ),
                    'OP': Currency(
                            decimals = 10 ** 18,
                            contract = contracts['op_op'],
                            return_price = return_asset_price
                        ),
                    'USDT': Currency(
                            decimals = 10 ** 6,
                            contract = contracts['usdt_op'],
                            return_price = None
                        ),
                    'USDC': Currency(
                            decimals = 10 ** 6,
                            contract = contracts['usdc_op'],
                            return_price = None
                        )
            },
                
            'Arbitrum':
                {
                    'ETH': Currency(
                            decimals = 10 ** 18,
                            contract = None,
                            return_price = return_asset_price
                        ),
                    'ARB': Currency(
                            decimals = 10 ** 18,
                            contract = contracts['arb_arb'],
                            return_price = return_asset_price
                        ),
                    'USDT': Currency(
                            decimals = 10 ** 6,
                            contract = contracts['usdt_arb'],
                            return_price = None
                        ),
                    'USDC': Currency(
                            decimals = 10 ** 6,
                            contract = contracts['usdc_arb'],
                            return_price = None
                        )
            },  
                
            'Base':
                {
                    'ETH': Currency(
                            decimals = 10 ** 18,
                            contract = None,
                            return_price = return_asset_price
                        ),
                    'USDC': Currency(
                            decimals = 10 ** 6,
                            contract = contracts['usdc_base'],
                            return_price = None
                        ),
                    'DAI': Currency(
                            decimals = 10 ** 18,
                            contract = contracts['dai_base'],
                            return_price = None
                        )
            }  
    } 
