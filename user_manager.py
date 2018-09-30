
import random
import re
import time

import email_api
import base_library
import sql_module
import server_data


VALID_CODE_EXPIER_TIME = 5 * 60 * 1000


def is_legal_user_name(user_name) :
    if re.match('[\w]+(?:\.[\w]+)*@(?:[\w](?:[\w-]*[\w])?\.)+[\w](?:[\w-]*[\w])?',user_name) :
        return True
    
    return False

def is_exist_user(user_name) :
    result = sql_module.query_data('SELECT * FROM user_info WHERE name="%s"' % user_name)
    
    if result :
        return server_data.server_api_result(True)
    
    return server_data.server_api_result(False,'Not Found User')

def is_active_user(user_name) :
    result = sql_module.query_data('SELECT active FROM user_info WHERE name="%s"' % user_name)
    
    if result :
        if result[0][0] == 1 :
            return server_data.server_api_result(True)
    
    return server_data.server_api_result(False,'This User was not Active')

def is_not_expier_valid_code_time(user_name) :
    result = sql_module.query_data('SELECT valid_code_make_time FROM user_info WHERE name="%s"' % user_name)
    
    if result :
        if base_library.get_time_tick() <= result[0][0] + VALID_CODE_EXPIER_TIME :
            return server_data.server_api_result(True)
    
    return server_data.server_api_result(False,'Valid Code Expire')

def check_valid_code(user_name,valid_code) :
    if not is_legal_user_name(user_name) :
        return server_data.server_api_result(False,'Is illegal User Name')
    
    if not is_not_expier_valid_code_time(user_name).get_status() :
        return server_data.server_api_result(False,'Valid Code Expire')
    
    result = sql_module.query_data('SELECT valid_code FROM user_info WHERE name="%s"' % user_name)
    
    if result :
        if result[0][0] == valid_code :
            return server_data.server_api_result(True)
    
    return server_data.server_api_result(False,'Valid Code Error')

def get_uid_by_user_name(user_name) :
    result = sql_module.query_data('SELECT uid FROM user_info WHERE name="%s"' % user_name)
    
    if result :
        return server_data.server_api_result(True,data = result[0][0])
    
    return server_data.server_api_result(False,'Not Found')

def make_new_valid_code(user_name) :
    valid_code = base_library.make_random_code()
    
    sql_module.insert_data('UPDATE user_info SET valid_code = "%s" , valid_code_make_time = %s WHERE name = "%s"' % \
                           (valid_code,base_library.get_time_tick(),user_name))
    
    return valid_code

def make_new_user(user_name) :
    if not is_legal_user_name(user_name) :
        return server_data.server_api_result(False,'Is illegal User Name')
    
    valid_code = None
    
    if not is_exist_user(user_name).get_status() :
        valid_code = base_library.make_random_code()
        
        sql_module.insert_data('INSERT INTO user_info(name,password,valid_code,valid_code_make_time) VALUES ("%s","","%s",%s)' % \
                               (user_name,valid_code,base_library.get_time_tick()))
    else :
        valid_code = make_new_valid_code(user_name)
    
    #email_api.send_valid_code_email(user_name,valid_code)
    
    return valid_code

def init_user(user_name,user_password) :
    uid_data = get_uid_by_user_name(user_name)
    
    if not uid_data.get_status() :
        return server_data.server_api_result(False,uid_data.get_description())
    
    sql_module.insert_data('UPDATE user_info SET password = "%s" , active = 1 WHERE name = "%s"' % \
                           (user_password,user_name))
    
    uid = uid_data.get_data()
    
    sql_module.insert_data('INSERT INTO user_address(uid,bind_btc_address,bind_eth_address,bind_usdt_address) VALUES (%s)' % (uid))
    sql_module.insert_data('INSERT INTO user_coin(uid) VALUES (%s)' % (uid))
    
    return server_data.server_api_result(True)
        
def regedit_new_user(user_name,user_password,valid_code) :
    if not is_legal_user_name(user_name) :
        return server_data.server_api_result(False,'Is illegal User Name')
    
    if is_active_user(user_name).get_status() :
        return server_data.server_api_result(False,'User has Regedit')
    
    valid_code_status = check_valid_code(user_name,valid_code)
    
    if not valid_code_status.get_status() :
        return server_data.server_api_result(False,valid_code_status.get_description())
    
    return init_user(user_name,user_password)

def login(user_name,user_password) :
    if not is_legal_user_name(user_name) :
        return server_data.server_api_result(False,'Is illegal User Name')
    
    if not is_active_user(user_name).get_status() :
        return server_data.server_api_result(False,'User has not Regedit')
    
    result = sql_module.query_data('SELECT password FROM user_info WHERE name = "%s"' % user_name)
    
    if result :
        if result[0][0] == user_password :
            return server_data.server_api_result(True)
    
    return server_data.server_api_result(False,'User or Password incorrect')

def get_user_coin(uid) :
    result = sql_module.query_data('SELECT * FROM user_address WHERE uid = %s' % uid)
    
    if result :
        result = []
        
        return server_data.server_api_result(True,data = result)
    
    return server_data.server_api_result(False,'Not Found')

def set_user_withdraw_address(uid,coin_name,address) :
    coin_name = coin_name.lower()
    
    if 'btc' == coin_name :
        sql_module.insert_data('UPDATE user_address SET bind_btc_address = "%s" WHERE uid = "%s"' % (address,uid))
    elif 'eth' == coin_name :
        sql_module.insert_data('UPDATE user_address SET bind_eth_address = "%s" WHERE uid = "%s"' % (address,uid))
    elif 'usdt' == coin_name :
        sql_module.insert_data('UPDATE user_address SET bind_usdt_address = "%s" WHERE uid = "%s"' % (address,uid))
    else :
        return server_data.server_api_result(False,'UnSupport Coin')
    
    return server_data.server_api_result(True)

def get_user_withdraw_address(uid,coin_name) :
    coin_name = coin_name.lower()
    
    if 'btc' == coin_name :
        result = sql_module.query_data('SELECT bind_btc_address FROM user_address WHERE uid = "%s" LIMIT 1' % uid)
    elif 'eth' == coin_name :
        result = sql_module.query_data('SELECT bind_eth_address FROM user_address WHERE uid = "%s" LIMIT 1' % uid)
    elif 'usdt' == coin_name :
        result = sql_module.query_data('SELECT bind_usdt_address FROM user_address WHERE uid = "%s" LIMIT 1' % uid)
    else :
        return server_data.server_api_result(False,'UnSupport Coin')
    
    if len(result) :
        return server_data.server_api_result(True,data = result[0][0])
    
    return server_data.server_api_result(False,'No Bind')

def query_user_by_withdraw_address(coin_name,address) :
    coin_name = coin_name.lower()
    
    if 'btc' == coin_name :
        result = sql_module.query_data('SELECT uid FROM user_address WHERE bind_btc_address = "%s" LIMIT 1' % address)
    elif 'eth' == coin_name :
        result = sql_module.query_data('SELECT uid FROM user_address WHERE bind_eth_address = "%s" LIMIT 1' % address)
    elif 'usdt' == coin_name :
        result = sql_module.query_data('SELECT uid FROM user_address WHERE bind_usdt_address = "%s" LIMIT 1' % address)
    else :
        return server_data.server_api_result(False,'UnSupport Coin')

    if len(result) :
        return server_data.server_api_result(True,data = result[0][0])
    
    return server_data.server_api_result(False,'Not Found')

def get_coin_list() :
    result = sql_module.query_data('SELECT column_name FROM information_schema.columns WHERE table_schema = "backend" And table_name = "user_coin"')
    
    return result[0]

def get_user_balance(uid,coin_name) :
    coin_name = coin_name.lower()
    result = sql_module.query_data('SELECT %s FROM user_coin WHERE uid = "%s"' % (coin_name,uid))
    
    if not len(result) :
        return server_data.server_api_result(False,'No Data')
    
    if len(result) :
        return server_data.server_api_result(True,data = float(result[0][0]))
    
    return server_data.server_api_result(False,'Not Found')

def set_user_balance(uid,coin_name,new_balance) :
    new_balance = float(new_balance)
    
    if new_balance < 0 :
        return server_data.server_api_result(False,'New Balance less than 0')
    
    coin_name = coin_name.lower()
    
    sql_module.insert('UPDATE user_coin SET %s = %f WHERE uid = "%s"' % (coin_name,new_balance,uid))
    
    return server_data.server_api_result(True)



