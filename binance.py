import os
import sys
import time
import json
import requests
import urllib
import pyotp
#from termcolor import colored
import logging
import multiprocessing
from common import blockDraw
from utils import getLength, redigit, tstodate, getSignature, getHeaders, busdTotal, green, red, getCoinBUSD, enoughToSell, getStepSize, responseHandler, calcLotSize, getTicketSize, tf, calcTicketSizeBinance, quoteAssets
from useragent import Agent
from screen import drawLine, clearLine
from ws import MarketUpdate

usleep = lambda x: time.sleep(x/1000000.0)

def pairDefinedBinance(rawSym, q):
    store = q.get()

    watchCoins = []
    for coin in store['coins']:
        if coin['monitor']:
            watchCoins.append(coin['name'])
            trans = "fee_%s_binance" % coin['name']
            #logging.info(trans)
            store[trans] = None

    fixCoin = "BUSD"
    symbols = quoteAssets(rawSym, watchCoins, fixCoin)
    coins = []

    for i,s in enumerate(symbols):
        coin = {}
        pair = "%s%s" % (s['baseAsset'], fixCoin)
        if s['baseAsset'] == fixCoin:
            pair = "%s%s" % (fixCoin, s['quoteAsset'])

        coin['pair'] = pair.lower()
        coins.append(coin)

    log = "defined pairs Binance: %s" % len(coins)
    logging.info(log)
    if len(coins) > 0:
        c = []
        for a in coins:
            bidName = "bids_%s" % a['pair']
            store[bidName] = None
            askName = "asks_%s" % a['pair']
            store[askName] = None
            c.append(a['pair'])

        store['pairDefinedBinance'] = True
        store['definedCoinsBinance'] = c
        store['actionCoinsBinance'] = watchCoins
    q.put(store)
    time.sleep(5)
    return

def exchangeInfoBinance(q):
    logging.info("exchangeInfoBinance")
    store = q.get()

    # binance
    if store is not None:
        endPoint = store['apiBinance']['endpoint']
        path = store['apiBinance']['infoPath']
        try:
            apiPath = "{0}".format(path)
            url="{0}/{1}".format(endPoint, apiPath)
            headers = {'User-Agent': Agent('brave')}
            getResp = requests.get(url, headers=headers)
            if getResp.status_code == 200:
                r = json.loads(getResp.content)
                store['symbols'] = r['symbols']
                #logging.info(store['pairDefinedBinance'])
                if not store['pairDefinedBinance']:
                    pairDefinedBinance(r['symbols'], q)

            elif getResp.status_code == 400:
                logging.info(getResp)
            else:
                logging.info(getResp)
                logging.info("coinPrice get error")
                responseHandler(response)
        except:
            logging.info("Binance Info Error")
            pass

    q.put(store)
    return

def processSell(pair, free, price, q):
    store = q.get()
    logging.info("checking enough to sell")
    free = calcLotSize(free, pair, q)
    if enoughToSell(pair, free, q):
        log = "enough to %s free: %s" % (pair, free)
        logging.info(log)
        if True:
        #if noAnyOpen(q):
            sellLimit(pair, free, price, q)
            #sellMarket(pair, free, q)
    else:
        log = "not enough to %s free: %s" % (pair, free)
        logging.info(log)

    q.put(store)

    #return False

#def processSell(coin, free, q):
#    store = q.get()
#    endCoin = store['endCoin']
#    second = False
#    if coin == endCoin: # sell to BUSD
#        pair = "%sBUSD" % coin
#        free = calcLotSize(free, pair, q)
#        if enoughToSell(pair, free, q):
#            log = "enough to sell %s %s free: %s" % (endCoin, pair, free)
#            logging.info(log)
#            sellThird(pair, free, second, q)
#        else:
#            log = "not enough to sell %s %s free: %s" % (endCoin, pair, free)
#            logging.info(log)
#
#    else: # sell to BNB
#        second = True
#        pair = "%s%s" % (coin, endCoin)
#        free = calcLotSize(free, pair, q)
#        if enoughToSell(pair, free, q):
#            log = "enough to %s free: %s" % (pair, free)
#            logging.info(log)
#            sellThird(pair, free, second, q)
#        else:
#            log = "not enough to %s free: %s" % (pair, free)
#            logging.info(log)
#
#    q.put(store)
#
#    #return False

def busdTX(coin, amt, q):
    logging.info('Process TX')

def stockCheckProcess(q):
    logging.info("stock checking process")
    store = q.get()
    if store is not None:
        if len(store['actionCoinsBinance']) == len(store['pullingsBinance']) and len(store['pullingsBinance']) > 0:
            if not store['homePause']:
                apiKey = store['keyBinance']['key']
                apiSecret = store['keyBinance']['secret']
                endPoint = store['apiBinance']['endpoint']
                path = store['apiBinance']['accountPath']
                timeStamp = int(time.time()*1000)
                queryObj = {
                        "recvWindow": 5000,
                        "timestamp": timeStamp
                        }
                queryString = urllib.parse.urlencode(queryObj, doseq=False)
                signature = getSignature(apiSecret, queryString)
                if signature is not None:
                    apiPath = "{0}?{1}".format(path, queryString)
                    url="{0}/{1}&signature={2}".format(endPoint, apiPath, signature)
                    headers = getHeaders(apiKey)
                    founds = []
                    try:
                        response=requests.get(url, headers=headers)
                        if response.status_code == 200:
                            r=json.loads(response.content)
                            #logging.info(json.dumps(r, indent=3))

                            #f = open("/tmp/bnst_process.json","r")
                            #x = f.read()
                            #f.close()
                            #p = json.loads(x)

                            for i,v in enumerate(r['balances']):
                                asset = v['asset']
                                free = float(v['free'])
                                #logging.info(f'{asset} {free}')

                                #if asset == "BUSD" and free > 10.0:
                                if asset == "BUSD":
                                    if store['btx']:
                                        logging.info("process tx busd")
                                        busdTX(asset, free, q)
                            #    if asset == coin:
                            #        free = float(v['free'])
                            #        if float(free) > 0.0:
                            #            #logging.info(asset)
                            #            #logging.info(free)
                            #            x = {
                            #                    "pair": pair,
                            #                    "amount": free,
                            #                    "price": price
                            #                    }
                            #            founds.append(x)
                            #        else:
                            #            logging.info("coin < 0.01")


                            store['bncheck'] = False
                        else:
                            responseHandler(response)
                    except:
                        logging.info("connection reset stockCheckProcess")
                        pass

                    # process sell
                    if len(founds) > 0:
                        for j,k in enumerate(founds):
                            logging.info(k['name'])
                            logging.info(k['amount'])
                            #processSell(k['pair'], k['amount'], k['price'], q)
                            time.sleep(0.5)

    q.put(store)

def displayWallet(coins, q):
    store = q.get()
    if store is not None:
        hAsset = store['hAsset']
        start = hAsset
        reverse = False
        nextColumn = 0
        space = 3
        maxLength = 0
        lst = ['asset', 'free', 'locked']
        lines = {}
        size = os.get_terminal_size()
        endColumn = 120

        exchange = "binance"
        exchangeText = red(exchange.upper())
        if store['canTrade']:
            exchangeText = green(exchange.upper())

        for v in lst:
            lines[v] = start
            clearLine(start, endColumn)
            start += 1

        exist = False
        lastBinanceV = 0

        for c in coins:
            asset = c['asset']
            free = c['free']
            locked = c['locked']

            if asset == "BUSD":
                store['busdOnly'] = free
                if free > store['busdMax']:
                    store['busdMax'] = free

            if not exist:
                exist = True
                text = "%s [%s] [BUSD, %s, {%s|%s|%s}] [THB, {%s|%s|%s|%s}]" % (exchangeText, store['k2fa'], store['busd_thb'], store['busdMin'], tf(store['busdMax'],2), store['busdOnly'], tf(store['thbAble'], 0), store['thbMin'], tf(store['thbMax'],2), tf(store['thbOnly'],2))
                line = hAsset - 1
                obj = json.dumps({
                        "text": text,
                        "line": line,
                        "column": 0,
                        "length": len(text),
                        "reverse": reverse
                        })
                drawLine(obj, True)

                obj = {
                        "lines": lines,
                        "nextColumn": nextColumn,
                        "space": space,
                        "lst": lst,
                        "reverse": reverse
                        }
                lastBinanceV = nextColumn
                nextColumn = blockDraw(json.dumps(obj), True)

            if free > 0.00 or locked > 0.00:
                ass = ["BUSD", "USDT"]
                if asset in ass:
                    lst = [asset, free, locked]
                    obj = {
                            "lines": lines,
                            "nextColumn": nextColumn,
                            "space": space,
                            "lst": lst,
                            "reverse": reverse
                            }
                    lastBinanceV = nextColumn
                    nextColumn = blockDraw(json.dumps(obj), True)

        store['endWallet'] = start + 1
        #store['coinsWallet'] = coinsWallet
        store['lastBinanceV'] = lastBinanceV

    q.put(store)

def getAddr(coin, q):
    '''
    get coin address,network,tag from env
    '''
    store = q.get()
    addr = {}
    if store is not None:
        #logging.info(store['userSatang'])
        for c in store['coins']:
            if c['name'] == coin:
                #logging.info(c)
                for x in c['exchange']:
                    if x['name'] == "satang":
                        for a in x['addrs']:
                            if a['name'] == store['userSatang']:
                                addr['addr'] = a['addr']
                                addr['tag'] = a['tag']
                                addr['network'] = c['network']
                                break
    q.put(store)
    return addr

def toSatang(coin, amt, q):
    addr = getAddr(coin, q)
    store = q.get()
    if store is not None:
        if len(addr) > 0:
            #logging.info(addr)
            timeStamp = int(time.time()*1000)
            queryObj = {}
            queryObj['coin'] = coin
            queryObj['address'] = addr['addr']
            if addr['tag']:
                queryObj['addressTag'] = addr['tag']
            queryObj['amount'] = amt
            queryObj['network'] = addr['network']
            queryObj['recvWindow'] = 5000
            queryObj['timestamp'] = timeStamp
            logging.info(queryObj)

            queryString = urllib.parse.urlencode(queryObj, doseq=False)
            apiKey = store['keyBinance']['key']
            apiSecret = store['keyBinance']['secret']
            signature = getSignature(apiSecret, queryString)
            if signature is not None:
                apiPath = "sapi/v1/capital/withdraw/apply"
                url="https://api.binance.com/{0}?{1}&signature={2}".format(apiPath, queryString, signature)
                headers = getHeaders(apiKey)
                try:
                    data = "{0}&signature={1}".format(queryString, signature)
                    logging.info(data)
                    response = requests.post(url, headers=headers, data=data, allow_redirects=True)
                    if response.status_code == 200:
                        r=json.loads(response.content)
                        logging.info(json.dumps(r, indent=3))
                    else:
                        responseHandler(response)
                except Exception as e:
                    logging.info("connection reset toSatang")
                    logging.info(e)
                    pass

    q.put(store)

def processStock(coins, q):
    logging.info("Process stock Binance")
    store = q.get()
    if store is not None:
        for c in coins:
            fee = "fee_%s_binance" % c['asset']
            #logging.info(float(store[fee]['min']))
            if c['free'] > float(store[fee]['min']): # minWithdraw
                if c['asset'] == "BUSD":
                    if store['btx']:
                        logging.info("busd withdraw process")
                        if False: # if forcing
                            toSatang(c['asset'], c['free'], q)
                        else: # not forcing
                            if True: # if BUSD is not last deposit
                                if len(store['trades']) > 0:
                                    if not orderExist(store['trades'][0]['sell']['pair'], q):
                                        toSatang(c['asset'], c['free'], q)
                                else:
                                    toSatang(c['asset'], c['free'], q)
                else:
                    logging.info(f"process others coin")
                    #thbMax = store['thbMax'] - store['thbOnly']
                    #free = c['free']
                    #asset = c['asset']
                    #pair = "%sBUSD" % asset
                    #bids = "bids_%s" % pair.lower()
                    #bp = list(store[bids][0])[0]
                    #if float(bp) * free > 10:
                    #    alphaPrice = (thbMax / store['busd_thb']) / c['free']
                    #    rate = store['busd_thb']
                    #    logging.info(f'max:{thbMax} price:{alphaPrice} amt:{free} bp:{bp} busd:{rate} {asset}')
                    #    a = alphaPrice * free
                    #    fee = store['binanceFee'] + store['satangFee'] + 0.1
                    #    b = a * (fee/100)
                    #    d = a + b
                    #    reCalc = d / free
                    #    logging.info(f'{a} {b} {d} {reCalc} {pair}')
                    #    bravoPrice = calcTicketSizeBinance(reCalc, pair, q)

                    #    price = bravoPrice
                    #    free = calcLotSize(free, pair, q)
                    #    time.sleep(0.5)
                    #    sellLimit(pair, free, price, q)

                    if len(store['trades']) > 0:
                        trades = sorted(store['trades'], key=lambda k: k['ts'], reverse=False)
                        for t in trades:
                            if t['coin'] == c['asset']:
                                if t['status'] == "buy":
                                    pair = t['sell']['pair']
                                    free = c['free']
                                    price = t['sell']['price']
                                    #processSell(pair, free, price, q)
                                    free = calcLotSize(free, pair, q)
                                    time.sleep(0.5)
                                    if float(free) * float(price) > 10:
                                        sellLimit(pair, free, price, q)
                                        #sellMarket(pair, free, price, q)
                                        # update status of trades store
                            else:
                                log = "%s not found in store" % t['coin']
                                logging.info(log)
            #else:
            #    logging.info("less than minimum")

            time.sleep(0.1)
    q.put(store)

def binanceWallet(q):
    #logging.info("binance wallet")
    store = q.get()
    if store is not None:
        apiKey = store['keyBinance']['key']
        apiSecret = store['keyBinance']['secret']
        endPoint = store['apiBinance']['endpoint']
        path = store['apiBinance']['accountPath']
        timeStamp = int(time.time()*1000)
        queryObj = {
                "recvWindow": 5000,
                "timestamp": timeStamp
                }
        queryString = urllib.parse.urlencode(queryObj, doseq=False)
        signature = getSignature(apiSecret, queryString)
        if signature is not None:
            apiPath = "{0}?{1}".format(path, queryString)
            url="{0}/{1}&signature={2}".format(endPoint, apiPath, signature)
            headers = getHeaders(apiKey)
            try:
                response=requests.get(url, headers=headers)
                if response.status_code == 200:
                    r=json.loads(response.content)
                    #logging.info(json.dumps(r, indent=3))
                    if r['canTrade']:
                        store['canTrade'] = True

                    coins = []
                    for i,v in enumerate(r['balances']):
                        for a in store['coins']:
                            if a['name'] == v['asset']:
                                coin = {}
                                coin['asset'] =v['asset']
                                coin['free'] = float(v['free'])
                                coin['locked'] = float(v['locked'])
                                coins.append(coin)

                    if len(coins) > 0:
                        displayWallet(coins, q)
                        time.sleep(1)
                        processStock(coins, q)
                else:
                    responseHandler(response)
            except Exception as e:
                logging.info("connection reset binanceWallet")
                logging.info(e)
                pass

    q.put(store)

def wsCall(sym, q):
    x = MarketUpdate(sym, q)
    x.run()
    time.sleep(0.03)

def binanceBids(limit, q):
    #logging.info("recall bids, asks Binance")
    store = q.get()
    if store is not None:
        if len(store['definedCoinsBinance']) > 0:
            pullings = store['pullingsBinance']
            #log = "pulling First: %s" % len(pullings)
            #logging.info(log)
            processes = []
            for i,sym in enumerate(store['definedCoinsBinance']):
                if sym.lower() not in pullings:
                    #log = "%s %s" % (i, sym.lower())
                    #logging.info(log)

                    #bids = "bids_%s" % s
                    #store[bids] = None

                    #process = multiprocessing.Process(target=wsCall, args=(s, q,))
                    #process.start()
                    #processes.append(process)

                    #time.sleep(0.1)

                    s = sym.lower()
                    wsCall(s, q)

                    #pullings.append(sym.lower())
                    #store['pullingsBinance'] = pullings
                    q.put(store)
                    time.sleep(0.01)
                    #if i > 0:
                    #    break

            #log = "pulling First: %s" % len(pullings)
            #logging.info(log)
        else:
            log = "Binance Coins is not defined"
            logging.info(log)

        if store['symbols'] is not None:
            log = " total first pairs: %s" % len(store['symbols'])
            #logging.info(log)

    q.put(store)

def openOrder(coin, q, buy=False):
    openning = False
    log = "---check openning: %s\n" % coin
    logging.info(log)
    store = q.get()
    if store is not None:
        apiKey = store['api']['key']
        apiSecret = store['api']['secret']
        endPoint = store['api']['endpoint']
        path = store['api']['openOrders']
        timeStamp = int(time.time()*1000)
        queryObj = {
                "symbol": "{}".format(coin),
                "timestamp": timeStamp
                }
        queryString = urllib.parse.urlencode(queryObj, doseq=False)
        signature = getSignature(apiSecret, queryString)
        if signature is not None:
            apiPath = "{0}?{1}".format(path, queryString)
            url="{0}/{1}&signature={2}".format(endPoint, apiPath, signature)
            headers = getHeaders(apiKey)
            try:
                response=requests.get(url, headers=headers)
                if response.status_code == 200:
                    r = json.loads(response.content)
                    if len(r) > 0:
                        if buy:
                            lst = sorted(r, key=lambda k: k['updateTime'], reverse=True)
                            for k,v in enumerate(lst):
                                if v['side'] == "BUY":
                                    logging.info("!!!-----------------YES is buy")
                                    openning = True
                        else:
                            logging.info("!!!-----------------IS NOT buy")
                            openning = True
                else:
                    responseHandler(response)
            except:
                logging.info("connection reset openOrder")
                pass

    log = "open check: %s result: %s" % (coin, openning)
    logging.info(log)
    q.put(store)
    return openning

def orderExist(pair, q):
    exist = False
    store = q.get()
    if store is not None:
        apiKey = store['keyBinance']['key']
        apiSecret = store['keyBinance']['secret']
        endPoint = store['apiBinance']['endpoint']
        path = store['apiBinance']['allOrders']
        timeStamp = int(time.time()*1000)
        headers = getHeaders(apiKey)
        queryObj = {
                "symbol": "{}".format(pair),
                "timestamp": timeStamp
                }
        queryString = urllib.parse.urlencode(queryObj, doseq=False)
        signature = getSignature(apiSecret, queryString)
        if signature is not None:
            apiPath = "{0}?{1}".format(path, queryString)
            url="{0}/{1}&signature={2}".format(endPoint, apiPath, signature)
            try:
                response=requests.get(url, headers=headers)
                if response.status_code == 200:
                    r=json.loads(response.content)
                    #logging.info(json.dumps(r, indent=3))
                    lst = sorted(r, key=lambda k: k['time'], reverse=True)
                    for k,v in enumerate(lst):
                        if v['status'] == "NEW":
                            logging.info(v)
                            exist = True
                else:
                    responseHandler(response)
            except:
                logging.info("error")
                pass

    q.put(store)
    log = "openning %s result: %s" % (pair, exist)
    logging.info(log)
    return exist

def coinMinimum(coin, stepPair, q):
    store = q.get()
    minimum = 0.00
    pair = "%sBUSD" % coin
    logging.info(pair)
    x = {
            "pair": pair,
            "buy": True,
            "middle": False,
            "last": False
            }
    buyPrice = getCoinBUSD(json.dumps(x), q)
    limit = store['busdMin']
    minimum = float(limit) / float(buyPrice)

    minimumLot = calcLotSize(minimum, stepPair, q)

    log = "coin: %s: price: %s minimum: %s minimumLot: %s" % (coin, buyPrice, minimum, minimumLot)
    logging.info(log)
    q.put(store)
    return minimumLot

def freeCoin(coin, q):
    free = 0.0
    store = q.get()
    if store is not None:
        apiKey = store['api']['key']
        apiSecret = store['api']['secret']
        endPoint = store['api']['endpoint']
        path = store['api']['accountPath']
        timeStamp = int(time.time()*1000)
        queryObj = {
        "recvWindow": 5000,
        "timestamp": timeStamp
        }
        queryString = urllib.parse.urlencode(queryObj, doseq=False)
        signature = getSignature(apiSecret, queryString)
        if signature is not None:
            apiPath = "{0}?{1}".format(path, queryString)
            url="{0}/{1}&signature={2}".format(endPoint, apiPath, signature)
            headers = getHeaders(apiKey)
            try:
                response=requests.get(url, headers=headers)
                if response.status_code == 200:
                    r = json.loads(response.content)
                    #logging.info(json.dumps(r, indent=3))
                    for i,v in enumerate(r['balances']):
                        if v['asset'] == coin.upper():
                            free = float(v['free'])
                            break
                else:
                    responseHandler(response)
            except:
                logging.info("connection reset freeCoin")
                pass

    q.put(store)
    log = "freeAll check: %s: %s" % (coin, free)
    logging.info(log)
    return free

def freeCoinLot(coin, pair, q):
    free = freeCoin(coin, q)
    stepSize = getStepSize(pair, q)
    freeLot = calcLotSize(free, pair, q)
    log = "coin: %s freeAll: %s stepSize: %s freeLot: %s" % (pair, free, stepSize, freeLot)
    logging.info(log)
    return freeLot

def openTrade(obj, q):
    j = json.loads(obj)
    pair = j['pair']
    price = j['price']
    quantity = j['quantity']
    side = j['side']
    timeInForce = j['timeInForce']
    store = q.get()
    if store is not None:
        apiKey = store['keyBinance']['key']
        apiSecret = store['keyBinance']['secret']
        endPoint = store['apiBinance']['endpoint']
        path = store['apiBinance']['order']
        timeStamp = int(time.time()*1000)
        queryObj = {
            "symbol": pair,
            "side": side,
            "type": "LIMIT",
            "timeInForce": timeInForce,
            "quantity": quantity,
            "price": price,
            "recvWindow": 5000,
            "timestamp": timeStamp
        }
        queryString = urllib.parse.urlencode(queryObj, doseq=False)
        signature = getSignature(apiSecret, queryString)
        if signature is not None:
            url="{0}/{1}".format(endPoint, path, signature)
            headers = getHeaders(apiKey)
            data = "{0}&signature={1}".format(queryString, signature)
            logging.info(data)
            try:
                response = requests.post(url, headers=headers, data=data, allow_redirects=True)
                if response.status_code == 200:
                    r = json.loads(response.content)
                else:
                    responseHandler(response)
                    logging.info(response.content)
                    if side == "sell":
                        for i,s in enumerate(store['trades']):
                            if s['sell']['pair'] == pair:
                                x = s
                                x['status'] = "sell"
                                store['trades'][i] = x

                    # update store status to sell

            except:
                logging.info("connection reset openTrade")
                pass

    q.put(store)

def noAnyOpen(q):
    logging.info("")
    logging.info("BEGIN---noAnyOpen---")
    notOpens = [True]
    store = q.get()
    for i,v in enumerate(store['trades']):
        pairs = v['pair'].split("_")
        for j,k in enumerate(pairs):
            concateCoin = k.replace("-","")
            logging.info(concateCoin)
            if openOrder(concateCoin, q): # PROMBUSD, PROMBNB, BNBBUSD
                notOpens.append(False)
                time.sleep(0.2)

    q.put(store)
    logging.info("END---noAnyOpen---\n")
    if False in notOpens:
        return False
    else:
        return True

def getPreviousMaxBuyPrice(pair, q):
    lastMaxBuy = 0.0
    store = q.get()
    if store is not None:
        apiKey = store['api']['key']
        apiSecret = store['api']['secret']
        endPoint = store['api']['endpoint']
        path = store['api']['allOrders']
        timeStamp = int(time.time()*1000)
        headers = getHeaders(apiKey)
        queryObj = {
                "symbol": "{}".format(pair),
                #"limit": 500,
                "timestamp": timeStamp
                }
        queryString = urllib.parse.urlencode(queryObj, doseq=False)
        signature = getSignature(apiSecret, queryString)
        if signature is not None:
            apiPath = "{0}?{1}".format(path, queryString)
            url="{0}/{1}&signature={2}".format(endPoint, apiPath, signature)
            try:
                response=requests.get(url, headers=headers)
                if response.status_code == 200:
                    r=json.loads(response.content)
                    #logging.info(json.dumps(r, indent=3))
                    lst = sorted(r, key=lambda k: k['updateTime'], reverse=True)
                    fills = []
                    buyFound = False
                    for k,v in enumerate(lst):
                        if v['status'] == "FILLED":
                            if v['side'] == "SELL":
                                if buyFound == True:
                                    break
                            if v['side'] == "BUY":
                                buyFound = True
                                fills.append(float(v['price']))

                    logging.info(json.dumps(fills, indent=3))
                    fills.sort()
                    lastMaxBuy = fills[-1]
                else:
                    responseHandler(response)
            except:
                logging.info("error")
    q.put(store)
    return lastMaxBuy

def getPreviousMaxBUSD(pair, q):
    lastMaxBuy = 0.0
    store = q.get()
    if store is not None:
        apiKey = store['api']['key']
        apiSecret = store['api']['secret']
        endPoint = store['api']['endpoint']
        path = store['api']['allOrders']
        timeStamp = int(time.time()*1000)
        headers = getHeaders(apiKey)
        queryObj = {
                "symbol": "{}".format(pair),
                #"limit": 500,
                "timestamp": timeStamp
                }
        queryString = urllib.parse.urlencode(queryObj, doseq=False)
        signature = getSignature(apiSecret, queryString)
        if signature is not None:
            apiPath = "{0}?{1}".format(path, queryString)
            url="{0}/{1}&signature={2}".format(endPoint, apiPath, signature)
            try:
                response=requests.get(url, headers=headers)
                if response.status_code == 200:
                    r=json.loads(response.content)
                    #logging.info(json.dumps(r, indent=3))
                    lst = sorted(r, key=lambda k: k['updateTime'], reverse=True)
                    fills = []
                    buyFound = False
                    for k,v in enumerate(lst):
                        if v['status'] == "FILLED":
                            if v['side'] == "SELL":
                                if buyFound == True:
                                    break
                            if v['side'] == "BUY":
                                buyFound = True
                                x = {
                                        "price": v['price'],
                                        "executedQty": v['executedQty'],
                                        "orderId": v['orderId']
                                        }
                                fills.append(x)

                    logging.info(json.dumps(fills, indent=3))
                    prices = []
                    for m,n in enumerate(fills):
                        price = float(n['price']) * float(n['executedQty'])
                        prices.append(price)
                    prices.sort()
                    logging.info(prices)
                    lastMaxBuy = prices[-1]
                else:
                    responseHandler(response)
            except:
                logging.info("error")
    q.put(store)
    return lastMaxBuy

def getPreviousBUSD(pair, q):
    pbusd = 0.0
    store = q.get()
    if store is not None:
        apiKey = store['api']['key']
        apiSecret = store['api']['secret']
        endPoint = store['api']['endpoint']
        path = store['api']['allOrders']
        timeStamp = int(time.time()*1000)
        headers = getHeaders(apiKey)
        queryObj = {
                "symbol": "{}".format(pair),
                #"limit": 500,
                "timestamp": timeStamp
                }
        queryString = urllib.parse.urlencode(queryObj, doseq=False)
        signature = getSignature(apiSecret, queryString)
        if signature is not None:
            apiPath = "{0}?{1}".format(path, queryString)
            url="{0}/{1}&signature={2}".format(endPoint, apiPath, signature)
            try:
                response=requests.get(url, headers=headers)
                if response.status_code == 200:
                    r=json.loads(response.content)
                    #logging.info(json.dumps(r, indent=3))
                    lst = sorted(r, key=lambda k: k['updateTime'], reverse=True)
                    fills = []
                    prevOrderId = None
                    for k,v in enumerate(lst):
                        if v['side'] == "BUY":
                        #if v['side'] == "SELL":
                            #logging.info(v)
                            if v['status'] == "FILLED":
                                #logging.info(v)
                                newOrderId = v['orderId']
                                if prevOrderId is not None:
                                    if newOrderId == prevOrderId:
                                        x = {
                                                "price": v['price'],
                                                "executedQty": v['executedQty'],
                                                "orderId": v['orderId']
                                                }
                                        fills.append(x)
                                    else:
                                        break
                                else:
                                    x = {
                                            "price": v['price'],
                                            "executedQty": v['executedQty'],
                                            "orderId": v['orderId']
                                            }
                                    fills.append(x)
                            prevOrderId = newOrderId

                    logging.info(json.dumps(fills, indent=3))
                    for m,n in enumerate(fills):
                        price = float(n['price']) * float(n['executedQty'])
                        pbusd += price
                else:
                    responseHandler(response)
            except:
                logging.info("error")
    q.put(store)
    return pbusd

def sellThird(thirdPair, free, second, q):
    ## buy and last
    store = q.get()
    #previousBUSD = getPreviousMaxBUSD(thirdPair, q)
    #log = "-------------------> previous: %s" % previousBUSD
    #logging.info(log)
    #a = previousBUSD + store['digitMargin']
    #b = a / free
    #b = calcTicketSizeBinance(b, thirdPair, q)
    #ticketSize = getTicketSize(thirdPair, q)
    #constant = 5
    #d = ticketSize * 5
    #e = b + d
    #f = e
    ##f = tf(e, 4)

    #log = "free: %s digitMargin: %s margined: %s priceA: %s ticket: %s inc: %s priceC: %s round: %s" % (free, store['digitMargin'], a, b, ticketSize, d, e, f)
    #logging.info(log)

    #calcPrice = calcTicketSizeBinance(free, thirdPair, q)
    freeCalc = calcLotSize(free, thirdPair, q)
    log = "sell third pair: %s" % thirdPair # XRPBUSD 
    logging.info(log)
    x = {
            "pair": thirdPair,
            "buy": False,
            "middle": False,
            "last": True
            }
    if second:
        x = {
                "pair": thirdPair,
                "buy": False,
                "middle": True,
                "last": False
                }
    firstSellPrice = getCoinBUSD(json.dumps(x), q)
    logging.info(firstSellPrice)

    #finalPrice = calcPrice
    #if float(firstSellPrice) > calcPrice:
    finalPrice = firstSellPrice

    obj = {
            "pair": thirdPair,
            "price": finalPrice,
            "quantity": freeCalc,
            "timeInForce": "GTC",
            "side": "SELL"
            }
    logging.info(json.dumps(obj))
    q.put(store)
    openTrade(json.dumps(obj), q)

def sellLimit(pair, free, price, q):
    store = q.get()
    log = "sell limit pair: %s" % pair
    logging.info(log)
    obj = {
            "pair": pair,
            "quantity": free,
            "price": price,
            "side": "SELL",
            "timeInForce": "GTC"
            }
    logging.info(json.dumps(obj, indent=3))
    openTrade(json.dumps(obj), q)
    q.put(store)

def sellSecond(secondPair, free, q):
    log = "sell second pair: %s" % secondPair # TRXXRP 
    logging.info(log)
    x = {
            "pair": secondPair,
            "middle": True,
            "buy": False,
            "last": False
            }
    price = getCoinBUSD(json.dumps(x), q)
    obj = {
            "pair": secondPair,
            "price": price,
            "quantity": free,
            "side": "SELL"
            }
    logging.info(json.dumps(obj))
    #openTrade(json.dumps(obj), q)

def buyFirst(concateCoin, buyPrice, minCoin, q):
    store = q.get()
    coin = "BUSD"
    free = freeCoin(coin, q)
    cost = float(buyPrice) * float(minCoin)
    if free > cost:
    #if free > store['busdMin']:
        minCalc = calcLotSize(minCoin, concateCoin, q)
        log = "buy first pair: %s" % concateCoin
        logging.info(log)

        #second = 60
        #gtc = int(time.time()*1000) + second
        obj = {
                "pair": concateCoin,
                "price": buyPrice,
                "quantity": minCalc,
                "timeInForce": "GTC",
                "side": "BUY"
                }
        logging.info(json.dumps(obj))
        openTrade(json.dumps(obj), q)
    else:
        logging.info("!!! not enough BUSD")

    q.put(store)

def processTrades(q):
    # check to see if trade pairs is openning
    # if yes then check how to it have open
    # and also check position of open order close to 1st or not
    # if condition is not good, time is too long then cancel that order pair
    # and reopenning with new incoming data of that pair

    store = q.get()
    logging.info(json.dumps(store['trades'], indent=3))
    if store['run']:
        if True:
        #if noAnyOpen(q): # TRXBUSD, TRXXRP, XRPBUSD
            for i,v in enumerate(store['trades']):
                #p = v['pair'].split("-")
                #logging.info(p)
                ## TRX 
                #firstCoin = p[0]
                #firstPair = v['pair'].replace("-","")
                #firstFree = freeCoinLot(firstCoin, firstPair, q)
                #minCoin = coinMinimum(firstCoin, firstPair, q)
                #log = "FIRST. coin: %s minimum: %s freeLot: %s" % (firstCoin, minCoin, firstFree)
                #logging.info(log)
                #if enoughToSell(firstPair, firstFree, q):
                #    #if not openOrder(secondPair, q):
                #    if True:
                #        log = "sell first pair: %s" % firstPair
                #        logging.info(log)
                #        sellThird(firstPair, firstFree, q)
                #else:
                if True:
                    # TRXBUSD
                    #if not openOrder(firstPair, q):
                    firstPair = "%sBUSD" % v['pair']
                    if not openOrder(firstPair, q, True):
                    #if True:
                        log = "buy first pair: %s" % firstPair
                        logging.info(log)
                        #buyFirst(firstPair, v['buyPrice'], v['minCoin'], q)

                #    time.sleep(1)
                time.sleep(1)

            time.sleep(0.1)
            if not store['loop']:
                store['run'] = False
                logging.info("turn off run command")

        else:
            logging.info("some of them are opening")
    else:
        logging.info("command run is not active")

    q.put(store)

def deleteOrder(symbol, orderId,  q):
    store = q.get()
    if store is not None:
        apiKey = store['api']['key']
        apiSecret = store['api']['secret']
        endPoint = store['api']['endpoint']
        path = store['api']['order']
        timeStamp = int(time.time()*1000)
        queryObj = {
                "symbol": "{}".format(symbol),
                "orderId": orderId,
                "timestamp": timeStamp
                }
        queryString = urllib.parse.urlencode(queryObj, doseq=False)
        signature = getSignature(apiSecret, queryString)
        if signature is not None:
            apiPath = "{0}?{1}".format(path, queryString)
            url="{0}/{1}&signature={2}".format(endPoint, apiPath, signature)
            headers = getHeaders(apiKey)
            try:
                response=requests.delete(url, headers=headers)
                if response.status_code == 200:
                    r = json.loads(response.content)
                    logging.info(json.dumps(r, indent=3))
                else:
                    responseHandler(response)
            except:
                logging.info("connection reset deleteOrder")
                pass

    q.put(store)

def processCancel(v, q):
    store = q.get()
    openTime = v['time']
    timeStamp = int(time.time()*1000)
    cancelTime = store['cancelMinute']
    cancelSecond = cancelTime * 60 * 1000
    diff = timeStamp - int(openTime)
    log = "open: %s now: %s cancelSecond: %s diff: %s" % (openTime, timeStamp, cancelSecond, diff)
    logging.info(log)
    if True:
    #if diff > cancelSecond:
        bids = "bids_%s" % v['symbol'].lower()
        logging.info("start cancel this id")
        #existPrice = list(store[bids][-1])[0]
        buyPosition = store['buyPosition']
        existPrice = list(store[bids][buyPosition])[0]
        log = "price: %s symbol: %s orderId: %s ask: %s existPrice: %s" % (v['price'], v['symbol'], v['orderId'], bids, existPrice)
        logging.info(log)
        if float(v['price']) < float(existPrice):
            log = "delete: %s %s" % (v['symbol'], v['orderId'])
            logging.info(log)
            deleteOrder(v['symbol'], v['orderId'], q)

    q.put(store)

def cancelBuy(q):
    logging.info("!!!---cancel first pair buy\n")
    store = q.get()
    position = store['buyPosition']
    logging.info(store['trades'])
    if len(store['trades']) > 0:
        apiKey = store['api']['key']
        apiSecret = store['api']['secret']
        endPoint = store['api']['endpoint']
        path = store['api']['openOrders']
        timeStamp = int(time.time()*1000)
        headers = getHeaders(apiKey)

        queryObj = {
                "timestamp": timeStamp
                }
        queryString = urllib.parse.urlencode(queryObj, doseq=False)
        signature = getSignature(apiSecret, queryString)
        if signature is not None:
            apiPath = "{0}?{1}".format(path, queryString)
            url="{0}/{1}&signature={2}".format(endPoint, apiPath, signature)
            try:
                response=requests.get(url, headers=headers)
                if response.status_code == 200:
                    r=json.loads(response.content)
                    #logging.info(json.dumps(r, indent=3))
                    lst = sorted(r, key=lambda k: k['time'], reverse=False)
                    for k,v in enumerate(lst):
                        if v['status'] == "NEW":
                            if v['side'] == "BUY":
                                #logging.info(json.dumps(v, indent=3))
                                processCancel(v, q)
                else:
                    responseHandler(response)
            except:
                logging.info("error")
                pass

    q.put(store)

def binanceHist(q):
    #logging.info("binanceHistory")
    store = q.get()
    if store is not None:
        apiKey = store['keyBinance']['key']
        apiSecret = store['keyBinance']['secret']
        #endPoint = store[exchange]['endpoint']
        #path = store[exchange]['histPath']
        apiPath = "sapi/v1/capital/withdraw/history"
        timeStamp = int(time.time()*1000)
        limit = 50
        queryObj = {
                #"coin": "%sBUSD" % coin,
                "timestamp": timeStamp,
                "limit": limit
                }
        queryString = urllib.parse.urlencode(queryObj, doseq=False)
        signature = getSignature(apiSecret, queryString, "binance")
        if signature is not None:
            #apiPath = "{0}?{1}".format(path, queryString)
            url="https://api.binance.com/{0}?{1}&signature={2}".format(apiPath, queryString, signature)
            #url="{0}/{1}&signature={2}".format(endPoint, apiPath, signature)
            headers = getHeaders(apiKey)
            try:
                response=requests.get(url, headers=headers)
                if response.status_code == 200:
                    r=json.loads(response.content)
                    #logging.info(json.dumps(r, indent=3))
                    store['binanceWithdraw'] = r

            except Exception as e:
                logging.info(f"error history call\n{e}")
                pass

    q.put(store)

#def binanceHistory(q, limit):
#    exchange = "binance"
    #store = q.get()
    #if store is not None:
    #    apiKey = store[exchange]['key']
    #    apiSecret = store[exchange]['secret']
    #    endPoint = store[exchange]['endpoint']
    #    path = store[exchange]['histPath']
    #    startLine = 5
    #    size = os.get_terminal_size()
    #    startColumn = size.columns / 2 + 15
    #    histories = []
    #    for _, coin in enumerate(store['executeCoins']):
    #        timeStamp = int(time.time()*1000)
    #        queryObj = {
    #                "symbol": "%sBUSD" % coin,
    #                "timestamp": timeStamp,
    #                "limit": limit
    #                }
    #        queryString = urllib.parse.urlencode(queryObj, doseq=False)
    #        signature = getSignature(apiSecret, queryString, exchange)
    #        if signature is not None:
    #            apiPath = "{0}?{1}".format(path, queryString)
    #            url="{0}/{1}&signature={2}".format(endPoint, apiPath, signature)
    #            headers = getHeaders(apiKey, exchange)
    #            #logging.info(url)
    #            #logging.info(headers)
    #            response=requests.get(url, headers=headers)
    #            #logging.info(response.status_code)
    #            #if True:
    #            try:
    #                response=requests.get(url, headers=headers)
    #                if response.status_code == 200:
    #                    r=json.loads(response.content)
    #                    #logging.info(json.dumps(r, indent=3))
    #                    #columns = ['time', 'symbol', 'side', 'price', 'origQty', 'executedQty']
    #                    #size = os.get_terminal_size()
    #                    #startLine =  int(size.lines / 4)
    #                    #reverse = False
    #                    lst = sorted(r, key=lambda k: k['time'], reverse=True)
    #                    #logging.info(lst[0])
    #                    #amount = 0.00
    #                    #price = 0.00
    #                    for k,v in enumerate(lst):
    #                        #if v['status'] == "CANCELED":
    #                        if v['status'] == "FILLED":
    #                            histories.append(v)


    #            except:
    #                logging.info("error history call")
    #                pass

    #    if len(histories) > 0:
    #        reverse = False
    #        columns = ['time', 'symbol', 'side', 'price', 'origQty', 'executedQty']
    #        lst = sorted(histories, key=lambda k: k['time'], reverse=True)
    #        for k,v in enumerate(lst):
    #            texts = []
    #            for a,b in enumerate(columns):
    #                value = v[b]
    #                if b == "time":
    #                    value = tstodate(v[b])

    #                if b == "price":
    #                    price = float(value)
    #                    value = redigit(v[b], 8, True)

    #                if b == "origQty":
    #                    value = redigit(v[b], 8, True)

    #                if b == "executedQty":
    #                    amount = float(value)
    #                    value = redigit(v[b], 8, True)

    #                if b == "side":
    #                    if v[b] == "BUY":
    #                        value = colored("BUY ", "green")

    #                if b == "side":
    #                    if v[b] == "SELL":
    #                        value = colored(v[b], "red")

    #                texts.append(str(value))

    #            display = " ".join(texts)
    #            obj = json.dumps({
    #                    "text": display,
    #                    "line": startLine,
    #                    "column": startColumn,
    #                    "length": 0,
    #                    "reverse": reverse
    #                    })

    #            drawLine(obj)
    #            startLine += 1

    #            if k == 0:
    #                x = amount * price
    #                log = "recored: %s" % x
    #                if x > store['lastTradeBUSD']:
    #                    logging.info(log)
    #                    store['lastTradeBUSD'] = x
    #        q.put(store)

#def toggleTrade(q):
#    store = q.get()
#    if store is not None:
#        text = ""
#        if store['tradeSell'] or store['tradeBuy']:
#            bid = green(store['tradeBuy'])
#            ask = green(store['tradeSell'])
#            if store['tradeBuy']:
#                bid = red(store['tradeBuy'])
#            if store['tradeSell']:
#                ask = red(store['tradeSell'])
#
#            text = "Bid: %s Ask: %s" % (bid, ask)
#        else:
#            text = "Trade: Stopped"
#            text = colored(text, 'green')
#
#        obj = json.dumps({
#                "text": text,
#                "line": 4,
#                "column": 30,
#                "length": 20,
#                #"length": len(text),
#                "reverse": True
#                })
#
#        #clearRow(obj)
#        drawLine(obj)

#def marketTicker(q):
#    store = q.get()
#    if store is not None:
#        apiKey = store['key']
#        secretKey = store['secret']
#        endPoint = store['endpoint']
#        timeStamp = int(time.time()*1000)
#        queryObj = {
#                "symbol": "BNBBTC",
#                }
#        queryString = urllib.parse.urlencode(queryObj, doseq=False)
#        apiPath = "ticker/24hr?{0}".format(queryString)
#        url="{0}/{1}".format(endPoint, apiPath)
#        headers = {'User-Agent': Agent('brave'), 'X-MBX-apiKey': apiKey}
#        response=requests.get(url, headers=headers)
#        if response.status_code == 200:
#            r=json.loads(response.content)
#            #logging.info(r)
#
#def reloadHistory(q, limit):
#    store = q.get()
#    if store is not None:
#        apiKey = store['key']
#        secretKey = store['secret']
#        endPoint = store['endpoint']
#        for _, coin in enumerate(store['executeCoins']):
#            timeStamp = int(time.time()*1000)
#            queryObj = {
#                    "symbol": "{}BUSD".format(coin),
#                    "timestamp": timeStamp,
#                    "limit": limit
#                    }
#            queryString = urllib.parse.urlencode(queryObj, doseq=False)
#            signature = hmac.new(bytes(secretKey, 'latin-1'), msg=bytes(queryString, 'latin-1'), digestmod=hashlib.sha256).hexdigest()
#            apiPath = "allOrders?{0}".format(queryString)
#            url="{0}/{1}&signature={2}".format(endPoint, apiPath, signature)
#            headers = {'User-Agent': Agent('brave'), 'X-MBX-apiKey': apiKey}
#            #logging.info(url)
#            #logging.info(headers)
#            response=requests.get(url, headers=headers)
#            #logging.info(response.status_code)
#            if response.status_code == 200:
#                r=json.loads(response.content)
#                #logging.info(json.dumps(r, indent=3))
#                columns = ['time', 'symbol', 'side', 'price', 'origQty', 'executedQty']
#                #size = os.get_terminal_size()
#                #startLine =  int(size.lines / 4)
#                startLine = 11
#                startColumn = 0
#                reverse = False
#                lst = sorted(r, key=lambda k: k['time'], reverse=True)
#                for k,v in enumerate(lst):
#                    if v['status'] == "FILLED":
#                    #if v['status'] == "CANCELED":
#                        texts = []
#                        for a,b in enumerate(columns):
#                            value = v[b]
#                            if b == "time":
#                                value = tstodate(v[b])
#
#                            if b == "price":
#                                value = redigit(v[b], 2, True)
#
#                            if b == "origQty":
#                                value = redigit(v[b], 5, True)
#
#                            if b == "executedQty":
#                                value = redigit(v[b], 5, True)
#
#                            if b == "side":
#                                if v[b] == "BUY":
#                                    value = colored("BUY ", "green")
#
#                            if b == "side":
#                                if v[b] == "SELL":
#                                    value = colored(v[b], "red")
#
#                            texts.append(str(value))
#
#                        display = " ".join(texts)
#                        obj = json.dumps({
#                                "text": display,
#                                "line": startLine,
#                                "column": startColumn,
#                                "length": 0,
#                                "reverse": reverse
#                                })
#
#                        drawLine(obj)
#                        startLine += 1

#def reloadOrderStatus(q):
#    store = q.get()
#    if store is not None:
#        apiKey = store['key']
#        secretKey = store['secret']
#        endPoint = store['endpoint']
#        for _, coin in enumerate(store['executeCoins']):
#            timeStamp = int(time.time()*1000)
#            queryObj = {
#                    "symbol": "{}BUSD".format(coin),
#                    "timestamp": timeStamp
#                    }
#            queryString = urllib.parse.urlencode(queryObj, doseq=False)
#            signature = hmac.new(bytes(secretKey, 'latin-1'), msg=bytes(queryString, 'latin-1'), digestmod=hashlib.sha256).hexdigest()
#            apiPath = "openOrders?{0}".format(queryString)
#            url="{0}/{1}&signature={2}".format(endPoint, apiPath, signature)
#            headers = {'User-Agent': Agent('brave'), 'X-MBX-apiKey': apiKey}
#            response=requests.get(url, headers=headers)
#            if response.status_code == 200:
#                r=json.loads(response.content)
#                #logging.info(json.dumps(r, indent=3))
#                lines = {}
#                startLine = 14
#                side = "BUY"
#                for i, v in enumerate(r):
#                    if v['side'] == "SELL":
#                        side = "SELL"
#                        startLine += 6
#
#                lines['pair'] = startLine
#                startLine += 1
#                lines['amt'] = startLine
#                startLine += 1
#                lines['filled'] = startLine
#                startLine += 1
#                lines['time'] = startLine
#                reverse = True
#                if len(r) > 0:
#                    space = 3
#                    maxLength = 0
#                    nextColumn = 0
#                    for x in lines:
#                        constant = 100
#                        #clearLine(lines[x], constant,  reverse)
#                        #clearLine(lines[x], store['endedBuy'], reverse)
#
#                    valuee = []
#                    for i, v in enumerate(r):
#                        pair = v['symbol']
#                        total = float(v['origQty']) * float(v['price'])
#                        amt = "{0} @ {1}".format(redigit(total, 2, True), redigit(v['price'], 2, True))
#                        filled = (float(v['executedQty'])/100) * float(v['origQty'])
#
#                        t = []
#                        for x in lines:
#                            t.append(x)
#
#                        texts = {}
#                        texts[t[0]] = pair
#                        texts[t[1]] = amt
#                        texts[t[2]] = "{}%".format(redigit(filled, 2))
#                        texts[t[3]] = tstodate(v['time'])
#
#                        array = []
#                        for x in lines:
#                            array.append(texts[x])
#
#                        maxLength = getLength(array)
#                        for x in lines:
#                            obj = json.dumps({
#                                "text": texts[x],
#                                "line": lines[x],
#                                "column": nextColumn,
#                                "length": maxLength,
#                                "reverse": reverse
#                                })
#
#                            drawLine(obj)
#                            #logging.info(obj)
#
#                        nextColumn = nextColumn + maxLength
#                        nextColumn += space
#                        store['endedBuy'] = nextColumn
#
#                else:
#                    for x in lines:
#                        #logging.info(lines[x])
#                        #logging.info(store['endedBuy'])
#                        constant = 100 # constant fix it later
#                        #clearLine(lines[x], constant, reverse)

#def openTradeLimit(obj, q):
#    j = json.loads(obj)
#    pair = j['pair']
#    price = j['price']
#    quantity = j['quantity']
#    side = j['side']
#    timeInForce = j['timeInForce']
#    orderType = j['type']
#    store = q.get()
#    if store is not None:
#        apiKey = store['api']['key']
#        apiSecret = store['api']['secret']
#        endPoint = store['api']['endpoint']
#        path = store['api']['order']
#        timeStamp = int(time.time()*1000)
#        queryObj = {
#            "symbol": pair,
#            "side": side,
#            "type": orderType,
#            "timeInForce": timeInForce,
#            "quantity": quantity,
#            "price": price,
#            "recvWindow": 5000,
#            "timestamp": timeStamp
#        }
#        queryString = urllib.parse.urlencode(queryObj, doseq=False)
#        signature = getSignature(apiSecret, queryString)
#        if signature is not None:
#            url="{0}/{1}".format(endPoint, path, signature)
#            headers = getHeaders(apiKey)
#            data = "{0}&signature={1}".format(queryString, signature)
#            logging.info(data)
#            try:
#                response = requests.post(url, headers=headers, data=data, allow_redirects=True)
#                if response.status_code == 200:
#                    r = json.loads(response.content)
#                else:
#                    responseHandler(response)
#
#            except:
#                logging.info("connection reset openTrade")
#                pass
#
#    q.put(store)

