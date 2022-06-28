import sys, time, os
import json
import hmac
import hashlib
import logging
import math
import requests
import urllib
import codecs
from datetime import datetime
from environs import Env
from termcolor import colored
import pyotp

from useragent import Agent
from screen import drawLine, clearLine

env = Env()
env.read_env()


def binanceWd(coin, q):
    store = q.get()
    last = 0
    if store is not None:
        if store['binanceWithdraw'] is not None:
            tf ='%Y-%m-%d %H:%M:%S'
            for a in store['binanceWithdraw']:
                if a['coin'] == coin:
                    d = a['applyTime']
                    #d.strftime(tf)
                    #d.strftime("%%s")
                    x = time.mktime(time.strptime(str(d), tf))
                    last = int(x)
                    break
    q.put(store)
    return last

def k2faCalc(q):
    store = q.get()
    if store is not None:
        totp = pyotp.TOTP('')
        store['k2fa'] = totp.now()
    q.put(store)

def quoteAssets(symbols, fCoins, quote):
    matches = []
    for sym in symbols:
        if sym['status'] == "TRADING":
            if sym['baseAsset'].upper() in fCoins:
                if sym['quoteAsset'].upper() == quote:
                    matches.append(sym)

            if sym['quoteAsset'].upper() in fCoins:
                if sym['baseAsset'].upper() == quote:
                    matches.append(sym)

    return matches

class bcolors:
    #BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    #BLUE = '\033[34m'
    #BLUE = '\033[44;1;31m'
    #BLUE = '\033[44;1;37m'
    BLUE = '\033[36;0;44m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    HEADER = '\033[95m'

    #BLUE = '\033[94m'
    #CYAN = '\033[96m'
    #GREEN = '\033[92m'
    #YELLOW = '\033[93m'

    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


def colors(text, colour):
    string = None
    if colour == 'BLUE':
        string = bcolors.BLUE + text + bcolors.ENDC
    elif colour == 'HEADER':
        string = bcolors.HEADER + text + bcolors.ENDC
    elif colour == 'RED':
        string = bcolors.RED + text + bcolors.ENDC
    elif colour == 'MAGENTA':
        string = bcolors.MAGENTA + text + bcolors.ENDC
    elif colour == 'CYAN':
        string = bcolors.CYAN + text + bcolors.ENDC
    elif colour == 'GREEN':
        string = bcolors.GREEN + text + bcolors.ENDC
    elif colour == 'YELLOW':
        string = bcolors.YELLOW + text + bcolors.ENDC
    elif colour == 'FAIL':
        string = bcolors.HEADER + text + bcolors.ENDC
    elif colour == 'BOLD':
        string = bcolors.BOLD + text + bcolors.ENDC
    elif colour == 'UNDERLINE':
        string = bcolors.UNDERLINE + text + bcolors.ENDC
    return string

def noScience(science):
    c = str(science).split("e")[1]
    d = abs(int(c))
    e = tf(science, 8)
    return e

def pink(text):
    return colored(text, 'yellow')

def red(text):
    return colored(text, 'red')

def green(text):
    return colored(text, 'green')

def tf(n, digits):
    n = float(int(n * 10**digits))
    n /=10**digits
    return n
    #return '{:f}'.format(n)

def f8(n):
    n = float(int(n * 100000000))
    n /=100000000
    return n

def f2(n):
    n = float(int(n * 100))
    n /=100
    return n

def findBid(array, minimum):
    bid = array[-1]
    #logging.info(bid)
    for x in array:
        #logging.info(float(list(x)[0]))
        #logging.info(tf(minimum, 2))
        if float(list(x)[1]) > tf(minimum, 2):
            bid = x
            #logging.info("found")
            #logging.info(bid)
            break

    #logging.info(bid)
    return bid

def calcFinal(buy, sell, digit):
    final = sell - buy
    #final = tf(final, digit)
    return final

def calcSell(coin, price, digit):
    sell = coin * price
    #sell = tf(sell, digit)
    return sell

def calcAfter(coin, fee, digit):
    after = coin - fee
    #after = tf(after, digit)
    return after

def calcMultiply(remain, price, digit):
    coin = remain * price
    #coin = tf(coin, digit)
    return coin

def calcDevide(remain, price, digit):
    coin = remain / price
    #coin = tf(coin, digit)
    return coin

def calcRemain(cost, fee, digit):
    remain = cost - fee
    #remain = tf(remain, digit)
    return remain

def calcFee(cost, feeRate, digit):
    fee = (feeRate/100) * cost
    #fee = tf(fee, digit)
    return fee

def calcAmount(obj, q):
    j = json.loads(obj)
    pair = j['pair'].lower()
    cost = j['cost']
    exchange = j['exchange']
    tradeFee = j['fee']

    store = q.get()
    calcd =  {
            "price": None,
            "amt": None
            }
    bids = "bids_%s" % pair
    asks = "asks_%s" % pair

    binanceBuyPosition = store['binanceBuyPosition']
    binanceSellPosition = store['binanceSellPosition']

    satangBuyPosition = store['satangBuyPosition']
    satangSellPosition = store['satangSellPosition']

    if store['pairDefinedBinance']:
        if store[bids] is not None:
            srcCoin = 0.00
            if len(store[bids]) == store['wsLimit']:
                srcFee = calcFee(cost, tradeFee, 8)
                srcRemain = calcRemain(cost, srcFee, 8)

                if exchange == "binance":
                    buyPrice = list(store[asks][binanceSellPosition])[0]
                    srcCoin = calcDevide(srcRemain, float(buyPrice), 8)
                    amt = calcLotSize(srcCoin, pair, q)

                if exchange == "satang":
                    if store['autoPosition']:
                        ssp = "satangSellPosition_%s" % pair.lower()
                        satangSellPosition = store[ssp]
                        thbMin = store['thbMin']
                        satangSellPosition = findPosition(satangSellPosition, store[asks], thbMin)
                        store[ssp] = satangSellPosition

                    buyPrice = list(store[asks][satangSellPosition])[0]
                    srcCoin = calcDevide(srcRemain, float(buyPrice), 8)
                    amt = calcBaseAssetPrecisionSatang(srcCoin, pair, q)
                calcd = {
                        "price": float(buyPrice),
                        "pair": pair,
                        "amt": amt
                        }
            #calcd = int(srcCoin) # avoid the lot_size remain coin

    q.put(store)
    return calcd

#def calcMargin(obj):
#    j = json.loads(obj)
#    coin = j['coin']
#    storeCoins = j['storeCoins']
#    buyTotal = float(j['buyTotal'])
#    buyPrice = float(j['buyPrice'])
#    buyAmount = float(j['buyAmount'])
#    sellPrice = float(j['sellPrice'])
#    src = j['src']
#    dst = j['dst']
#    busdTHB = float(j['busd_thb'])
#
#    margin = 0.00
#
#    srcFeeRate = 0.00
#    dstFeeRate = 0.00
#    srcWithdrawFee = 0.00
#    digit = {}
#    for x in storeCoins['names']:
#        if x['name'] == coin:
#            for  y in x['exchange']:
#                if  y['name'] == src:
#                    srcWithdrawFee = y['withdraw']['fee']
#                    srcFeeRate = y['trade']
#                    digit['buy_price'] = y['digit']['price']
#                    digit['buy_total'] = y['digit']['total']
#                    digit['buy_amount'] = y['digit']['amount']
#
#                if  y['name'] == dst:
#                    dstFeeRate = y['trade']
#                    digit['sell_price'] = y['digit']['price']
#                    digit['sell_total'] = y['digit']['total']
#                    digit['sell_amount'] = y['digit']['amount']
#
#
#    srcFee = calcFee(buyTotal, srcFeeRate, digit['buy_total'])
#    srcRemain = calcRemain(buyTotal, srcFee, digit['buy_price'])
#    srcCoin = calcCoin(srcRemain, buyPrice, 8)
#    srcCoinAfter = calcAfter(srcCoin, srcWithdrawFee, 8)
#
#    #log = "--\n buy price: %s\n buy amount: %s\n remain: %s\n coin: %s" % (buyPrice, buyAmount, srcRemain, srcCoinAfter)
#    #logging.info(log)
#
#    dstGet = calcSell(srcCoinAfter, sellPrice, digit['sell_price'])
#    dstFee = calcFee(dstGet, dstFeeRate, 8)
#    dstRemain = calcRemain(dstGet, dstFee, digit['sell_total'])
#    #log = "--\n sell price: %s\n dst get: %s\n dst remain: %s\n" % (sellPrice, dstGet, dstRemain)
#    #logging.info(log)
#    if src == "satang" and dst == "binance":
#        margin = calcFinal(buyTotal, (dstRemain * busdTHB), 2)
#    if src == "binance" and dst == "satang":
#        totalTHB = busdTHB * buyTotal
#        totalTHB = tf(totalTHB, digit['sell_total'])
#        #log = "%s %s %s" % (buyTotal, totalTHB, dstRemain)
#        #logging.info(log)
#        #diff = dstRemain - totalTHB
#        #logging.info(diff)
#        margin = calcFinal(totalTHB, dstRemain, 2)
#    return margin

#def binanceNetwork(coin, network, q):
#    store = q.get()
#    obj = None
#    if store is not None:
#        timeStamp = int(time.time()*1000)
#        queryObj = {
#                "recvWindow": 5000,
#                "timestamp": timeStamp
#                }
#        #logging.info(store['keyBinance'])
#        apiKey = store['keyBinance']['key']
#        secretKey = store['keyBinance']['secret']
#        queryString = urllib.parse.urlencode(queryObj, doseq=False)
#        signature = getSignature(secretKey, queryString)
#        apiPath = "sapi/v1/capital/config/getall?{0}".format(queryString)
#        url="https://api3.binance.com/{0}&signature={1}".format(apiPath, signature)
#        headers = {'User-Agent': 'API', 'X-MBX-APIKEY': apiKey}
#        if not store['netBinance']:
#            store['netBinance'] = True
#            try:
#                response=requests.get(url, headers=headers)
#                logging.info("calling binance network")
#                if response.status_code == 200:
#                    r=json.loads(response.content)
#                    #print(json.dumps(v, indent = 3))
#                    #timeStamp = datetime.today().strftime("%B,%d %H:%M:%S")
#                    timeStamp = int(time.time()*1000)
#                    for v in r:
#                        if v['coin'] == coin:
#                            if len(v['networkList']) > 0:
#                                for n in v['networkList']:
#                                    if n['network'] == network:
#                                        obj = {
#                                                "fee": n['withdrawFee'],
#                                                "min": n['withdrawMin'],
#                                                "deposit": n['depositEnable'],
#                                                "withdraw": n['withdrawEnable'],
#                                                "timeStamp": timeStamp
#                                                }
#                                        break
#                else:
#                    responseHandler(response)
#            except:
#                logging.info("connection reset binanceNetWork")
#                pass
#            finally:
#                store['netBinance'] = False
#        else:
#            logging.info("already called waiting...")
#
#    q.put(store)
#    #logging.info(obj)
#    return obj

def satangNetwork(q):
    store = q.get()
    if store is not None:
        url="https://satangcorp.com/api/configs/web/"
        headers = {'User-Agent': Agent('brave')}
        try:
            response=requests.get(url, headers=headers)
            #logging.info("calling satang network")
            if response.status_code == 200:
                r=json.loads(response.content)
                #logging.info(json.dumps(r, indent = 3))
                #timeStamp = datetime.today().strftime("%B,%d %H:%M:%S")
                timeStamp = int(time.time()*1000)
                coins = store['coins']
                ##sameNetwork = ["satang","binance"]
                for c in coins:
                    for v in r['networks']['networks']:
                        if v == c['name'].lower():
                            for x in c['exchange']:
                                if x['name'] == "satang":
                                    for n in r['networks']['networks'][v]:
                                        if n == c['network'].lower():
                                            #logging.info(r['networks']['networks'][v][n]['withdrawEnable'])
                                            obj = {
                                                    "fee": r['networks']['networks'][v][n]['withdrawFee'],
                                                    "min": r['networks']['networks'][v][n]['withdrawMin'],
                                                    "deposit": r['networks']['networks'][v][n]['depositEnable'],
                                                    "withdraw": r['networks']['networks'][v][n]['withdrawEnable'],
                                                    "timeStamp": timeStamp
                                                    }
                                            trans = "fee_%s_%s" % (c['name'], x['name'])
                                            store[trans] = obj
                            break
            else:
                responseHandler(response)
        except:
            logging.info("connection reset satangNetWork")
            pass

    q.put(store)
    return

def binanceNetwork(q):
    store = q.get()
    if store is not None:
        timeStamp = int(time.time()*1000)
        queryObj = {
                "recvWindow": 5000,
                "timestamp": timeStamp
                }
        #logging.info(store['keyBinance'])
        apiKey = store['keyBinance']['key']
        secretKey = store['keyBinance']['secret']
        queryString = urllib.parse.urlencode(queryObj, doseq=False)
        signature = getSignature(secretKey, queryString)
        apiPath = "sapi/v1/capital/config/getall?{0}".format(queryString)
        url="https://api3.binance.com/{0}&signature={1}".format(apiPath, signature)
        #logging.info(url)
        headers = {'User-Agent': 'API', 'X-MBX-APIKEY': apiKey}
        try:
            response=requests.get(url, headers=headers)
            #logging.info("calling binance network")
            if response.status_code == 200:
                r=json.loads(response.content)
                #logging.info(json.dumps(r, indent = 3))
                #timeStamp = datetime.today().strftime("%B,%d %H:%M:%S")
                timeStamp = int(time.time()*1000)
                coins = store['coins']
                #sameNetwork = ["satang","binance"]
                for c in coins:
                    for v in r:
                        if v['coin'] == c['name']:
                            for x in c['exchange']:
                                if x['name'] == "binance":
                                    if len(v['networkList']) > 0:
                                        for n in v['networkList']:
                                            if n['network'] == c['network']:
                                                obj = {
                                                        "fee": n['withdrawFee'],
                                                        "min": n['withdrawMin'],
                                                        "deposit": n['depositEnable'],
                                                        "withdraw": n['withdrawEnable'],
                                                        "timeStamp": timeStamp
                                                        }
                                                trans = "fee_%s_%s" % (c['name'], x['name'])
                                                #logging.info(trans)
                                                #logging.info(obj)
                                                store[trans] = obj

                                #if x['name'] == "satang":
                                #    trans = "fee_%s_%s" % (c['name'], x['name'])
                                #    prev = "fee_%s_binance" % (c['name'])
                                #    store[trans] = store[prev]

                            break
            else:
                responseHandler(response)
        except:
            logging.info("connection reset binanceNetWork")
            pass

    q.put(store)
    return
    #logging.info(obj)
    #return obj

#def getFeeUpdate(exchange, coin, coins, q):
#    store = q.get()
#    fee = 0.0
#    sameNetwork = ["satang","binance"]
#    trans = "fee_%s_%s" % (coin, exchange)
#    for c in coins:
#        if c['name'] == coin:
#            for x in c['exchange']:
#                if x['name'] == exchange:
#                    if exchange in sameNetwork:
#                        if exchange == "binance":
#                            network = c['network']
#                            feeUpdate = binanceNetwork(coin, network, q)
#                            if feeUpdate is not None:
#                                store[trans] = feeUpdate
#                                fee = float(feeUpdate['fee'])
#                        if exchange == "satang":
#                            prev = "fee_%s_binance" % (coin)
#                            store[trans] = store[prev]
#                        break
#            break
#
#    q.put(store)
#    return fee

def transFeeCoin(coin, exchange, q):
    store = q.get()
    fee = 0.0
    if store is not None:
        try:
            coins = store['coins']
            trans = "fee_%s_%s" % (coin, exchange)
            #logging.info(trans)
            #if store[trans] is not None:
            if len(store[trans]) > 0:
                fee = float(store[trans]['fee'])
        except Exception as e:
            logging.info(e)
            pass

    q.put(store)
    f = '{:f}'.format(fee)
    return f

#def transFeeCoin(coin, exchange, q):
#    store = q.get()
#    coins = store['coins']
#    fee = 0.0
#    trans = "fee_%s_%s" % (coin, exchange)
#    if store[trans] is not None:
#        fee = float(store[trans]['fee'])
#        if float(fee) > 0.0:
#            ts = store[trans]['timeStamp']
#            now = int(time.time()*1000)
#            diff = now - int(ts)
#            diff = diff / 1000.00
#            diff = int(diff)
#            x = 30
#            if diff > int(x):
#                logging.info(store['netBinance'])
#                log = "diff: %s x: %s" % (diff, x)
#                logging.info(log)
#                logging.info("updating network <---------------")
#                fee = getFeeUpdate(exchange, coin, coins, q)
#        #    else:
#        #        fee = float(store[trans]['fee'])
#        #else:
#        #    fee = float(store[trans]['fee'])
#    else:
#        fee = getFeeUpdate(exchange, coin, coins, q)
#
#    q.put(store)
#    f = '{:f}'.format(fee)
#    return f

def averageDST(js, store):
    j = json.loads(js)
    array = j['bids']
    exchange = j['exchange']
    exchanges = ['binance']

    obj = {}
    amount = 0.00
    if exchange in exchanges:
        for k,v in enumerate(array):
            amt = float(list(v)[1])
            amount += amt

        price = float(list(array[9])[0])
        obj['averagePrice'] = price
        obj['averageAmount'] = amount
    elif exchange == "satang":
        array = array[:4]
        for k,v in enumerate(array):
            amt = float(list(v)[1])
            amount += amt

        price = float(list(array[3])[0])
        obj['averagePrice'] = price
        obj['averageAmount'] = amount

    else:
        logging.info("not defined exchange")

    return json.dumps(obj)

def busdTotal(balances, store, q):
    total = 0.00
    subtotal = 0.00
    free = 0.00
    for k,v in enumerate(balances):
        free = float(v['free'])
        asset = v['asset'].lower()
        locked = float(v['locked'])
        calcs = [free, locked]
        for c in calcs:
            if c > 0.00:
                if asset.upper() == "BUSD":
                    value = c
                    subtotal += value
                    store['busd'] = free

    q.put(store)
    #total = redigit(subtotal, 2, True)
    total = subtotal
    return "BUSD: %s" % total

def tstodate(ts):
    ts = ts/1000
    return datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')
    #datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    #datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def initialValues(q):
    STORE = {}
    busd = env("busdRates")
    for rate in busd.split(","):
        end = "endColumn_busd_%s" % rate.lower()
        STORE[end]= 0

        busdx = "busd_%s" % rate.lower()
        STORE[busdx] = 0

        thb = "endColumn_thb_%s" % rate.lower()
        STORE[thb]= 0

        thb = "thb_%s" % rate.lower()
        STORE[thb] = 0

    apis = json.loads(env('apis'))
    for a in apis:
        if a['name'] == "binance":
            STORE['apiBinance'] = a['params']
            STORE['binanceFee'] = a['fee']
            for b in a['users']:
                if b['active'] == True:
                    STORE['keyBinance'] = b['secret']
                    STORE['userBinance'] = b['name']

        if a['name'] == "satang":
            STORE['apiSatang'] = a['params']
            STORE['satangFee'] = a['fee']
            for b in a['users']:
                if b['active'] == True:
                    STORE['keySatang'] = b['secret']
                    STORE['userSatang'] = b['name']

    coins = json.loads(env('coins'))
    for c in coins:
        lastBuy = "satang_%s_last" % c['name'].lower()
        STORE[lastBuy] = 0

    STORE['coins'] = coins
    STORE['rates'] = busd
    STORE['homePause'] = False
    STORE['hAsset'] = 6
    STORE['canTrade'] = False
    #STORE['busd'] = 0.0
    STORE['showPercent'] = -99
    STORE['busd_thb'] = 1.0
    STORE['busdOnly'] = 1.0
    STORE['thbOnly'] = 1.0
    STORE['thbAble'] = 1.0
    STORE['endWallet'] = 0
    STORE['endBuyBinance'] = 0
    #STORE['coinsWallet'] = []
    #STORE['hasPairs'] = []

    STORE['symbols'] = None
    STORE['pairDefinedBinance'] = False
    STORE['actionCoinsBinance'] = []
    STORE['definedCoinsBinance'] = []
    STORE['pullingsBinance'] = []

    STORE['symbolsSecond'] = None
    STORE['pairDefinedSatang'] = False
    STORE['actionCoinsSatang'] = []
    STORE['definedCoinsSatang'] = []
    STORE['pullingsSatang'] = []

    STORE['bidsStore'] = False
    STORE['lastBinanceV'] = 0

    STORE['autoPosition'] = True
    #STORE['autoPosition'] = False

    STORE['binanceBuyPosition'] = 0
    STORE['binanceSellPosition'] = 0
    STORE['binanceWithdraw'] = None

    STORE['satangConfigs'] = None
    STORE['satangWallets'] = None
    STORE['satangBuyPosition'] = 0
    STORE['satangSellPosition'] = 0

    STORE['bncheck'] = False

    STORE['trades'] = []
    STORE['traded'] = []
    # decimal point at the end is important
    STORE['busdMin'] = 160.00
    STORE['thbMin'] = 4000.00
    STORE['busdMax'] = 0
    STORE['thbMax'] = 0
    STORE['wsLimit'] = 5
    STORE['thbMinMargin'] = 1
    STORE['percentMargin'] = 0.298
    # can not be 0.0001 it will be lost
    STORE['cancelMinute'] = 1
    STORE['k2fa'] = "-"

    STORE['netBinance'] = False

    params = ['loop', 'run', 'btx']
    for x in params:
        end = "end%s" % x
        STORE[end] = 0
        STORE[x] = False

    STORE['plist'] = params
    q.put(STORE)

def getLength(array):
    x = []
    for a in array:
        x.append(len(str(a)))
    x.sort()
    return x[-1]

def redigit(value, digit, comma=False):
    value = float(value)
    if comma:
        #return "{1:,.{0}f}".format(digit, float(value))
        #return ('%.%f' % (value, digit)).rstrip('0').rstrip('.')
        return "{1:,.{0}f}".format(digit, value).rstrip('0').rstrip('.')
    else:
        return "{1:.{0}f}".format(digit, float(value))

#def runStatus(q):
#    store = q.get()
#
#    line = 4
#    column = store['endLoop']
#    text = "Run"
#    reverse = True
#    status = str(store['run'])
#    if store['run']:
#        text = "%s: %s" % (text, red(status))
#    else:
#        text = "%s: %s" % (text, green(status))
#
#    clearLine(line, store['endRun'], reverse)
#    obj = json.dumps({
#            "text": text,
#            "line": line,
#            "column": column,
#            "length": len(text),
#            "reverse": reverse
#            })
#    if store['run']:
#        time.sleep(1)
#    drawLine(obj)
#    store['endRun'] = len(text)
#    q.put(store)

def controlStatus(q):
    store = q.get()
    if store is not None:
        params = store['plist']
        line = 4
        for i, param in enumerate(params):
            line += i
            column = 0
            text = param.upper()
            reverse = True
            status = str(store[param])
            if store[param]:
                text = "%s: %s" % (text, red(status))
            else:
                text = "%s: %s" % (text, green(status))

            end = "end%s" % param
            clearLine(line, store[end], reverse)
            obj = json.dumps({
                    "text": text,
                    "line": line,
                    "column": column,
                    "length": len(text),
                    "reverse": reverse
                    })
            if store[param]:
                time.sleep(1)
            drawLine(obj)
            store[end] = len(text)
            q.put(store)

def digitalClock(q):
    line = 2
    column = 0
    timeStamp = datetime.today().strftime("%B,%d %H:%M:%S")
    text = "%s" % (timeStamp)
    reverse = True
    obj = json.dumps({
            "text": text,
            "line": line,
            "column": column,
            "length": len(text),
            "reverse": reverse
            })
    drawLine(obj)
    controlStatus(q)
    #runStatus(q)

def getHeaders(apiKey):
    headers = {'User-Agent': Agent('brave'), 'X-MBX-apiKey': apiKey}
    return headers

def getSignature(secretKey, queryString, exchange=None):
    signature = None
    if exchange == "satang":
        signature = hmac.new(codecs.encode(secretKey), msg=codecs.encode(queryString), digestmod=hashlib.sha512).hexdigest()
    else:
        signature = hmac.new(bytes(secretKey, 'latin-1'), msg=bytes(queryString, 'latin-1'), digestmod=hashlib.sha256).hexdigest()
    return signature

def getOpenAmtBinanceBids(pair, exchange, q):
    store = q.get()
    amt = 0.00
    bids = "bids_%s" % pair.lower()
    if store[bids] is not None:
        position = store['binanceBuyPosition']
        amt = float(list(store[bids][position])[1])
    q.put(store)
    precision = getBaseAssetPrecisionBinance(pair, q)
    return tf(amt, precision)

def getOpenAmtSatangBids(pair, exchange, q):
    store = q.get()
    amt = 0.00
    bids = "bids_%s" % pair.lower()
    if store[bids] is not None:
        if store['autoPosition']:
            sbp = "satangBuyPosition_%s" % pair.lower()
            satangBuyPosition = store[sbp]
            amt = float(list(store[bids][satangBuyPosition])[1])

        #p = position - 1
        #for _ in range(p):
        #    position -= 1
        #    amt += float(list(store[bids][position])[1])
    q.put(store)
    precision = getBaseAssetPrecisionSatang(pair, q)
    return tf(amt, precision)

def getOpenAmtSatangAsks(pair, exchange, q):
    store = q.get()
    amt = 0.00
    asks = "asks_%s" % pair.lower()
    if store[asks] is not None:
        if store['autoPosition']:
            ssp = "satangSellPosition_%s" % pair.lower()
            satangSellPosition = store[ssp]
            amt = float(list(store[asks][satangSellPosition])[1])

    q.put(store)
    precision = getBaseAssetPrecisionSatang(pair, q)
    return tf(amt, precision)

def getEBUSD(amt, q):
    price = 0.00
    store = q.get()
    bids = "bids_busd_thb"
    if store[bids] is not None:
        for a in store[bids]:
            #logging.info(list(a)[1])
            if float(list(a)[1]) > amt:
                thbAble = float(list(a)[0]) * float(list(a)[1])
                if thbAble > store['thbMin']:
                    price = float(list(a)[0])
                    store['thbAble'] = thbAble
                    #log = "%s %s" % (float(list(a)[1]), float(list(a)[0]))
                    #logging.info(log)
                    break
    q.put(store)
    return price

#def getCoinBUSD(obj, q):
#    j = json.loads(obj)
#    pair = j['pair']
#    buy = j['buy']
#    exchange = j['exchange']
#    store = q.get()
#    price = 0.0
#    binanceBuyPosition = store['binanceBuyPosition']
#    binanceSellPosition = store['binanceSellPosition']
#    satangBuyPosition = store['satangBuyPosition']
#    satangSellPosition = store['satangSellPosition']
#    if len(store['pullingsBinance']) > 0:
#        bids = "bids_%s" % pair.lower()
#        asks = "asks_%s" % pair.lower()
#        if store[bids] is not None:
#            if buy:
#                if exchange == "binance":
#                    bp = list(store[bids][binanceBuyPosition])[0]
#                if exchange == "satang":
#                    bp = list(store[bids][satangBuyPosition])[0]
#
#            else:
#                if exchange == "binance":
#                    bp = list(store[asks][binanceSellPosition])[0]
#                if exchange == "satang":
#                    bp = list(store[asks][satangSellPosition])[0]
#
#            #price = redigit(bp, 8, True)
#            price = ("{:.8f}".format(float(bp)))
#            #price = calcTicketSizeBinance(float(bp), pair, q)
#        #else:
#        #    logging.info("not found: %s" % bids)
#
#    q.put(store)
#    return price

def findPosition(currentPosition, array, minimum):
    position = currentPosition
    for k, a in enumerate(array):
        price = float(list(a)[0])
        amt = float(list(a)[1])
        calcAmt = float(minimum/price)
        #log = "Price: %s Amt: %s Calc: %s Minimum: %s" % (price, amt, calcAmt, minimum)
        #logging.info(log)
        if amt > calcAmt:
            position = k
            #log = "K: %s P: %s" % (k, position)
            #logging.info(log)
            break
        else:
            position = len(array) - 1

    #logging.info(position)
    return position

def getCoinBUSD(obj, q):
    j = json.loads(obj)
    pair = j['pair']
    buy = j['buy']
    exchange = j['exchange']
    store = q.get()
    price = 0.0

    binanceBuyPosition = store['binanceBuyPosition']
    binanceSellPosition = store['binanceSellPosition']
    satangBuyPosition = store['satangBuyPosition']
    satangSellPosition = store['satangSellPosition']

    if len(store['pullingsBinance']) > 0:
        bids = "bids_%s" % pair.lower()
        asks = "asks_%s" % pair.lower()
        if store[bids] is not None:

            if exchange == "binance":
                # ignore binance position cause high liquidity
                if buy:
                    bp = list(store[bids][binanceBuyPosition])[0]
                else:
                    bp = list(store[asks][binanceSellPosition])[0]

            if exchange == "satang":
                if store['autoPosition']:
                    sbp = "satangBuyPosition_%s" % pair.lower()
                    satangBuyPosition = store[sbp]

                    thbMin = store['busdMin'] * store['busd_thb']
                    satangBuyPosition = findPosition(satangBuyPosition, store[bids], thbMin)

                    store[sbp] = satangBuyPosition

                if buy:
                    bp = list(store[bids][satangBuyPosition])[0]
                else:
                    bp = list(store[asks][satangSellPosition])[0]

            #if buy:
            #    if exchange == "binance":
            #        bp = list(store[bids][binanceBuyPosition])[0]
            #    if exchange == "satang":
            #        bp = list(store[bids][satangBuyPosition])[0]

            #else:
            #    if exchange == "binance":
            #        bp = list(store[asks][binanceSellPosition])[0]
            #    if exchange == "satang":
            #        bp = list(store[asks][satangSellPosition])[0]

            #price = redigit(bp, 8, True)
            price = ("{:.8f}".format(float(bp)))
            #price = calcTicketSizeBinance(float(bp), pair, q)
        #else:
        #    logging.info("not found: %s" % bids)

    q.put(store)
    return price

def getCoinBUSD_MOD(obj, q):
    j = json.loads(obj)
    pair = j['pair']
    buy = j['buy']
    exchange = j['exchange']
    store = q.get()
    price = 0.0
    binanceBuyPosition = store['binanceBuyPosition']
    binanceSellPosition = store['binanceSellPosition']
    satangBuyPosition = store['satangBuyPosition']
    satangSellPosition = store['satangSellPosition']
    if len(store['pullingsBinance']) > 0:
        bids = "bids_%s" % pair.lower()
        asks = "asks_%s" % pair.lower()
        if store[bids] is not None:
            if buy:
                #if exchange == "binance": # for Satang calc
                #    #position = findPosition(binanceBuyPosition, store[bids], store['busdMin'])
                #    #bp = list(store[bids][position])[0]
                #    bp = list(store[bids][0])[0]
                if exchange == "satang": # for Binance calc
                    thbMin = store['busdMin'] * store['busd_thb']
                    position = findPosition(satangBuyPosition, store[bids], thbMin)
                    bp = list(store[bids][position])[0]
                    #bp = list(store[bids][0])[0]

            #else:
            #    if exchange == "binance":
            #        position = findPosition(binanceSellPosition, store[asks]), store['busdMin']
            #        bp = list(store[asks][position])[0]
            #    if exchange == "satang":
            #        position = findPosition(satangSellPosition, store[asks], store['thbMin'])
            #        bp = list(store[asks][position])[0]

            #price = redigit(bp, 8, True)
            price = ("{:.8f}".format(float(bp)))
            #price = calcTicketSizeBinance(float(bp), pair, q)
        #else:
        #    logging.info("not found: %s" % bids)

    q.put(store)
    return price

def getMarginBinance(coin, q):
    margin =  {
            "buyAmt": None,
            "sellAmt": None,
            "busd": 0.00
            }
    store = q.get()
    # FIXIT
    busd = float(store['busdMin'])
    if float(store['busdOnly']) > busd:
        busd = float(store['busdOnly'])
    #    store['busdMin'] = busd

    firstPair = "%sBUSD" % coin
    for x in store['coins']:
        if x['name'] == coin:
            if x['reverse']:
                firstPair = "BUSD%s" % coin
                break

    x = {
            "pair": firstPair,
            "cost": busd,
            "fee": store['binanceFee'],
            "exchange": "binance"
            }
    obj = json.dumps(x)
    first = calcAmount(obj, q)
    if first['price'] is not None:
        secondPair = "%s_THB" % (coin)
        x = { "pair": secondPair, "buy": True, "exchange": "satang" }
        satangSellPrice = getCoinBUSD(json.dumps(x), q)
        satangSellPrice = calcTicketSizeSatang(float(satangSellPrice), secondPair, q)

        required = first['amt']
        openAmt = getOpenAmtSatangBids(secondPair, "satang", q)
        precision = getBaseAssetPrecisionSatang(secondPair, q)
        #if required > openAmt: required = openAmt
        transFee = transFeeCoin(coin, "binance", q)
        remain = required - float(transFee)
        satangSellAmt = tf(remain, precision)

        binanceBuyAmtWithFee = satangSellAmt + float(transFee)
        step = getPairStepBinance(firstPair, q)
        binanceBuyAmtWithFee = math.ceil(binanceBuyAmtWithFee*10**step)/10**step

        newCost = first['price'] * binanceBuyAmtWithFee
        newCost = tf(newCost, 8)

        gotTHB = float(satangSellAmt) * float(satangSellPrice)
        gotTHB = gotTHB - (gotTHB * (store['satangFee'] / 100.0))
        gotTHB = calcTicketSizeSatang(gotTHB, secondPair, q)

        busdTHB = float(store['busd_thb'])
        thbBUSD = gotTHB / busdTHB
        thbBUSD = calcTicketSizeBinance(thbBUSD, firstPair, q)

        if float(thbBUSD) > 0.0:
            m = thbBUSD - newCost
            percent = (100 * m ) / thbBUSD
            percent = tf(percent, 3)
            m = calcTicketSizeBinance(m, firstPair, q)
            m = tf(m, 2)
            n = m * busdTHB
            n = calcTicketSizeBinance(n, firstPair, q)
            n = tf(n, 2)
            margin = {
                    "buyPrice": first['price'],
                    "buyAmt": binanceBuyAmtWithFee,
                    "fee": transFee,
                    "sellPrice": satangSellPrice,
                    "sellAmt": satangSellAmt,
                    "openAmt": openAmt,
                    "percent": percent,
                    "busd": m,
                    "thb": n
                    }
            #logging.info(json.dumps(margin, indent=3))
            #os.system("clear")
            #os._exit(1)

    q.put(store)
    return json.dumps(margin)

def getMarginSatang(coin, q):
    # initial object
    margin =  {
            "buyAmt": None,
            "sellAmt": None,
            "busd": 0.00
            }
    store = q.get()
    thb = float(store['thbMin'])
    firstPair = "%s_THB" % coin
    x = {
            "pair": firstPair,
            "cost": thb,
            "fee": store['satangFee'],
            "exchange": "satang"
            }
    obj = json.dumps(x)
    first = calcAmount(obj, q)
    if first['price'] is not None:
        secondPair = "%sBUSD" % (coin)
        for x in store['coins']:
            if x['name'] == coin:
                if x['reverse']:
                    secondPair = "BUSD%s" % coin
                    break

        x = {"pair": secondPair,"buy": True,"exchange": "binance"}
        binanceSellPrice = getCoinBUSD(json.dumps(x), q)
        binanceSellPrice = calcTicketSizeBinance(float(binanceSellPrice), secondPair, q)

        required = first['amt']
        #openAmt = getOpenAmtBinanceBids(secondPair, "binance", q)

        openAmt = getOpenAmtSatangAsks(firstPair, "satang", q)
        #openAmt = "++"

        precision = getPairStepBinance(secondPair, q)

        transFee = transFeeCoin(coin, "satang", q)
        remain = required - float(transFee)

        binanceSellAmt = tf(remain, precision)
        satangBuyAmtWithFee = binanceSellAmt + float(transFee)
        step = getBaseAssetPrecisionSatang(firstPair, q)
        satangBuyAmtWithFee = math.ceil(satangBuyAmtWithFee*10**step)/10**step

        newCost = first['price'] * satangBuyAmtWithFee
        newCost = tf(newCost, 8)

        gotBUSD = float(binanceSellAmt) * float(binanceSellPrice)
        gotBUSD = gotBUSD - (gotBUSD * (store['binanceFee'] / 100.0))
        gotBUSD = calcTicketSizeBinance(gotBUSD, secondPair, q)

        busdTHB = float(store['busd_thb'])
        thbBUSD = gotBUSD * busdTHB
        thbBUSD = calcTicketSizeSatang(thbBUSD, firstPair, q)

        if float(thbBUSD) > 0.0:
            m = thbBUSD - newCost
            percent = (100 * m ) / thbBUSD
            percent = tf(percent, 3)
            m = tf(m, 2)
            n = m / busdTHB
            n = tf(n, 2)
            o = tf(newCost, 2)
            profit = newCost + m
            p = tf(profit, 2)
            busdPro = gotBUSD
            busdPro = tf(busdPro, 2)
            eBUSD = getEBUSD(busdPro, q)
            backConv = eBUSD * busdPro
            fee = backConv * (0.25/100.00)
            backConv = backConv - fee
            backConv = tf(backConv, 2)
            margin = {
                    "buyPrice": first['price'],
                    "buyAmt": satangBuyAmtWithFee,
                    "fee": transFee,
                    "sellPrice": binanceSellPrice,
                    "sellAmt": binanceSellAmt,
                    "openAmt": openAmt,
                    "percent": percent,
                    "thb": m,
                    "busd": n,
                    "cost": o,
                    "profit": p,
                    "busdPro": busdPro,
                    "ebusd": eBUSD,
                    "backConv": backConv
                    }
            #logging.info(json.dumps(margin, indent=3))
            #os.system("clear")
            #os._exit(1)

    q.put(store)
    return json.dumps(margin)

def getQuotePrecisionBinance(pair, q):
    pair = pair.upper()
    precision = 0
    store = q.get()
    for v in store['symbols']:
        if v['symbol'] == pair:
            precision = float(v['quotePrecision'])
            break

    q.put(store)
    return precision

def calcQuotePrecisionBinance(price, pair, q):
    pair = pair.upper()
    quote = getQuotePrecisionBinance(pair, q)
    e = tf(price, quote)
    return e

def getBaseAssetPrecisionBinance(pair, q):
    pair = pair.upper()
    precision = 0
    store = q.get()
    for v in store['symbols']:
        if v['symbol'] == pair:
            precision = int(v['baseAssetPrecision'])
            break

    q.put(store)
    return precision

def calcBaseAssetPrecisionBinance(amount, pair, q):
    pair = pair.upper()
    baseAsset = getBaseAssetPrecisionBinance(pair, q)
    e = tf(amount, baseAsset)
    return e

def getQuotePrecisionSatang(pair, q):
    pair = pair.lower()
    precision = 0
    store = q.get()
    for v in store['symbolsSecond']:
        if v['symbol'] == pair:
            precision = float(v['quotePrecision'])
            break

    q.put(store)
    #logging.info(precision)
    return precision

def calcQuotePrecisionSatang(price, pair, q):
    pair = pair.lower()
    quote = getQuotePrecisionSatang(pair, q)
    e = tf(price, quote)
    return e

def getBaseAssetPrecisionSatang(pair, q):
    pair = pair.lower()
    precision = 0
    store = q.get()
    for v in store['symbolsSecond']:
        if v['symbol'] == pair:
            precision = int(v['baseAssetPrecision'])
            break

    q.put(store)
    return precision

def calcBaseAssetPrecisionSatang(amount, pair, q):
    pair = pair.lower()
    baseAsset = getBaseAssetPrecisionSatang(pair, q)
    e = tf(amount, baseAsset)
    return e

def getTicketSize(pair, q):
    stepTicket = 0.00000000
    store = q.get()
    for v in store['symbols']:
        #logging.info(v['symbol'])
        if v['symbol'] == pair:
            #log = "found symbol: %s" % pair
            #logging.info(log)
            for k in v['filters']:
                if k['filterType'] == "PRICE_FILTER":
                    stepTicket = float(k['tickSize'])
                    #logging.info(k)
                    break
            break

    q.put(store)
    return stepTicket

def calcTicketSizeBinance(price, pair, q):
    ticketSize = getTicketSize(pair, q)
    #logging.info(ticketSize)
    b = "{:.1e}".format(ticketSize)
    #logging.info(b)
    c = str(b).split("e")[1]
    d = abs(int(c))
    e = tf(price, d)
    #log = "%s %s %s %s" % (b, c, d, e)
    #logging.info(log)
    return e

def getTicketSizeSecond(pair, q):
    stepTicket = 0.00000000
    store = q.get()
    for v in store['symbolsSecond']:
        if v['symbol'] == pair:
            for k in v['filters']:
                if k['filterType'] == "PRICE_FILTER":
                    stepTicket = float(k['tickSize'])
                    break
            break

    q.put(store)
    return stepTicket

def calcTicketSizeSatang(price, pair, q):
    pair = pair.lower()
    ticketSize = getTicketSizeSecond(pair, q)
    b = "{:.1e}".format(ticketSize)
    c = str(b).split("e")[1]
    d = abs(int(c))
    e = tf(price, d)
    return e

def getPairStepBinance(pair, q):
    pair = pair.upper()
    stepSize = 0.00000000
    store = q.get()
    for v in store['symbols']:
        #logging.info(v['symbol'])
        if v['symbol'] == pair:
            #log = "found symbol: %s" % pair
            #logging.info(log)
            for k in v['filters']:
                if k['filterType'] == "LOT_SIZE":
                    stepSize = float(k['stepSize'])
                    #logging.info(k)
                    break
            break
    b = "{:.1e}".format(stepSize)
    c = str(b).split("e")[1]
    d = abs(int(c))
    q.put(store)
    return d

def getStepSize(pair, q):
    pair = pair.upper()
    stepSize = 0.00000000
    store = q.get()
    for v in store['symbols']:
        #logging.info(v['symbol'])
        if v['symbol'] == pair:
            #log = "found symbol: %s" % pair
            #logging.info(log)
            for k in v['filters']:
                if k['filterType'] == "LOT_SIZE":
                    stepSize = float(k['stepSize'])
                    #logging.info(k)
                    break
            break

    q.put(store)
    return stepSize

def calcLotSize(amount, pair, q):
    pair = pair.upper()
    stepSize = getStepSize(pair, q)
    #logging.info(stepSize)
    b = "{:.1e}".format(stepSize)
    #logging.info(b)
    c = str(b).split("e")[1]
    d = abs(int(c))
    e = tf(amount, d)
    #log = "%s %s %s %s" % (b, c, d, e)
    #logging.info(log)
    return e

def getMinNotional(pair, q):
    minNotional = 10.00000000
    store = q.get()
    for v in store['symbols']:
        if v['symbol'] == pair:
            for k in v['filters']:
                if k['filterType'] == "MIN_NOTIONAL":
                    minNotional = float(k['minNotional'])
                    break
            break

    q.put(store)
    return minNotional

def enoughToSell(pair, free, q):
    enough = False
    store = q.get()
    x = {
            "pair": pair,
            "middle": False,
            "buy": True
            }
    price = getCoinBUSD(json.dumps(x), q)
    total = float(price) * float(free)
    notional = getMinNotional(pair, q)
    if total > notional:
        enough = True

    #price = redigit(bp, 8, True)
    #total = redigit(total, 8, False)
    #log = "pair: %s freeLot: %s price: %s total: %s notional: %s" % (pair, free, price, total, notional)
    #logging.info(log)

    q.put(store)
    return enough

def responseHandler(response):
    logging.info(response)
    notices = [429, 418]
    if int(response.status_code) in notices:
        os._exit(1)


