
import time

import ccxt

import base_library
import configure
import sql_module


class base_api :
    
    def __init__(self,exchange_object) :
        exchange_object.load_markets()
        
        self.exchange_object = exchange_object
        
    def get_all_coin(self) :
        return self.exchange_object.symbols
        
    def get_all_coin_info(self) :
        symbols_list = self.get_all_coin()
        result = []
        
        for index in symbols_list :
            data = self.exchange_object.fetch_ticker(index)
            
            result.append({
                'pair' : index ,
                'amount' : data['info']['vol'] ,
                'price' : data['info']['sell'] ,
                'last' : data['info']['last'] ,
            })
            
        return result
        
    def get_k_line_data(self,pair_name,time_interval = '1m',timetick = None) :
        format_result = []
        
        try :
            if not None == timetick :
                k_line_data = self.exchange_object.fetch_ohlcv(pair_name,time_interval,timetick)
            else :
                k_line_data = self.exchange_object.fetch_ohlcv(pair_name,time_interval)
        except :
            return False
        
        for index in k_line_data :
            format_result.append({
                'time' : index[0] ,
                'open' : index[1] ,
                'max' : index[2] ,
                'min' : index[3] ,
                'close' : index[4] ,
                'amount' : index[5]
            })
        
        return format_result
    
    def get_depth(self,pair_name,limit = None) :
        try :
            result = {
                'timetick' : base_library.get_time_tick() ,
            }

            if not None == limit :
                data = self.exchange_object.fetch_order_book(pair_name,limit)
            else :
                data = self.exchange_object.fetch_order_book(pair_name)

            result['bid'] = data['bids']
            result['ask'] = data['asks']

            return result
        except :
            return False
    
    def fetch_ticker(self,pair_name) :
        try :
            return self.exchange_object.fetch_ticker(pair_name)
        except :
            return False
        
    @staticmethod
    def is_exist_k_line_data(pair_name,time_tick,time_interval) :
        result = sql_module.query_data('SELECT * FROM history_market WHERE pair = "%s" and timetick = %s and timeinterval = "%s"' % \
                                       (pair_name,time_tick,time_interval))

        if result :
            return True

        return False

    def fill_k_line_data(self,pair_name = 'BTC/USDT',time_interval = '1m') :
        k_line_data = self.get_k_line_data(pair_name,time_interval)

        if not k_line_data :
            return

        last_k_line_data = k_line_data[-1]

        for index in k_line_data :
            if base_api.is_exist_k_line_data(pair_name,index['time'],time_interval) :
                continue

            #print 'Add New K-Line Data:',index

            sql_module.insert_data('INSERT INTO history_market(pair,open,close,max,min,timetick,amount,timeinterval) VALUES ("%s",%s,%s,%s,%s,%s,%s,"%s")' % \
                                   (pair_name,index['open'],index['close'],index['max'],index['min'],index['time'],index['amount'],time_interval))

    @staticmethod
    def is_exist_coin_pair(pair_name) :
        result = sql_module.query_data('SELECT * FROM market WHERE pair = "%s" ' % (pair_name))

        if result :
            return True

        return False
    
    def update_depth(self,pair_name) :
        data = self.get_depth(pair_name)

        if not data :
            return False

        #print 'update_depth()  Add New Coin Depth:',pair_name

        sql_module.insert_data('INSERT INTO history_depth(pair,timetick,bid,ask) VALUES ("%s",%s,"%s","%s")' % \
                               (pair_name,data['timetick'],str(data['bid']),str(data['ask'])))
        
        return data
        
    def update_all_depth(self) :
        symbols_list = self.get_all_coin()
        result = []
        
        for pair_name in symbols_list :
            data = self.update_depth(pair_name)
            
            if data :
                result.append(data)
            
        return result

    def update_all_coin(self) :
        symbols_list = self.get_all_coin()

        for pair_name in symbols_list :
            data = self.fetch_ticker(pair_name)
            try :
                amount = data['info']['vol']
                price = data['info']['sell']
            except :
                pass

            if base_api.is_exist_coin_pair(pair_name) :
                #print 'Update Coin Data:',pair_name

                now_time = time.localtime()

                if 0 == now_time.tm_hour and 0 == now_time.tm_min and 0 == now_time.tm_sec :
                    sql_module.insert_data('UPDATE market SET price = %s , open = %s , amount = %s , increase = 0 WHERE pair = "%s"' % \
                                           (price,amount,pair_name))
                else :
                    result = sql_module.query_data('SELECT open FROM market WHERE pair = "%s" ' % (pair_name))

                    if result :
                        open_price = float(result[0][0])
                        now_price  = float(price)

                        if float(price) >= open_price :
                            increase = (now_price - open_price) / open_price
                        else :
                            increase = (open_price - now_price) / open_price

                        sql_module.insert_data('UPDATE market SET price = %s , amount = %s , increase = %.3f WHERE pair = "%s"' % \
                                               (price,amount,increase,pair_name))
                    
            else :
                #print 'Add New Coin Data:',pair_name

                sql_module.insert_data('INSERT INTO market(pair,price,open,amount,increase) VALUES ("%s",%s,%s,%s,0)' % \
                                       (pair_name,price,price,amount))
            
            self.fill_k_line_data(pair_name)
        
    @staticmethod
    def is_support_exchange_coin(coin_name) :
        result = sql_module.query_data('select COLUMN_NAME from information_schema.COLUMNS where table_name = "user_coin"')
        coin_name = 'coin_%s' % coin_name
        
        if len(result) :
            if len(result[0]) :
                for index in result[0] :
                    if coin_name == index :
                        return True
        
        return False
        
    @staticmethod
    def get_coin_amount(uid,coin_name) :
        coin_name = 'coin_%s' % coin_name
        result = sql_module.query_data('select %s from user_coin where uid = "%d"' % (coin_name,uid))
        
        if len(result) :
            return result[0]
        
        return False
    
    def order_buy(pair_name,amount,price) :
        try :
            return self.exchange_object.create_order(pair_name,'limit','buy',amount,price)['id']
        except :
            return False
        
    def order_sell(pair_name,amount,price) :
        try :
            return self.exchange_object.create_order(pair_name,'limit','sell',amount,price)['id']
        except :
            return False
        
    def withdraw(coin_name,amount,address) :
        try :
            return self.exchange_object.withdraw(coin_name,amount,address)['id']
        except :
            return False
        
        
def new_exchange_object() :
    api_key = configure.exchange_api['coinex']['api_key']
    secret_key = configure.exchange_api['coinex']['secret_key']
    
    try :
        exec('''exchange_api = ccxt.%s({"apiKey": "%s","secret": "%s"})''' % ('coinex',api_key,secret_key))
    except Exception ,e:
        print 'new_exchange_object Except',e
        
        exchange_api = new_exchange_object()
        
    return exchange_api
        
    
#exchange_api_list = configure.exchange_api
#for exchange_index in exchange_api_list :
#exec('exchange_api = ccxt.%s({"apiKey": "%s","secret": "%s"})' % (exchange_index,api_key,secret_key))

#exec('''exchange_api = ccxt.%s({"apiKey": "%s","secret": "%s","proxies": {
#    "http" : "%s" ,
#    "https" : "%s" ,
#}})''' % ('okex',api_key,secret_key,configure.proxy['http'],configure.proxy['https']))
#exec('''exchange_api = ccxt.%s({"apiKey": "%s","secret": "%s"})''' % ('coinex',api_key,secret_key))
exchange_api = new_exchange_object()
exchange = base_api(exchange_api)




if __name__ == '__main__' :
    print exchange.update_depth('ETH/BTC')
    
    #while True :
    #exchange.update_all_depth()
    #exchange.update_all_coin()
    #data = exchange.get_k_line_data('BTC/USDT',timetick = 1)

    #print int(time.time() * 1000)
    #print data[-1]

    #fill_k_line_data(exchange)
    #fill_k_line_data(exchange,'5m')
    #fill_k_line_data(exchange,'4h')
    #fill_k_line_data(exchange,'1d')

    #update_all_coin(exchange)


