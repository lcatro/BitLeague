
URL : http://127.0.0.1:8088/router?router=方法


#### 检查用户名是否存在

router=check_exist_name

POST 请求,参数

user  字符串,用户名

JSON返回值

{ 'status' : result , 'data' : '' , 'description' : '' }


#### 生成邮件验证码

router=make_valid_code

POST 请求,参数

user  字符串,用户名

JSON返回值

{ 'status' : result , 'data' : '' , 'description' : '' }


#### 注册用户

router=regeist_user

POST 请求,参数

user  字符串,用户名
pass  字符串,密码
valid_code  字符串,验证码

JSON返回值

{ 'status' : result , 'data' : '' , 'description' : '' }


#### 登陆用户

router=login

POST 请求,参数

user  字符串,用户名
pass  字符串,密码

JSON返回值

{ 'status' : result , 'data' : '' , 'description' : '' }
Cookie Session


#### 退出用户

router=logout

POST 请求,无参数,依赖session

无返回值


#### 获取用户余额

router=get_user_coin

POST 请求,无参数,依赖session

JSON返回值

{ 'status' : result , 'data' : '' , 'description' : '' }


#### 获取排行榜

router=get_rank

GET 请求,无参数

JSON返回值

{ 'status' : result , 'data' : '' , 'description' : '' }


#### 获取交易对信息

router=get_coin

GET 请求,参数

pair  字符串,交易对名称

JSON返回值

{ 'status' : result , 'data' : ['交易对名字','当前价格','24小时成交数量','涨跌幅','当天开盘价'] , 'description' : '' }


#### 获取当前成交记录

router=get_deal_record

GET 请求,参数

pair  字符串,交易对名称

JSON返回值

{ 'status' : result , 'data' : '' , 'description' : '' }


#### 获取深度数据

router=get_depth

GET 请求,参数

pair  字符串,交易对名称

JSON返回值

{ 'status' : result , 'data' : '' , 'description' : '' }


#### 获取简易行情

router=get_simple_k_line

GET 请求,参数

pair  字符串,交易对名称

JSON返回值

{ 'status' : result , 'data' : '' , 'description' : '' }


#### 获取行情数据

router=get_coin_k_line

GET 请求,参数

pair  字符串,交易对名称
interval  字符串,K 线时间间隔,取值:1min,5min,30min,4h,1d .值可以为空,为空时默认为1min

JSON返回值

{ 'status' : result , 'data' : '' , 'description' : '' }


#### 购买接口

router=buy

POST 请求,有参数,依赖session

pair    字符串,交易对名称
amount  浮点数字,购买数量
price   浮点数字,购买价格

JSON返回值

{ 'status' : result , 'data' : '' , 'description' : '' }


#### 卖出接口

router=sell

POST 请求,有参数,依赖session

pair    字符串,交易对名称
amount  浮点数字,购买数量
price   浮点数字,购买价格

JSON返回值

{ 'status' : result , 'data' : '' , 'description' : '' }


#### 用户提现

router=withdraw

POST 请求,有参数,依赖session

coin  字符串,提现币的名称

JSON返回值

{ 'status' : result , 'data' : '' , 'description' : '' }


#### 获取用户提现地址

router=get_withdraw_address

POST 请求,有参数,依赖session

coin  字符串,获取提现地址的币名称

JSON返回值

{ 'status' : result , 'data' : '' , 'description' : '' }


#### 设置用户提现地址

router=set_withdraw_address

POST 请求,有参数,依赖session

coin  字符串,获取提现地址的币名称
address  字符串,钱包地址

JSON返回值

{ 'status' : result , 'data' : '' , 'description' : '' }


