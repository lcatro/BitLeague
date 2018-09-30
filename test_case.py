
import json
import random
import requests


global_router = {
    'GET' : [
        'get_rank' , 'get_coin' , 'get_simple_k_line' , 'get_deal_record'
    ] ,
    'POST' : [ 
        'check_exist_name' , 'make_valid_code' , 'regeist_user' , 'login' , 'get_user_coin' 
    ]
}


class test_case_result :
    
    def __init__(self,result,data = None) :
        self.result = result
        self.data   = data
        
    def __str__(self) :
        return str(self.result)
        
    def get_result(self) :
        return self.result
    
    def get_data(self) :
        return self.data
        

def test_case_check_exist_name() :
    exist_name = 'root'
    exist_name_no_active = 'admin'
    no_exist_name = '32jasd8123'
    
    responed_exist = requests.post('http://127.0.0.1:8088/router?router=check_exist_name',data = {
        'user' : exist_name ,
    })
    responed_exist_but_no_active = requests.post('http://127.0.0.1:8088/router?router=check_exist_name',data = {
        'user' : exist_name_no_active ,
    })
    responed_no_exist = requests.post('http://127.0.0.1:8088/router?router=check_exist_name',data = {
        'user' : no_exist_name ,
    })
    
    responed_exist_data = json.loads(responed_exist.text)
    responed_exist_but_no_active_data = json.loads(responed_exist_but_no_active.text)
    responed_no_exist_data = json.loads(responed_no_exist.text)
    
    print 'test_case_check_exist_name() responed_exist_data status:',responed_exist_data['status']
    print 'test_case_check_exist_name() responed_exist_but_no_active_data status:',responed_exist_but_no_active_data['status']
    print 'test_case_check_exist_name() responed_no_exist_data status:',responed_no_exist_data['status']
    
    if responed_exist_data['status'] and not responed_exist_but_no_active_data['status'] and not responed_no_exist_data['status'] :
        return test_case_result(True)
    
    return test_case_result(False)
    
def test_case_make_valid_code() :
    test_user_name = 'emsk1'
    responed = requests.post('http://127.0.0.1:8088/router?router=make_valid_code',data = {
        'user' : test_user_name ,
    })
    responed_data = json.loads(responed.text)
    
    print 'test_case_make_valid_code() responed_data status:',responed_data['status']
    print 'test_case_make_valid_code() responed_data valid_code:',responed_data['data']
    
    if responed_data['data'] :
        if len(responed_data['data']) :
            return test_case_result(True)
    
    return test_case_result(False)
    
def test_case_regeist_user() :
    test_user_name = 'test_regester' + str(random.randint(0,999999))
    responed_make_user = requests.post('http://127.0.0.1:8088/router?router=make_valid_code',data = {
        'user' : test_user_name ,
    })
    responed_make_user_data = json.loads(responed_make_user.text)
    
    print 'test_case_regeist_user() responed_data make_valid_code status:',responed_make_user_data['status']
    
    if not responed_make_user_data['status'] :
        print 'test_case_regeist_user() responed_data make_valid_code status Error'
                                           
        return test_case_result(False)
    
    valid_code = responed_make_user_data['data']
    
    responed_regeist = requests.post('http://127.0.0.1:8088/router?router=regeist_user',data = {
        'user' : test_user_name ,
        'pass' : '1234' ,
        'valid_code' : valid_code ,
    })
    responed_regeist_data = json.loads(responed_regeist.text)
    
    print 'test_case_regeist_user() responed_data regeist status:',responed_regeist_data['status']
    
    if responed_regeist_data['status'] :
        return test_case_result(True,test_user_name)
    
    print 'test_case_regeist_user() responed_data regeist Error:',responed_regeist_data['description']
    
    return test_case_result(False)
    
def test_case_login(test_login_user_name = 'root',test_login_user_password = 'root') :
    responed = requests.post('http://121.42.179.107:8088/router?router=login',data = {
        'user' : test_login_user_name ,
        'pass' : test_login_user_password ,
    })
    print responed.text
    responed_data = json.loads(responed.text)
    
    print 'test_case_login() responed_data make_valid_code status:',responed_data['status']
    
    if not responed_data['status'] :
        print 'test_case_login() responed_data make_valid_code status Error'
                                           
        return test_case_result(False)
    
    #session_id = responed.headers['Set-Cookie']
    #session_id = session_id[ : session_id.find(';')]
    #session_id = session_id.split('=')[1]
    session_id = responed_data['data'][0]
    
    print 'test_case_login() responed_data return cookie:',session_id
    
    return test_case_result(True,session_id)
    
def test_case_logout(test_session_id) :
    responed_no_session = requests.post('http://127.0.0.1:8088/router?router=logout')
    responed_no_session_data = json.loads(responed_no_session.text)
    
    print 'test_case_logout() responed_no_session status:',responed_no_session_data['status']
    
    if responed_no_session_data['status'] :
        print 'test_case_logout() responed_no_session_data logic Error'
                                           
        return test_case_result(False)
    
    print 'test_case_logout() test_session_id:',test_session_id
    
    responed_take_session = requests.post('http://127.0.0.1:8088/router?router=logout',cookies = {
        'session' : test_session_id ,
    })
    responed_take_session_data = json.loads(responed_take_session.text)
    
    print 'test_case_logout() responed_take_session status:',responed_take_session_data['status']
    
    if responed_take_session_data['status'] :
        return test_case_result(True)
    
    return test_case_result(False)
    
def test_case_get_user_coin(test_session_id) :
    responed = requests.post('http://121.42.179.107:8088/router?router=get_user_coin',cookies = {
        'session' : test_session_id ,
    })
    responed_data = json.loads(responed.text)
    
    print 'test_case_get_user_coin() responed_data status:',responed_data['status']
    
    if not responed_data['status'] :
        print 'test_case_get_user_coin() responed_data Error',responed_data['description']
                                           
        return test_case_result(False)
    
    print 'test_case_get_user_coin() responed_data Success ,Data =',responed_data['data']
    
    return test_case_result(True)

def test_get_increase_rank() :
    responed = requests.get('http://127.0.0.1:8088/router?router=get_rank')
    responed_data = json.loads(responed.text)
    
    print 'test_get_increase_rank() responed_data status:',responed_data['status']
    
    if not responed_data['status'] :
        print 'test_get_increase_rank() responed_data Error'
                                           
        return test_case_result(False)
    
    print 'test_get_increase_rank() responed_data data',len(responed_data['data'])
    
    if len(responed_data['data']) :                                           
        return test_case_result(True)
    
    return test_case_result(False)

def test_get_real_time_deal_record() :
    responed = requests.get('http://127.0.0.1:8088/router?router=get_deal_record',data = {
        'coin' : 'BTC/USDT'
    })
    responed_data = json.loads(responed.text)
        
    if not responed_data['status'] :
        print 'test_get_real_time_deal_record() responed_data Error'
                                           
        return test_case_result(False)
    
    print 'test_get_real_time_deal_record() responed_data data',len(responed_data['data'])
    
    if len(responed_data['data']) :                                           
        return test_case_result(True)
    
    return test_case_result(False)

def test_get_depth() :
    responed = requests.get('http://127.0.0.1:8088/router?router=get_depth',data = {
        'coin' : 'BTC/USDT'
    })
    responed_data = json.loads(responed.text)
        
    if not responed_data['status'] :
        print 'test_get_depth() responed_data Error'
                                           
        return test_case_result(False)
    
    print 'test_get_depth() responed_data data',len(responed_data['data'])
    
    if len(responed_data['data']['bid']) and len(responed_data['data']['ask']) :                                           
        return test_case_result(True)
    
    return test_case_result(False)
    
    


#print test_case_check_exist_name()
#print test_case_make_valid_code()
#print test_case_regeist_user()
login_result = test_case_login('18814114124','123456')
print login_result
print test_case_get_user_coin(login_result.get_data())
#print test_case_logout(login_result.get_data())
#print test_get_increase_rank()
#print test_get_real_time_deal_record()
#print test_get_depth()



