
import time

import price_get


PRICE_LIMIT_PERSENT = 0.05
BASE_ETH_AMOUR = 5
BASE_BTC_AMOUR = 0.8
BASE_BTC_PRICE = 48000
ALERT_ETH_AMOUR = 0.4
ALERT_BTC_AMOUR = 0.1


def calculate(ask_price,bid_price,ask_rate = 0.001,bid_rate = 0.001) :
    price = (ask_price - ask_price * ask_rate) - (bid_price + bid_price * bid_rate)

    return price , price / bid_price * 100

def withdrew(coin_name,amount) :
    if 'ETH' == coin_name :
        return amount - 0.01
    elif 'BTC' == coin_name :
        return amount - 0.001
    #elif 'BTC' == coin_name :
    #    return amount - amount * 0.5


money_list = {
    'coinex' : {
        'ETH' : BASE_ETH_AMOUR ,
        'BTC' : BASE_BTC_AMOUR } ,
    '9coin'  : {
        'ETH' : BASE_ETH_AMOUR ,
        'BTC' : BASE_BTC_AMOUR }
}
count = 0.0
start_time = time.time()

while True :
    price_coinex = price_get.get_coin_price_from_coinex('ETH/BTC')
    price_9coin = price_get.get_coin_price_from_9coin('ETH/BTC')
    data = calculate(price_coinex[2],price_9coin[2])

    if PRICE_LIMIT_PERSENT > abs(data[1]) :
        print 'No Trade ..  Data = ',data

        time.sleep(10)
        continue

    min_amount = min(price_coinex[3],price_9coin[3])

    if price_coinex[2] > price_9coin[2] :
        money_list['9coin']['ETH']  += min_amount
        money_list['9coin']['BTC']  -= min_amount * price_9coin[2]
        money_list['coinex']['ETH'] -= min_amount
        money_list['coinex']['BTC'] += min_amount * price_coinex[2]
    else :
        money_list['9coin']['ETH']  -= min_amount
        money_list['9coin']['BTC']  += min_amount * price_9coin[2]
        money_list['coinex']['ETH'] += min_amount
        money_list['coinex']['BTC'] -= min_amount * price_coinex[2]
    
    if ALERT_ETH_AMOUR > money_list['9coin']['ETH'] and ALERT_ETH_AMOUR > money_list['coinex']['ETH'] :
        print 'WARNING ! System Except !! ETH less'
        
        exit()
    elif ALERT_BTC_AMOUR > money_list['9coin']['BTC'] and ALERT_BTC_AMOUR > money_list['coinex']['BTC'] :
        print 'WARNING ! System Except !! BTC less'
        
        exit()
    elif ALERT_ETH_AMOUR > money_list['9coin']['ETH'] :
        print 'Trigger ETH Withdrew : coinex -> 9coin'
        
        tracese_money = (money_list['coinex']['ETH'] + money_list['9coin']['ETH']) / 2
        withdrew_money = withdrew('ETH',tracese_money)
        
        money_list['coinex']['ETH'] -= tracese_money
        money_list['9coin']['ETH']  += withdrew_money
    elif ALERT_ETH_AMOUR > money_list['coinex']['ETH'] :
        print 'Trigger ETH Withdrew : 9coin -> coinex'
        
        tracese_money = (money_list['coinex']['ETH'] + money_list['9coin']['ETH']) / 2
        withdrew_money = withdrew('ETH',tracese_money)
        
        money_list['9coin']['ETH']  -= tracese_money
        money_list['coinex']['ETH'] += withdrew_money
    elif ALERT_BTC_AMOUR > money_list['9coin']['BTC'] :
        print 'Trigger BTC Withdrew : coinex -> 9coin'
        
        tracese_money = (money_list['coinex']['BTC'] + money_list['9coin']['BTC']) / 2
        withdrew_money = withdrew('BTC',tracese_money)
        
        money_list['coinex']['BTC'] -= tracese_money
        money_list['9coin']['BTC']  += withdrew_money
    elif ALERT_BTC_AMOUR > money_list['coinex']['BTC'] :
        print 'Trigger BTC Withdrew : 9coin -> coinex'
        
        tracese_money = (money_list['coinex']['BTC'] + money_list['9coin']['BTC']) / 2
        withdrew_money = withdrew('BTC',tracese_money)
        
        money_list['9coin']['BTC']  -= tracese_money
        money_list['coinex']['BTC'] += withdrew_money
        
    
    count += abs(data[0]) * min_amount

    print 'Timetick:',time.time() - start_time
    print 'CoinEx:',price_coinex,'9Coin:',price_9coin,'Earn:',data[0],data[1]
    print 'Count =',count,' Match Amount =',min_amount,'All Earn Momey',count * BASE_BTC_PRICE
    print 'Money List  ',money_list['coinex'],'  ',money_list['9coin']
    print 'Diff  BTC:',money_list['coinex']['BTC'] + money_list['9coin']['BTC'] - BASE_BTC_AMOUR * 2
    print 'Diff  ETH:',money_list['coinex']['ETH'] + money_list['9coin']['ETH'] - BASE_ETH_AMOUR * 2

    time.sleep(60)


