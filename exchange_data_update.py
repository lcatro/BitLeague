
import thread
import threading
import time

import blockchain_wallet
import blockchain_transation_manager
import configure
import exchange_api
import sql_module
import user_manager


DEFAULT_DATA_UPDATE_DELAY = 5
DEFAULT_BLOCKCHAIN_TRANSATION_CHECK_DELAY = 120

thread_exit_lock = threading.Lock()


def background_k_line_update_thread(argument) :
    exchange_object = exchange_api.new_exchange_object()
    exchange = exchange_api.base_api(exchange_object)
        
    while True :
        exchange.update_all_coin()
        
        time.sleep(DEFAULT_DATA_UPDATE_DELAY)
        
def background_depth_update_thread(argument) :
    exchange_object = exchange_api.new_exchange_object()
    exchange = exchange_api.base_api(exchange_object)
        
    while True :
        exchange.update_all_depth()
        
        time.sleep(DEFAULT_DATA_UPDATE_DELAY)
        
def get_new_blockchain_transation(blockchain_trnsation,last_transation) :
    if not last_transation :
        search_index = len(blockchain_trnsation) - 1
    else :
        last_transation_address = last_transation[0]
        last_transation_tx = last_transation[1]
        last_transation_timetick = last_transation[2]
        
        search_index = 0
        search_length = len(blockchain_trnsation)

        if search_index == search_length :
            return []

        while search_index < search_length :
            blockchain_trnsation_index = blockchain_trnsation[search_index]

            if  last_transation_address == blockchain_trnsation_index['from_address'] and \
                last_transation_tx == blockchain_trnsation_index['tx_hash'] and \
                last_transation_timetick == blockchain_trnsation_index['timetick'] :
                break
    
    result = []
    
    while -1 < search_index :
        blockchain_trnsation_index = blockchain_trnsation[search_index]
        address = blockchain_trnsation_index['from_address']
        tx = blockchain_trnsation_index['tx_hash']
        value = blockchain_trnsation_index['value']
        timetick = blockchain_trnsation_index['timetick']
        
        result.append({
            'address' : address ,
            'tx' : tx ,
            'value' : value ,
            'timetick' : timetick ,
        })
        
        search_index -= 1
    
    return result
        
def btc_new_transation_check() :
    btc_address = configure.wallet_address['btc']
    blockchain_btc_transation = blockchain_wallet.get_btc_transation(btc_address)
    last_btc_transation = blockchain_transation_manager.get_last_blockchain_transation('btc')
    new_transation_list = get_new_blockchain_transation(blockchain_btc_transation,last_btc_transation)

    for new_transation_index in new_transation_list :
        address = new_transation_index['address']
        tx = new_transation_index['tx']
        value = new_transation_index['value']
        timetick = new_transation_index['timetick']
        uid = user_manager.query_user_by_withdraw_address('btc',address)

        if not uid.get_status() :
            continue

        uid = uid.get_data()
        balance = user_manager.get_user_balance('btc',uid)

        if not balance.get_status() :
            continue

        balance += value

        user_manager.set_user_balance('btc',uid,balance)
        blockchain_transation_manager.add_blockchain_transation('btc',address,tx,timetick)
    
def eth_new_transation_check() :
    eth_address = configure.wallet_address['eth']
    blockchain_eth_transation = blockchain_wallet.get_eth_transation(eth_address)
    last_eth_transation = blockchain_transation_manager.get_last_blockchain_transation('eth')
    new_transation_list = get_new_blockchain_transation(blockchain_eth_transation,last_eth_transation)

    for new_transation_index in new_transation_list :
        address = new_transation_index['address']
        tx = new_transation_index['tx']
        value = new_transation_index['value']
        timetick = new_transation_index['timetick']
        uid = user_manager.query_user_by_withdraw_address('eth',address)

        if not uid.get_status() :
            continue

        uid = uid.get_data()
        balance = user_manager.get_user_balance('eth',uid)

        if not balance.get_status() :
            continue

        balance += value

        user_manager.set_user_balance('eth',uid,balance)
        blockchain_transation_manager.add_blockchain_transation('eth',address,tx,timetick)
    
def background_deposit_thread(argument) :
    while True :
        try :
            btc_new_transation_check()
        except :
            pass
        
        try :
            eth_new_transation_check()
        except :
            pass
        
        time.sleep(DEFAULT_BLOCKCHAIN_TRANSATION_CHECK_DELAY)
        
def background_update() :
    print 'Exchange K-line Data Thread Booting'
    
    thread.start_new_thread(background_k_line_update_thread,(None,))
    
    print 'Exchange Depth Data Thread Booting'
    
    thread.start_new_thread(background_depth_update_thread,(None,))
    
    print 'BlockChain Wallet Transation Thread Booting'
    
    thread.start_new_thread(background_deposit_thread,(None,))

def loop() :
    try :
        thread_exit_lock.acquire()
    except :
        print 'Are you want to Exit:(y/n)'
        
        key = str(input()).lower()
        
        if 'y' == key :
            exit()            
            

if __name__ == '__main__' :
    print 'Exchange Data Update Thread Ready Load ..'
    
    thread_exit_lock.acquire()
    
    print 'Exchange Data Update Thread is Booting ..'
    
    while True :
        loop()
    
    print 'Exchange Data Update Thread has Shutdown !'

