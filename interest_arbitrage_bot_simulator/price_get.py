
import ccxt
import json
import requests


def get_coin_price_from_coinex(pair_name) :
    try :
        coinex = ccxt.coinex()
        data = coinex.fetchTicker(pair_name)

        return data['ask'],data['bid'],data['last'],get_coin_depth_from_coinex(pair_name)
    except :
        return get_coin_price_from_coinex(pair_name)

def get_coin_depth_from_coinex(pair_name) :
    try :
        coinex = ccxt.coinex()
        data = coinex.fetchOrderBook(pair_name)

        return data['asks'][0][1]
    except :
        return get_coin_depth_from_coinex(pair_name)

def get_coin_price_from_9coin(pair_name) :
    try :
        responed = requests.get('https://www.9coin.com/home/api/tickers')
        data = json.loads(responed.text)['data']
        pair_name = pair_name.replace('/','_')

        for search_index in data :
            if not search_index['cy_mark'] == pair_name :
                continue

            return float(search_index['buy_one_price']),float(search_index['sell_one_price']),float(search_index['new_price']),get_coin_depth_from_9coin(pair_name)

        return False
    except :
        return get_coin_price_from_9coin(pair_name)

def get_coin_depth_from_9coin(pair_name) :
	try :
		responed = requests.post('https://www.9coin.com/home/api/buy',data = {
			'cy_id' : '27' , #pair_name.replace('/','_')
		},timeout = 5)
		bid_data = json.loads(responed.text)['data']
		responed = requests.post('https://www.9coin.com/home/api/sell',data = {
			'cy_id' : '27' , #pair_name.replace('/','_')
		},timeout = 5)
		ask_data = json.loads(responed.text)['data']

		return float(bid_data[0]['wtlnum'])
	except :
		return get_coin_depth_from_9coin(pair_name)


#get_coin_depth_from_9coin('ETH/BTC')
#print get_coin_price_from_coinex('ETH/BTC')
#print get_coin_price_from_9coin('ETH/BTC')

