#!/usr/local/bin/python3
'''
Market Data Endpoints
'''

import re
import sys
import time
import requests
import urllib
import json
import argparse
from utils import precision, freeCoin

global usleep
usleep = lambda x: time.sleep(x/1000000.0)


def buyMarket():
    timeStamp = int(time.time()*1000)
    free = freeCoin('USDT')
    #print(free)
    #exfee = free - (free*fee)
    queryObj = {
            "symbol": "BTCUSDT",
            "recvWindow": 5000,
            "side": "BUY", "type": "MARKET",
            "quoteOrderQty": free,
            "timestamp": timeStamp
            }
    queryString = urllib.parse.urlencode(queryObj, doseq=False)
    #print(str(queryString))
    signature = hmac.new(bytes(secretKey, 'latin-1'), msg=bytes(queryString, 'latin-1'), digestmod=hashlib.sha256).hexdigest()
    #print(signature)
    apiPath = "/order"
    #print(apiPath)
    url="https://api3.binance.com/api/v3{0}".format(apiPath)
    #print(url)
    headers = {'User-Agent': 'API', 'X-MBX-APIKEY': apiKey}
    #print(headers)
    data = "{0}&signature={1}".format(queryString, signature)
    print(data)
    r = requests.post(url, headers=headers, data=data, allow_redirects=True)
    #print(r.content)
    print(json.dumps(json.loads(r.content), indent = 3))

def sellMarket():
    timeStamp = int(time.time()*1000)
    free = freeCoin('BTC')
    queryObj = {
            "symbol": "BTCUSDT",
            "recvWindow": 5000,
            "side": "SELL", "type": "MARKET",
            "quantity": free,
            "timestamp": timeStamp
            }
    #queryString = "symbol=BTCUSDT&recvWindow=5000&timestamp={0}".format(timeStamp)
    queryString = urllib.parse.urlencode(queryObj, doseq=False)
    print(str(queryString))
    signature = hmac.new(bytes(secretKey, 'latin-1'), msg=bytes(queryString, 'latin-1'), digestmod=hashlib.sha256).hexdigest()
    print(signature)
    apiPath = "/order"
    print(apiPath)
    url="https://api3.binance.com/api/v3{0}".format(apiPath)
    print(url)

    headers = {'User-Agent': 'API', 'X-MBX-APIKEY': apiKey}
    print(headers)
    data = "{0}&signature={1}".format(queryString, signature)
    print(data)
    r = requests.post(url, headers=headers, data=data, allow_redirects=True)
    #print(r.content)
    print(json.dumps(json.loads(r.content), indent = 3))

def sellLimit():
    timeStamp = int(time.time()*1000)
    #print(freeCoin('BTC'))
    queryObj = {
            "symbol": "BTCUSDT",
            "recvWindow": 5000, "timeInForce": "GTC",
            "side": "SELL", "type": "LIMIT",
            #"quantity": 0.000363,
            "quantity": freeCoin('BTC'),
            "price": 39280.0, # decimal required
            "timestamp": timeStamp
            }
    #queryString = "symbol=BTCUSDT&recvWindow=5000&timestamp={0}".format(timeStamp)
    queryString = urllib.parse.urlencode(queryObj, doseq=False)
    print(str(queryString))
    signature = hmac.new(bytes(secretKey, 'latin-1'), msg=bytes(queryString, 'latin-1'), digestmod=hashlib.sha256).hexdigest()
    print(signature)
    apiPath = "/order"
    print(apiPath)
    url="https://api3.binance.com/api/v3{0}".format(apiPath)
    print(url)

    headers = {'User-Agent': 'API', 'X-MBX-APIKEY': apiKey}
    print(headers)
    data = "{0}&signature={1}".format(queryString, signature)
    print(data)
    r = requests.post(url, headers=headers, data=data, allow_redirects=True)
    #print(r.content)
    print(json.dumps(json.loads(r.content), indent = 3))

def queryOrder():
    #apiPath = "/exchangeInfo"
    #apiPath = "/ping"
    #apiPath = "/time"
    timeStamp = int(time.time()*1000)
    #timeStamp = 1612674785213
    #print(timeStamp)
    queryObj = {
            "symbol": "BTCUSDT",
            "recvWindow": 5000,
            "timestamp": timeStamp
            }
    #queryString = "symbol=BTCUSDT&recvWindow=5000&timestamp={0}".format(timeStamp)
    queryString = urllib.parse.urlencode(queryObj, doseq=False)
    print(queryString)
    apiPath = "/order?{0}".format(queryString)
    print(apiPath)
    signature = hmac.new(secretKey, queryString, hashlib.sha256).hexdigest()
    print(signature)
    #headers = {'User-Agent': 'Mozilla/5.0', 'X-MBX-APIKEY': apiKey}
    ##headers = {'User-Agent': 'Mozilla/5.0'}
    #print(headers)
    url="https://api3.binance.com/api/v3{0}".format(apiPath)
    print(url)
    #response=requests.get(url, headers=headers)
    #r=json.loads(response.content.split("\n")[0])
    #print(r)
    ##print("serverTime: %s" % r["serverTime"])

def getBinancePrice(pair):
    #timeStamp = int(time.time()*1000)
    queryObj = {
            "symbol": "BNBUSDT",
            "limit": 5
            }
    queryString = urllib.parse.urlencode(queryObj, doseq=False)
    apiPath = "/depth?{0}".format(queryString)
    #print(queryString)
    ##apiPath = "/order?{0}".format(queryString)
    #print(apiPath)
    #signature = hmac.new(secretKey, queryString, hashlib.sha256).hexdigest()
    #print(signature)
    #headers = {'User-Agent': 'Mozilla/5.0', 'X-MBX-APIKEY': apiKey}
    headers = {'User-Agent': 'Mozilla/5.0'}

    #print(headers)
    url="https://api3.binance.com/api/v3{0}".format(apiPath)
    print(url)
    response = requests.get(url, headers=headers)
    #
    #print(json.dumps(json.loads(response.content), indent = 3))
    r = json.loads(response.content)
    print(r['bids'])
    for bid in enumerate(r['bids']):
        print(bid)

    #r=json.loads(response.content.split("\n")[0])
    #print(r)
    ##print("serverTime: %s" % r["serverTime"])

    return True

if __name__ == '__main__':
    # nonce=int(datetime.strptime(str(datetime.now()), '%Y-%m-%d %H:%M:%S.%f').strftime("%s"))

    '''
    get BNB price from binance
    avarage price from 10-20 orders
    and return in THB device by THB price bath api from BOT
    https://www.bot.or.th/thai/financialmarkets/_layouts/application/exchangerate/exchangerate.aspx
    '''
    binancePrice = getBinancePrice('BNB/USD') # return price in USD

    #bitkubPrice = getBitkubPrice('BNB/THB')

    i=0
    if True:
        free = precision(freeCoin('BUSD'))
        print("\n{0}.checking remaining: {1}".format(i, free))
        if free == 0.0:
            print("do buying")
            #buyMarket()
        else:
            print("do selling")
            #sellMarket()
        time.sleep(2)

    #i=0
    #while True:
    #    freeBTC = precision(freeCoin('BTC'))
    #    print("\n{0}.checking remaining BTC: {1}".format(i, freeBTC))
    #    if freeBTC == 0.0:
    #        print("do buying")
    #        #buyMarket()
    #    else:
    #        print("do selling")
    #        #sellMarket()
    #    time.sleep(1)

