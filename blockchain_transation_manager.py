
import sql_module


def add_blockchain_transation(coin_name,address,tx,timetick) :
    sql_module.insert_data('INSERT INTO history_transation(coin,address,tx,timetick) VALUES ("%s","%d","%s",%s)' % (coin_name,address,tx,timetick))
    
def get_last_blockchain_transation(coin_name) :
    result = sql_module.query_data('SELECT address,tx,timetick FROM history_transation WHERE coin = "%s" ORDER BY timetick LIMIT 1' % coin_name)
    
    if len(result) :
        return (result[0][0],result[0][1],int(result[0][2]))
    
    return False

def get_transation(coin_name,address) :
    result = sql_module.query_data('SELECT tx,timetick FROM history_transation WHERE coin = "%s" And address = "%s"' % (coin_name,address))
    
    if len(result) :
        output_result = []
        
        for index in result :
            output_result.append((index[0],int(index[1])))
        
        return result
    
    return False
    
