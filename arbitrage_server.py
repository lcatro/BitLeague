
COINEX_USDT_WALLET_ADDRESS = '1MYNZekWtJfpbKX8czU4MPnSdMgZD3Lw4Y'
COINEX_ETH_WALLET_ADDRESS = '0x453343839526ff5156ea3bd1debf6cecbd196b87'
JEX_USDT_WALLET_ADDRESS = '1JsEFoVswu7t5vc7dMCzYsb19pJF9oE83H'
JEX_ETH_WALLET_ADDRESS = '0xbd8a8a7d80e3cbde065a5f5ba94b3caebafb2a37'

'''

    Buy :
    CoinEx using USDT Buy ETH ---> Transer ---> JEX Sell ETH
    
    RollBack :
    JEX using ETH get USDT ---> Transer ---> CoinEx using USDT Buy ETH

'''


class exchange_coinex :
    
    def __init__(self,wallet_address) :
        pass

    def get_ask_tex(self) :
        return 0.001

    def get_bid_tex(self) :
        return 0.001
    
    def withdrew(self) :
        pass
    
    
    
    
    
def calculate_profit(ask_price,bid_price,sell_exchange_object,buy_exchange_object) :
    ask_tex = sell_exchange_object.get_ask_tex()
    bid_tex = buy_exchange_object.get_bid_tex()
    profit = (ask_price - ask_price * ask_tex) - (bid_price + bid_price * bid_tex)
    profit_percent = (profit / bid_price) * 100
    
    return profit,profit_percent
    
    
    

    



print calculate_profit(491.29,475)





























