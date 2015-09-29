__author__ = 'richard abrahams'


import requests
import json
import base64
import hmac
import hashlib
import time

def create_tonce():
    tonce = int(time.time() * 1000000)
    return tonce

# STRING access_key NEEDS TO BE YOUR ACCESS KEY

def create_access_key():
    access_key = 'YOUR ACCESS KEY HERE'
    return access_key

# STRING secret_key NEEDS TO BE YOUR SECRET KEY

def create_secret_key():
    secret_key = 'YOUR SECRET KEY HERE'
    return secret_key

def create_requestmethod():
    request_method = 'post'
    return  request_method

def create_method(query_method):
    method = query_method
    return method

def create_params(query_params):
    param_len = len(query_params)
    param_string ='&params='
    param_count = 1
    for i in query_params:
        if i != None:
            if param_count < param_len:
                i = str(i)
                param_string = param_string+i+','
            else:
                i = str(i)
                param_string = param_string+i
            param_count +=1
        if i == None:
                param_string = param_string+','
        param_count +=1
    return param_string

def create_payload_params(query_params):
    param_payload = []
    for i in query_params:
            param_payload.append(i)
    return (param_payload)

def hash_string(auth_string, secret_key):
    hashed_string = hmac.new(secret_key.encode(), auth_string.encode(), hashlib.sha1).hexdigest()
    return hashed_string

def build_auth_header(hashed_string, captured_tonce):
    headerbytes = create_access_key() + ':' +hashed_string
    headerbytes = headerbytes.encode()
    headerbytes = base64.b64encode(headerbytes)
    headerbytes = str(headerbytes)
    headerbytes = 'Basic '+headerbytes[2:-1]
    headers={'Authorization':headerbytes,'Json-Rpc-Tonce':int(captured_tonce)}
    return headers

def makepayload(captured_tonce, query_method, param_payload):
    payload = {'accesskey': create_access_key(), 'id': int(captured_tonce), 'requestmethod': 'post', 'tonce': int(captured_tonce), 'params':param_payload,
               'method': query_method}
    return payload

def makecall(payload, headers):
    url = 'https://api.btcc.com/api_trade_v1.php'
    r = requests.post(url, json.dumps(payload), headers=headers)
    return r

def start_query(query_method, query_params):
    captured_tonce = str(create_tonce())
    tonce = 'tonce=' + captured_tonce
    access_key = '&accesskey=' + create_access_key()
    request_method = '&requestmethod=' + create_requestmethod()
    ident = '&id=' + captured_tonce
    method = '&method=' + query_method
    params = create_params(query_params)
    param_payload = create_payload_params(query_params)
    secret_key = create_secret_key()
    auth_string = tonce+access_key+request_method+ident+method+params
    hashed_string = hash_string(auth_string, secret_key)
    headers = build_auth_header(hashed_string, captured_tonce)
    payload = makepayload(captured_tonce, query_method, param_payload)
    result = makecall(payload, headers)
    return result

def get_balances():
    query_method ='getAccountInfo'
    query_params = ['balance']
    r = error_shield(query_method, query_params)
    result = r.json().get('result')
    currency = (result['balance']['cny']['amount'])
    btc = (result['balance']['btc']['amount'])
    return [currency, btc]


def get_orders():
    query_method ='getOrders'
    query_params = []
    r = error_shield(query_method, query_params)
    result = r.json().get('result')
    order_list = []
    try:
        order_type = (result['order'][0]['type'])
        order_amount = (float(result['order'][0]['amount']))
        order_price = (float(result['order'][0]['price']))
        order_id = (result['order'][0]['id'])
        order_list = [order_type, order_amount, order_price, order_id]
    except:
        pass
    return order_list

def get_sell(query_params):

    query_method ='sellOrder2'
    r = error_shield(query_method, query_params)
    result = r.json().get('result')
    return result

def get_buy(query_params):
    query_method ='buyOrder2'
    r = error_shield(query_method, query_params)
    result = r.json().get('result')
    return result

def get_cancel(query_params):
    query_method ='cancelOrder'
    r = error_shield(query_method, query_params)
    result = r.json().get('result')
    return result

def get_stop(query_params):
    query_method ='buyStopOrder'
    r = error_shield(query_method, query_params)
    result = r.json().get('result')
    return result

def get_transactions(query_params):
    query_method ='getTransactions'
    r = error_shield(query_method, query_params)
    result = r.json().get('result')
    trans_type = (result['transaction'][0]['type'])
    transaction_list = [trans_type]
    return transaction_list

def get_market_depth():
    query_method ='getMarketDepth2'
    query_params = [10]
    r = error_shield(query_method, query_params)
    result = r.json().get('result')
    return result

def error_shield(query_method, query_params):
    r = start_query(query_method, query_params)
    counter = 0
    while r.status_code != 200:
        print('Comm error, retrying')
        print('Status code:', r.status_code)
        print('headers:\n', r.headers)
        print('request headers:\n', r.request.headers)
        print(r.text)
        time.sleep(5)
        r = start_query(query_method, query_params)
        counter += 1
        if counter == 5:
            print('Comms failed')
            break
    return r


