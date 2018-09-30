
import time

import base_library
import exchange_api
import sql_module
import server_data
import user_manager


def get_rank() :
    result = sql_module.query_data('SELECT * FROM market ORDER BY increase DESC')
    
    if not result :
        return server_data.server_api_result(False,'No Data')
    
    output_result = []
    
    for index in result :
        #simple_k_line_data = get_simple_k_line(index[0])
        
        output_result.append({
            'name' : index[0] ,
            'price' : str(index[1]) ,
            'amount' : str(index[2]) ,
            'increase' : str(index[3]) ,
            #'simple_k_line' : simple_k_line_data.get_data()
        })
    
    return server_data.server_api_result(True,data = output_result)    

def get_coin_info(pair_name) :
    result = sql_module.query_data('SELECT * FROM market WHERE pair = "%s"' % pair_name)
    
    if not result :
        return server_data.server_api_result(False,'No Data')

    result = {
        'pair' : result[0][0] ,
        'price' : str(result[0][1]) ,
        'amount' : str(result[0][2]) ,
        'increase' : str(result[0][3]) ,
        'open' : str(result[0][4]) ,
    }
    
    return server_data.server_api_result(True,data = result)

def get_k_line(pair_name,time_interval = '1min') :
    if '1min' == time_interval :
        result = sql_module.query_data('SELECT * FROM history_market WHERE pair = "%s" ORDER BY timetick LIMIT 1440' % pair_name)
    #elif '3min' == time_interval :
    #elif '5min' == time_interval :
    #elif '15min' == time_interval :
    #elif '1h' == time_interval :
    #elif '4h' == time_interval :
    #elif '12h' == time_interval :
    #elif '1d' == time_interval :
    #elif '1w' == time_interval :
    #    result = sql_module.query_data('SELECT * FROM history_market WHERE pair = "%s" ORDER BY timetick LIMIT 1440' % pair_name)
    
    output_result = []
    
    for index in result :
        output_result.append({
            'open' : str(index[1]) ,
            'close' : str(index[2]) ,
            'max' : str(index[3]) ,
            'min' : str(index[4]) ,
            'timetick' : str(index[5]) ,
            'amount' : str(index[6]) ,
        })
    
    if not result :
        return server_data.server_api_result(False,'No Data')
    
    return server_data.server_api_result(True,data = output_result)
    
def get_simple_k_line(pair_name) :
    SIMPLE_K_LINE_TIME_INTERVAL = 30
    
    result = sql_module.query_data('SELECT close FROM history_market WHERE pair = "%s" AND timeinterval = "1m" ORDER BY timetick LIMIT 1440' % pair_name)
    
    if not result :
        return server_data.server_api_result(False,'No Data')
    
    output_result = []
    
    for index in range(0,len(result),SIMPLE_K_LINE_TIME_INTERVAL) :
        end_search_limit = 0
        
        if index + SIMPLE_K_LINE_TIME_INTERVAL > len(result) :
            end_search_limit = len(result)
        else :
            end_search_limit = index + SIMPLE_K_LINE_TIME_INTERVAL
            
        max_close = 0

        for search_max_index in range(index,end_search_limit) :
            if max_close < result[search_max_index] :
                max_close = str(result[search_max_index][0])

        output_result.append(max_close)
    
    return server_data.server_api_result(True,data = output_result)
    
def get_real_time_deal_record(pair_name) :
    result = sql_module.query_data('SELECT price,amount,timetick FROM history_exchange WHERE pair = "%s" ORDER BY timetick LIMIT 60' % pair_name)
    
    if not result :
        return server_data.server_api_result(False,'No Data')
    
    format_result = []
    
    for index in result :
        format_result.append((float(index[0]),float(index[1]),int(index[2])))
    
    return server_data.server_api_result(True,data = format_result)

def get_depth(pair_name) :
    DEPTH_EXPIRE_DATA_TIME = 5 * 60
    result = sql_module.query_data('SELECT timetick,bid,ask FROM history_depth WHERE pair = "%s" ORDER BY timetick LIMIT 30' % pair_name)
    
    if result :
        timetick = result[0][0]
        exec('bid_list = ' + result[0][1])
        exec('ask_list = ' + result[0][2])
        
        if base_library.get_time_tick() < timetick + DEPTH_EXPIRE_DATA_TIME :
            return server_data.server_api_result(True,data = {
                'timetick' : timetick ,
                'bid' : bid_list ,
                'ask' : ask_list ,
            })
        
    depth_result = exchange_api.exchange.update_depth(pair_name)

    if not depth_result :
        return server_data.server_api_result(False,'No Data')

    return server_data.server_api_result(True,data = depth_result)
    
BUY_SELL_POUNDAGE_RATE = 0.002
    
def order_buy(uid,pair_name,amount,price) :
    symbols_list = exchange_api.exchange.get_all_coin()

    if not pair_name in symbols_list :
        return server_data.server_api_result(False,'Not Found Symbols')

    base_coin = pair_name.split('/')[1]

    if not exchange_api.base_api.is_support_exchange_coin(base_coin) or not exchange_api.base_api.is_exist_coin_pair(pair_name) :
        return server_data.server_api_result(False,'Internal Exchange UnSupport')

    coin_amount = exchange_api.base_api.get_coin_amount(base_coin)

    if amount > coin_amount :
        return server_data.server_api_result(False,'User Coin Amount Less')
    
    order_id = exchange_api.exchange.order_buy(pair_name,amount,price)
    
    if not order_id :
        return server_data.server_api_result(False,'Make Order Except')
        
    poundage = amount * price * BUY_SELL_POUNDAGE_RATE
    
    sql_module.insert_data('INSERT INTO history_exchange(uid,pair,amount,price,poundage,timetick) VALUES (%s,"%s","","%s",%s,%s)' % (uid,pair_name,amount,price,poundage,base_library.get_time_tick()))
    
    return server_data.server_api_result(True)
    
def order_sell(uid,pair_name,amount,price) :
    symbols_list = exchange_api.exchange.get_all_coin()

    if not pair_name in symbols_list :
        return server_data.server_api_result(False,'Not Found Symbols')

    base_coin = pair_name.split('/')[0]

    if not exchange_api.base_api.is_support_exchange_coin(base_coin) or not exchange_api.base_api.is_exist_coin_pair(pair_name) :
        return server_data.server_api_result(False,'Internal Exchange UnSupport')

    coin_amount = exchange_api.base_api.get_coin_amount(base_coin)

    if amount > coin_amount :
        return server_data.server_api_result(False,'User Coin Amount Less')
    
    order_id = exchange_api.exchange.order_sell(pair_name,amount,price)
    
    if not order_id :
        return server_data.server_api_result(False,'Make Order Except')
        
    poundage = amount * price * BUY_SELL_POUNDAGE_RATE
    
    sql_module.insert_data('INSERT INTO history_exchange(uid,pair,amount,price,poundage,timetick) VALUES (%s,"%s","","%s",%s,%s)' % (uid,pair_name,amount,price,poundage,base_library.get_time_tick()))
    
    return server_data.server_api_result(True)
    
def withdraw(uid,coin_name,amount) :
    #if not exchange_api.base_api.is_support_exchange_coin(coin_name) :
    #    return server_data.server_api_result(False,'Not Found Coin')
    
    coin_name = coin_name.lower()
    
    if not len(result) :
        return server_data.server_api_result(False,'User not Bind Withdraw Address')
    
    address = user_manager.get_user_withdraw_address(uid,coin_name)
    
    if not address.get_status() :
        return address
    
    address = address.get_data()
    coin_amount = exchange_api.base_api.get_coin_amount(coin_name)
    
    if amount > coin_amount :
        return server_data.server_api_result(False,'User Coin Amount Less')
    
    withdraw_id = exchange_api.exchange.withdraw(coin_name,amount,address)
    
    if not withdraw_id :
        return server_data.server_api_result(False,'Withdraw Except')
    
