
import ccxt

DEFAULT_SHAKE_LIMIT_VALUE = 0.1


def get_k_line_data(exchange_object,pair_name,time_interval = '1m',timetick = None) :
    try :
        format_result = []

        #try :
        if not None == timetick :
            k_line_data = exchange_object.fetch_ohlcv(pair_name,time_interval,timetick)
        else :
            k_line_data = exchange_object.fetch_ohlcv(pair_name,time_interval)
        #except :
        #    return False

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
    except :
        pass
    
    return get_k_line_data(exchange_object,pair_name,time_interval,timetick)

def get_ema(data_list,coefficient) :
    ema_result = []
    coefficient = 2.0 / (coefficient + 1)
    
    for data_index in range(len(data_list)) :
        data = data_list[data_index]
        
        if 0 == data_index :
            ema_result.append(data['close'])
        else :
            last_data = ema_result[data_index - 1]
            
            ema_result.append((1 - coefficient) * last_data + coefficient * data['close'])
    
    return ema_result
    
def get_diff(short_ema,long_ema) :
    if not len(short_ema) == len(long_ema) :
        return False
    
    diff_result = []
    
    for index in range(len(short_ema)) :
        diff_result.append(short_ema[index] - long_ema[index])
        
    return diff_result
    
def get_dea(data_list) :
    dea_result = []
    m_coefficient = 9
    coefficient = 2.0 / (m_coefficient + 1)
    
    for data_index in range(len(data_list)) :
        data = data_list[data_index]
        
        if 0 == data_index :
            dea_result.append(data)
        else :
            last_data = dea_result[data_index - 1]
            
            dea_result.append((1 - coefficient) * last_data + coefficient * data)
    
    return dea_result
    
def get_macd(data) :
    short_ema = get_ema(data,12)
    long_ema = get_ema(data,26)
    diff_ema = get_diff(short_ema,long_ema)
    dea_result = get_dea(diff_ema)
    macd_result = []
    
    for diff_index in range(len(diff_ema)) :
        diff_data = diff_ema[diff_index]
        dea_data = dea_result[diff_index]
        
        macd_result.append(2 * (diff_data - dea_data))
    
    return macd_result

def is_macd_buy_signal(macd_value) :
    if  -DEFAULT_SHAKE_LIMIT_VALUE > macd_value :
        return False
    elif DEFAULT_SHAKE_LIMIT_VALUE < macd_value :
        return True
    
    return None


exchange_api = ccxt.coinex()

exchange_api.load_markets()


if __name__ == '__main__' :
    data = get_k_line_data(exchange_api,'ETH/USDT','5m')

    if data : 
        print get_macd(data)
    else :
        print 'Get K-Line Error'








