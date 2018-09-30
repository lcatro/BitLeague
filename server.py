
import hashlib
import os
import random
import time

import tornado.ioloop
import tornado.web
from tornado.web import StaticFileHandler

import base_library
import captcha
import configure
import exchange_data_update
import market_manager
import user_manager
import server_data


def argument_filter(tornado_argument) :
    replace_list = ['\'','"','<','>','?','#','|','(',')',';','&']
    
    if dict == type(tornado_argument) :
        for argument_index in tornado_argument.keys() :
            data = tornado_argument[argument_index]
            
            for value_index in range(len(data)) :
                value_data = data[value_index]
            
                for replace_index in replace_list :
                    value_data = value_data.replace(replace_index,'')
                    
                data[value_index] = value_data
                
            tornado_argument[argument_index] = data
    elif list == type(tornado_argument) :
        for argument_index in range(len(tornado_argument)) :
            data = tornado_argument[argument_index]
                    
            for value_index in range(len(data)) :
                value_data = data[value_index]
            
                for replace_index in replace_list :
                    value_data = value_data.replace(replace_index,'')
                    
                data[value_index] = value_data
                
            tornado_argument[argument_index] = data

            
class session :
    
    SESSION_NAME = 'session'
    
    def __init__(self) :
        self.session = {}
        self.session_expire_time = 24 * 60 * 60 * 1000
        self.session_internal_key_word = ['__interal_create_time']
        
    def sha256(self,data) :
        sha256 = hashlib.sha256()
        
        sha256.update(data)
        sha256.update(sha256.digest())
        
        return sha256.hexdigest()
        
    def is_exist_session(self,session_code) :
        if self.session.has_key(session_code) :
            return True
        
        return False
    
    def is_expire_session(self,session_code) :
        if not self.is_exist_session(session_code) :
            return False
        
        if base_library.get_time_tick() > self.session[session_code]['__interal_create_time'] + self.session_expire_time :
            return True
        
        return False
        
    def make_new_session(self) :
        while True :
            session_id = self.sha256('%s%s' % (str(base_library.get_time_tick()),random.randint(0,10000)))
            
            if self.is_exist_session(session_id) :
                continue
            
            self.session[session_id] = {
                '__interal_create_time' : base_library.get_time_tick()
            }
            
            return session_id
            
    def delete_session(self,session_code) :
        if self.is_exist_session(session_code) :
            self.session.pop(session_code)
            
    def get_session_data(self,session_code,key_name) :
        if self.is_expire_session(session_code) :
            self.delete_session(session_code)
            
            return None
        
        if key_name in self.session_internal_key_word :
            return None
        
        if not self.session[session_code].has_key(key_name) :
            return None
            
        return self.session[session_code][key_name]
            
    def set_session_data(self,session_code,key_name,value) :
        if self.is_expire_session(session_code) :
            self.delete_session(session_code)
            
            return None
        
        if key_name in self.session_internal_key_word :
            return None
        
        self.session[session_code][key_name] = value
        
        return True
        
    def delete_session_data(self,session_code,key_name) :
        if self.is_expire_session(session_code) :
            self.delete_session(session_code)
            
            return None
        
        if key_name in self.session_internal_key_word :
            return None
        
        if not self.session[session_code].has_key(key_name) :
            return None
            
        self.session[session_code].pop(key_name)
        
        return True

class root_handler(tornado.web.RequestHandler) :
    
    def get(self) :
        self.write('BE Root Dir ..')

class router_handler(tornado.web.RequestHandler) :
    
    def get(self) :
        argument_filter(self.request.query_arguments)
        
        router = self.get_argument('router')
        
        if not router :
            self.write('No Router ..')
        
        if router in global_router['GET'] :
            router_function = global_router['GET'][router]
            
            api_status = router_function(self)
        elif global_router['GET'].has_key('*') :
            router_function = global_router['GET']['*']
            
            api_status = router_function(self)
            
        self.set_header('Access-Control-Allow-Origin','*')
        self.write(str(api_status))
    
    def post(self) :
        argument_filter(self.request.query_arguments)
        
        router = self.get_argument('router')
        
        if not router :
            self.write('No Router ..')
            
        if router in global_router['POST'] :
            router_function = global_router['POST'][router]
            
            api_status = router_function(self)
        elif global_router['POST'].has_key('*') :
            router_function = global_router['POST']['*']
            
            api_status = router_function(self)
            
        self.set_header('Access-Control-Allow-Origin','*')
        self.write(str(api_status))
            
class internal_router_logic :
    
    @staticmethod
    def unsupport_api(tornado_object) :
        return server_data.server_api_result(True,'UnSupport Handler ..')

    # POST
    
    @staticmethod
    def check_exist_name(tornado_object) :
        user_name = tornado_object.get_argument('user')
        
        if not user_name :
            return server_data.server_api_result(False,'Not Found User')
        
        return user_manager.is_active_user(user_name)

    @staticmethod
    def make_valid_code(tornado_object) :
        user_name = tornado_object.get_argument('user')

        if not user_name :
            return server_data.server_api_result(False,'Not Found User')
        
        valid_code = user_manager.make_new_user(user_name)
        
        #  valid_code will send to browser for debug , remember delete it ..
        
        return server_data.server_api_result(True,data = valid_code)
    
    @staticmethod
    def regeist_user(tornado_object) :
        user_name = tornado_object.get_argument('user')
        password = tornado_object.get_argument('pass')
        valid_code = tornado_object.get_argument('valid_code')

        if not user_name or not password or not valid_code :
            return server_data.server_api_result(False,'Lost Argument')
        
        return user_manager.regedit_new_user(user_name,password,valid_code)
    
    @staticmethod
    def login(tornado_object) :
        user_name = tornado_object.get_argument('user')
        password = tornado_object.get_argument('pass')
        tick_id = tornado_object.get_argument('tick')
        valid_result = captcha.check_tick(tick_id)
        
        if not tick_id.get_status() :
            return valid_result
        
        if not user_name or not password :
            return server_data.server_api_result(False,'Lost Argument')
        
        status = user_manager.login(user_name,password)
        
        if status.get_status() :
            if session.SESSION_NAME in tornado_object.request.arguments.keys() :
                old_session_id = tornado_object.get_argument(session.SESSION_NAME)
                #old_session_id = tornado_object.get_cookie(session.SESSION_NAME)

                if old_session_id :
                    global_session.delete_session(old_session_id)
            
            new_session_id = global_session.make_new_session()
            uid = user_manager.get_uid_by_user_name(user_name).get_data()
        
            global_session.set_session_data(new_session_id,'uid',uid)
            #tornado_object.set_cookie(session.SESSION_NAME,new_session_id)
            
            return server_data.server_api_result(True,data = new_session_id)
        
        return status
    
    @staticmethod
    def logout(tornado_object) :
        session_id = tornado_object.get_argument(session.SESSION_NAME)
        #session_id = tornado_object.get_cookie(session.SESSION_NAME)
        
        if not session_id :
            return server_data.server_api_result(False)
        
        global_session.delete_session(session_id)
        #tornado_object.set_cookie(session.SESSION_NAME,'')
        
        return server_data.server_api_result(True)
        
    @staticmethod
    def get_user_coin(tornado_object) :
        session_id = tornado_object.get_argument(session.SESSION_NAME)
        #session_id = tornado_object.get_cookie(session.SESSION_NAME)
        
        if not session_id :
            return server_data.server_api_result(False,'Plaese Login')
        
        uid = global_session.get_session_data(session_id,'uid')
        
        if not uid :
            return server_data.server_api_result(False,'Invalid uid')
        
        status = user_manager.get_user_coin(uid)
        
        if status.get_status() :
            return server_data.server_api_result(True,data = status.get_description())
        
        return server_data.server_api_result(False,status.get_description())
    
    @staticmethod
    def buy(tornado_object) :
        session_id = tornado_object.get_argument(session.SESSION_NAME)
        #session_id = tornado_object.get_cookie(session.SESSION_NAME)
        
        if not session_id :
            return server_data.server_api_result(False,'Plaese Login')
        
        uid = global_session.get_session_data(session_id,'uid')
        
        if not uid :
            return server_data.server_api_result(False,'Invalid uid')
        
        try :
            pair_name = tornado_object.get_argument('pair')
            amount = float(tornado_object.get_argument('amount'))
            price = float(tornado_object.get_argument('price'))
        except :
            return server_data.server_api_result(False,'Invalid Argument')
        
        return market_manager.order_buy(uid,pair_name,amount,price)
    
    @staticmethod
    def sell(tornado_object) :
        session_id = tornado_object.get_argument(session.SESSION_NAME)
        #session_id = tornado_object.get_cookie(session.SESSION_NAME)
        
        if not session_id :
            return server_data.server_api_result(False,'Plaese Login')
        
        uid = global_session.get_session_data(session_id,'uid')
        
        if not uid :
            return server_data.server_api_result(False,'Invalid uid')
        
        try :
            pair_name = tornado_object.get_argument('pair')
            amount = float(tornado_object.get_argument('amount'))
            price = float(tornado_object.get_argument('price'))
        except :
            return server_data.server_api_result(False,'Invalid Argument')
        
        return market_manager.order_sell(uid,pair_name,amount,price)
    
    @staticmethod
    def withdraw(tornado_object) :
        session_id = tornado_object.get_argument(session.SESSION_NAME)
        #session_id = tornado_object.get_cookie(session.SESSION_NAME)
        
        if not session_id :
            return server_data.server_api_result(False,'Plaese Login')
        
        uid = global_session.get_session_data(session_id,'uid')
        
        if not uid :
            return server_data.server_api_result(False,'Invalid uid')
        
        try :
            coin = tornado_object.get_argument('coin')
            amount = float(tornado_object.get_argument('amount'))
        except :
            return server_data.server_api_result(False,'Invalid Argument')
    
        return market_manager.withdraw(uid,coin,amount)
    
    @staticmethod
    def set_withdraw_address(tornado_object) :
        session_id = tornado_object.get_argument(session.SESSION_NAME)
        #session_id = tornado_object.get_cookie(session.SESSION_NAME)
        
        if not session_id :
            return server_data.server_api_result(False,'Plaese Login')
        
        uid = global_session.get_session_data(session_id,'uid')
        
        if not uid :
            return server_data.server_api_result(False,'Invalid uid')
        
        try :
            coin = tornado_object.get_argument('coin')
            address = tornado_object.get_argument('address')
        except :
            return server_data.server_api_result(False,'Invalid Argument')
    
        return user_manager.set_user_withdraw_address(uid,coin,address)
    
    @staticmethod
    def get_withdraw_address(tornado_object) :
        session_id = tornado_object.get_argument(session.SESSION_NAME)
        #session_id = tornado_object.get_cookie(session.SESSION_NAME)
        
        if not session_id :
            return server_data.server_api_result(False,'Plaese Login')
        
        uid = global_session.get_session_data(session_id,'uid')
        
        if not uid :
            return server_data.server_api_result(False,'Invalid uid')
        
        try :
            coin = tornado_object.get_argument('coin')
        except :
            return server_data.server_api_result(False,'Invalid Argument')
    
        return user_manager.get_user_withdraw_address(uid,coin)
    
    #  GET
    
    @staticmethod
    def get_rank(tornado_object) :
        return market_manager.get_rank()
    
    @staticmethod
    def get_coin(tornado_object) :
        pair_name = tornado_object.get_argument('pair')
        
        if not pair_name :
            return server_data.server_api_result(False,'Lost Argument')
        
        return market_manager.get_coin_info(pair_name)
    
    @staticmethod
    def get_coin_simple_k_line(tornado_object) :
        pair_name = tornado_object.get_argument('pair')
        
        if not pair_name :
            return server_data.server_api_result(False,'Lost Argument')
        
        return market_manager.get_simple_k_line(pair_name)
        
    @staticmethod
    def get_coin_k_line(tornado_object) :
        pair_name = tornado_object.get_argument('pair')
        time_interval = tornado_object.get_argument('interval')
        
        if not time_interval :
            time_interval = '1min'
        
        if not pair_name :
            return server_data.server_api_result(False,'Lost Argument')
        
        return market_manager.get_k_line(pair_name,time_interval)
    
    @staticmethod
    def get_deal_record(tornado_object) :
        pair_name = tornado_object.get_argument('pair')
        
        if not pair_name :
            return server_data.server_api_result(False,'Lost Argument')
        
        return market_manager.get_real_time_deal_record(pair_name)
    
    @staticmethod
    def get_depth(tornado_object) :
        pair_name = tornado_object.get_argument('pair')
        
        if not pair_name :
            return server_data.server_api_result(False,'Lost Argument')
        
        return market_manager.get_depth(pair_name)
    
    

global_session = session()
global_router = {
    'GET' : {
        'get_rank' : internal_router_logic.get_rank ,
        'get_coin' : internal_router_logic.get_coin ,
        'get_simple_k_line' : internal_router_logic.get_coin_simple_k_line ,
        'get_coin_k_line' : internal_router_logic.get_coin_k_line ,
        'get_deal_record' : internal_router_logic.get_deal_record ,
        'get_depth' : internal_router_logic.get_depth ,
        '*' : internal_router_logic.unsupport_api ,
    } ,
    'POST' : {
        'check_exist_name' : internal_router_logic.check_exist_name ,
        'make_valid_code' : internal_router_logic.make_valid_code ,
        'regeist_user' : internal_router_logic.regeist_user ,
        'login' : internal_router_logic.login ,
        'logout' : internal_router_logic.logout ,
        'get_user_coin' : internal_router_logic.get_user_coin ,
        'buy' : internal_router_logic.buy ,
        'sell' : internal_router_logic.sell ,
        'withdraw' : internal_router_logic.withdraw ,
        'set_withdraw_address' : internal_router_logic.set_withdraw_address ,
        'get_withdraw_address' : internal_router_logic.get_withdraw_address ,
        '*' : internal_router_logic.unsupport_api ,
    }
}

        

if __name__ == '__main__' :
    exchange_data_update.background_update()
    
    print 'Background Threads is Booting ..'
    
    app = tornado.web.Application([
        (r'/' , root_handler),     #  base logic
        (r'/router' , router_handler),
        (r'/html/(.*)' , StaticFileHandler , {
            'path' : os.path.join(os.getcwd() + '/html')
        }),
        ('/get_captcha',captcha.get_captcha_handle) ,  #  captcha logic
        ('/valid_captcha',captcha.valid_captcha_handle) ,
        ('/captcha/(.*)',tornado.web.StaticFileHandler,{
            'path' : os.path.join(os.getcwd() + '/captcha')
        }) ,
        ('/captcha_picture/(.*)',tornado.web.StaticFileHandler,{
            'path' : os.path.join(os.getcwd() + '/captcha_picture')
        })
    ])
    
    print 'Server.py Start'
    
    app.listen(configure.server_configure['port'])
    tornado.ioloop.IOLoop.current().start()


