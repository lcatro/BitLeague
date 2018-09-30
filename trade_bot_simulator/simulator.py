
import sys
import time

import trade_bot


BASE_PAIR_NAME = 'ETH/USDT'
BASE_USDT_AMOUNT = 200.0  #  USDT


class user :
    
    @staticmethod
    def get_coin(pair_name) :
        return pair_name.split('/')
        
    @staticmethod
    def calculate_free(price,ask_rate = 0.001) :
        price = price - price * ask_rate

        return price
    
    def __init__(self) :
        self.balance = {}
        self.loan = {}
        
    def set_coin_balance(self,coin_name,value = 0.0) :
        self.balance[coin_name] = value
        self.loan[coin_name] = 0.0
        
    def get_coin_balance(self,coin_name) :
        if not coin_name in self.balance.keys() :
            return False
        
        return self.balance[coin_name]
        
    def get_coin_loan(self,coin_name) :
        if not coin_name in self.loan.keys() :
            return False
        
        return self.loan[coin_name]
        
    def buy(self,pair_name,current_price,amount) :
        base_coin = user.get_coin(pair_name)[1]
        target_coin = user.get_coin(pair_name)[0]
        base_coin_balance = self.get_coin_balance(base_coin)
        target_coin_balance = self.get_coin_balance(target_coin)
        
        if 'all' == amount :
            amount = base_coin_balance
        elif base_coin_balance < amount :
            amount = base_coin_balance
        
        total_buy = amount / current_price
        buy_coin = user.calculate_free(total_buy)
        
        self.set_coin_balance(base_coin,base_coin_balance - amount)
        self.set_coin_balance(target_coin,target_coin_balance + buy_coin)

    def sell(self,pair_name,current_price,amount) :
        base_coin = user.get_coin(pair_name)[1]
        target_coin = user.get_coin(pair_name)[0]
        base_coin_balance = self.get_coin_balance(base_coin)
        target_coin_balance = self.get_coin_balance(target_coin)
        
        if 'all' == amount :
            amount = target_coin_balance
        elif target_coin_balance < amount :
            amount = target_coin_balance
        
        total_sell = amount * current_price
        sell_coin = user.calculate_free(total_sell)
        
        self.set_coin_balance(base_coin,base_coin_balance + sell_coin)
        self.set_coin_balance(target_coin,target_coin_balance - amount)

    def loan(self,coin_name,value,lever_rate = 1,loan_rate = 0.001) :
        coin_balance = self.get_coin_balance(coin_name)
        coin_load = self.loan[coin_name]
        
        if coin_balance - coin_load < value and 0.0 < value :
            value = coin_balance
        
        self.balance[coin_name] += value 
        self.loan[coin_name] += value + value * loan_rate
    
    def revert(self,coin_name,value) :
        coin_load = self.loan[coin_name]
        
        if 0.0 < coin_load and 0.0 < value and value <= coin_load :
            self.balance[coin_name] -= value 
            self.loan[coin_name] -= value
    
    
def record_simulator(time_interval = '5m') :
    data_list = trade_bot.get_k_line_data(trade_bot.exchange_api,BASE_PAIR_NAME,time_interval)
    macd_list = trade_bot.get_macd(data_list)
    simulator_user = user()
    last_strategy = None
    
    simulator_user.set_coin_balance('USDT',BASE_USDT_AMOUNT)
    simulator_user.set_coin_balance('ETH')
    
    for index in range(len(macd_list)) :
        price_index = data_list[index]['close']
        macd_index = macd_list[index]
        current_strategy = trade_bot.is_macd_buy_signal(macd_index)
        
        if None == current_strategy or last_strategy == current_strategy :
            continue
        
        last_strategy = current_strategy
        
        if last_strategy :
            simulator_user.buy(BASE_PAIR_NAME,price_index,'all')
            
            print 'Try to Buy . usdt_value : %f  coin_value : %f' % (simulator_user.get_coin_balance('USDT'),simulator_user.get_coin_balance('ETH'))
        else :
            simulator_user.sell(BASE_PAIR_NAME,price_index,'all')
            
            print 'Try to Sell . usdt_value : %f  coin_value : %f' % (simulator_user.get_coin_balance('USDT'),simulator_user.get_coin_balance('ETH'))
    
    if simulator_user.get_coin_balance('ETH') > 0.0 :
        simulator_user.sell(BASE_PAIR_NAME,price_index,'all')
        
        print 'Sell All Coin . usdt_value : %f  coin_value : %f' % (simulator_user.get_coin_balance('USDT'),simulator_user.get_coin_balance('ETH'))
    
    usdt_value = simulator_user.get_coin_balance('USDT')
    coin_value = simulator_user.get_coin_balance('ETH')
    
    return usdt_value,coin_value,usdt_value > BASE_USDT_AMOUNT

def realtime_simulator(time_interval = '5m') :
    simulator_user = user()
    last_strategy = None
    
    simulator_user.set_coin_balance('USDT',BASE_USDT_AMOUNT)
    simulator_user.set_coin_balance('ETH')
    
    #try :    
    while True :
        data_list = trade_bot.get_k_line_data(trade_bot.exchange_api,BASE_PAIR_NAME,time_interval)
        macd_list = trade_bot.get_macd(data_list)
        last_macd_data = macd_list[-1]
        current_strategy = trade_bot.is_macd_buy_signal(last_macd_data)

        if None == current_strategy :
            print 'Diff is low ,Current State :',last_strategy,last_macd_data,' . usdt_value : %f  coin_value : %f' % (simulator_user.get_coin_balance('USDT'),simulator_user.get_coin_balance('ETH'))

            continue

        if last_strategy == current_strategy :
            print 'No Buy Or Sell ,Current State :',last_strategy,last_macd_data,' . usdt_value : %f  coin_value : %f' % (simulator_user.get_coin_balance('USDT'),simulator_user.get_coin_balance('ETH'))

            continue

        last_strategy = current_strategy
        price_index = data_list[-1]['close']
        
        if last_strategy and usdt_value > 0.0 :
            simulator_user.buy(BASE_PAIR_NAME,price_index,'all')
            
            print 'Try to Buy . usdt_value : %f  coin_value : %f' % (simulator_user.get_coin_balance('USDT'),simulator_user.get_coin_balance('ETH'))
        elif not last_strategy and coin_value > 0.0 :
            simulator_user.sell(BASE_PAIR_NAME,price_index,'all')

            print 'Try to Sell . usdt_value : %f  coin_value : %f' % (simulator_user.get_coin_balance('USDT'),simulator_user.get_coin_balance('ETH'))
        else :
            print 'No Buy Or Sell ,Current State :',last_strategy,last_macd_data,' . usdt_value : %f  coin_value : %f' % (simulator_user.get_coin_balance('USDT'),simulator_user.get_coin_balance('ETH'))
            
        time.sleep(30)
    #except :
    #    pass
    
    if simulator_user.get_coin_balance('ETH') > 0 :
        simulator_user.sell(BASE_PAIR_NAME,price_index,'all')
        
        print 'Sell All Coin . usdt_value : %f  coin_value : %f' % (simulator_user.get_coin_balance('USDT'),simulator_user.get_coin_balance('ETH'))
    
    usdt_value = simulator_user.get_coin_balance('USDT')
    coin_value = simulator_user.get_coin_balance('USDT')
    
    return usdt_value,coin_value,usdt_value > BASE_USDT_AMOUNT


if __name__ == '__main__' :
    if not 2 == len(sys.argv) :
        print 'Using : simulator.py -rc | -rt'
        
        exit()
        
    if '-rc' == sys.argv[1] :
        print record_simulator()
    elif '-rt' == sys.argv[1] :
        print realtime_simulator()
    else :
        print 'Using : simulator.py -rc | -rt'


















