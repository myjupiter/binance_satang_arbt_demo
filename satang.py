import os
import sys
import time
from datetime import datetime
import json
import requests
import urllib
#from termcolor import colored
import logging
import multiprocessing
from common import blockDraw
from utils import getLength, redigit, tstodate, getSignature, getHeaders, busdTotal, green, red, getCoinBUSD, enoughToSell, getStepSize, responseHandler, calcLotSize, getTicketSize, tf, calcTicketSizeSatang, getBaseAssetPrecisionSatang, calcFee, quoteAssets, binanceWd
from useragent import Agent
from screen import drawLine, clearLine
from ws import MarketUpdateSecond

usleep = lambda x: time.sleep(x/1000000.0)

#def satangProcess(q):
#    store = q.get()
#    logging.info(json.dumps(store['trades'], indent=3))
#    if store['run']:
#        # check Satang buy tag
#        f = open("/tmp/satang_process.json","r")
#        x = f.read()
#        f.close()
#        p = json.loads(x)
#        buyed = p['buyed']
#        if not buyed:
#            logging.info("process Satang buy")

def getLastTs(orders):
    last = 0
    tf ='%Y-%m-%d %H:%M:%S'
    for l in orders:
        if l['status'] == "completed":
            ls = l['created_at']
            #d = datetime.fromisoformat(ls[:20] + '+00:00')
            d = datetime.fromisoformat(ls[:19])
            d.strftime(tf)
            #d.strftime("%%s")
            x = time.mktime(time.strptime(str(d), tf))
            last = int(x)
            break
    return last

def cancelBuy(pair, q):
    logging.info("satang canceling buy")
    store = q.get()
    if store is not None:
        payload = {
                "pair": pair.lower()
                }
        queryString = urllib.parse.urlencode(payload, True)
        apiKey = store['keySatang']['key']
        apiSecret = store['keySatang']['secret']
        endPoint = store['apiSatang']['endpoint']
        path = store['apiSatang']['orders']

        exchange = "satang"
        signature = getSignature(apiSecret, queryString, exchange)
        if signature is not None:
            url = "{}/{}/all".format(endPoint, path)
            logging.info(url)
            try:
                headers = {}
                headers['Authorization'] = "TDAX-API {0}".format(apiKey)
                headers['Signature'] = signature
                response = requests.delete(url, headers=headers, json=payload)
                logging.info(response)
                logging.info(response.content)
                if response.status_code == 200:
                    store['trades'] = []
                    store['run'] = True

            except Exception as e:
                logging.info(e)

    q.put(store)

def satangCancelBuy(q):
    logging.info("satang cancel check")
    store = q.get()
    if store is not None:
        #pair = "busd_thb"
        #cancelBuy(pair, q)
        second = 60*20
        logging.info(store['trades'])
        if len(store['trades']) > 0:
            for s in store['trades']:
                if s['source'] == "satang":
                    pair = s['buy']['pair']
                    openTs = int(s['ts'])
                    currentTs = int(time.time()*1000)
                    diff = currentTs - openTs
                    logging.info(f'openTs:{openTs} currentTs:{currentTs} diff:{diff}')
                    if int((currentTs - openTs) / 1000) > second:
                        if s['status'] == "buy":
                            logging.info("process cancel buy")
                            #cancelBuy(pair, q)

                time.sleep(1)

    q.put(store)

def satangHist(q):
    #logging.info("satangBuyed History")
    store = q.get()
    if store is not None:
        exc = []
        apiKey = store['keySatang']['key']
        apiSecret = store['keySatang']['secret']
        endPoint = store['apiSatang']['endpoint']
        p = store['satangWallets']
        for c in store['coins']:
            xc = c['name'].lower()
            network = c['network']
            ava = float(p[xc]['available_balance'])
            #logging.info(f'{xc} {network} {ava}')
            fee = "fee_%s_satang" % c['name']
            fn = store[fee]
            # bug str float
            minWith = float(fn['min'])
            if xc == "busd":
            #if ava > minWith:
                #logging.info(f'calling for {xc}')
                pair = "%s_thb" % xc
                getVar = {
                        "pair": pair,
                        "limit": 50,
                        "offset": 0,
                        #"status": "open",
                        "side": "buy"
                        }
                queryString = urllib.parse.urlencode(getVar, True)
                payload = {}
                x = urllib.parse.urlencode(payload, True)
                signature = getSignature(apiSecret, x, "satang")
                if signature is not None:
                    apiPath = "orders/user?{0}".format(queryString)
                    url="{0}/{1}".format(endPoint, apiPath)
                    try:
                        headers = {}
                        headers["Authorization"] = "TDAX-API {0}".format(apiKey)
                        headers["Signature"] = signature
                        response=requests.get(url, headers=headers)
                        if response.status_code == 200:
                            r=json.loads(response.content)
                            #logging.info(json.dumps(r, indent=3))
                            if len(r) > 0:
                                ts = getLastTs(r)
                                if ts > 0:
                                    #logging.info(json.dumps(r, indent=3))
                                    lastBuy = "satang_%s_last" % xc
                                    store[lastBuy] = ts
                                    #logging.info(f'{xc} {ts}')

                        else:
                            responseHandler(response)

                    except Exception as e:
                        logging.info(f"connection reset satangHist\n{e}")
                        pass

                time.sleep(0.2)

    q.put(store)

#def sellBusd(q):
#    store = q.get()
#    prices = [0]
#    #trades = sorted(store['trades'], key=lambda k: k['ts'], reverse=True)
#    trades = store['trades']
#    for t in trades:
#        if t['source'] == "satang":
#            prices.append(t['ebusd'])
#    prices = prices.sort()
#    q.put(store)
#    return prices[-1]

#def maxSellBusd(q):
#    store = q.get()
#    busd = 0
#    if store is not None:
#        busd = store['maxBusd']
#    q.put(store)
#    return busd

def removeTrades(busd, q):
    logging.info("remove matched trades")

def processSell(asset, ava, price, q):
    logging.info("sell satang")
    store = q.get()
    if store is not None:
        #amount = float(thb) / float(buyPrice)
        #fee = (store['satangFee']/100) * amount
        #amount = amount - fee
        buyPair = "%s_thb" % asset.lower()
        precision = getBaseAssetPrecisionSatang(buyPair, q)
        amount = tf(ava, precision)
        logging.info(f'amount: {amount} precision: {precision}')
        fee = "fee_%s_satang" % asset
        fn = store[fee]
        minWith = float(fn['min'])
        if float(amount) > minWith:
            timeStamp = int(time.time()*1000)
            payload = {
                    "amount": str(amount),
                    "nonce": timeStamp,
                    "pair": str(buyPair),
                    "price": str(price),
                    "side": "sell",
                    "type": "limit"
                    }
            queryString = urllib.parse.urlencode(payload, True)
            apiKey = store['keySatang']['key']
            apiSecret = store['keySatang']['secret']
            endPoint = store['apiSatang']['endpoint']
            path = store['apiSatang']['orders']

            exchange = "satang"
            signature = getSignature(apiSecret, queryString, exchange)
            if signature is not None:
                url = "{}/{}/".format(endPoint, path)
                logging.info(url)
                try:
                    headers = {}
                    headers['Authorization'] = "TDAX-API {0}".format(apiKey)
                    headers['Signature'] = signature
                    response = requests.post(url, headers=headers, json=payload)
                    if response.status_code == 200:
                        r = json.loads(response.content)
                        logging.info(json.dumps(r, indent=3))
                        if True: # if success open sell order
                            time.sleep(3) #delay for update new BUSD buy bids
                            store['trades'] = []
                            store['run'] = True
                            #if store['loop']:
                            #    store['run'] = True
                    else:
                        responseHandler(response)
                except Exceptions as e:
                    logging.info(f"connection reset processSell\n{e}")
                    pass

    q.put(store)

def processStock(coins, q):
    logging.info("Process stock Satang")
    store = q.get()
    if store is not None:
        #if True:
        if len(store['trades']) > 0:
            trades = sorted(store['trades'], key=lambda k: k['ebusd'], reverse=True)
            maxBUSD = trades[0]['ebusd']
            for c in coins:
                asset = c['asset']
                ava = c['free']
                fee = "fee_%s_satang" % asset
                fn = store[fee]
                #logging.info(fn)
                s = float(fn['fee']) + float(fn['min'])
                if fn['withdraw']:
                    lastBuy = "satang_%s_last" % asset.lower()
                    buyTs = store[lastBuy]
                    depTs = binanceWd(asset, q)
                    if ava > s:
                        #logging.info("amount be able to withdraw")
                        if float(depTs) > float(buyTs):
                            logging.info("checking store['trade']")
                            if asset == "BUSD":
                                sellPrice = maxBUSD
                                logging.info(sellPrice)
                                if float(sellPrice) > 0:
                                    processSell(asset, ava, sellPrice, q)
                                else:
                                    logging.info("sell price eq 0")
                            else:
                                # read source from binance
                                logging.info("others coin than BUSD")

                            # checking for store buffer
                            #lastBuy = "satang_%s_last" % asset.lower()
                            #buyTs = store[lastBuy]
                            #logging.info(f'{buyTs}')
                    #else:
                    #    #logging.info(f'coin: {asset} sum: {s} available: {ava}')
                    #    logging.info(f'coin: {asset} sum: {s} available: {ava} buyTs: {buyTs} depTs: {depTs}')
                else:
                    logging.info(f'{asset} is unable to withdraw')

                #break
                time.sleep(0.1)

    q.put(store)

def satangWallet(q):
    store = q.get()
    if store is not None:
        apiKey = store['keySatang']['key']
        apiSecret = store['keySatang']['secret']
        endPoint = store['apiSatang']['endpoint']
        url="{0}/users/me".format(endPoint)
        #url = store['apiSatang']['profile']
        #timeStamp = int(time.time()*1000)
        payload = ''
        queryString = urllib.parse.urlencode(payload, doseq=False)
        exchange = "satang"
        signature = getSignature(apiSecret, queryString, exchange)
        #logging.info("satang wallet")
        if signature is not None:
            headers = {}
            headers["Authorization"] = "TDAX-API {0}".format(apiKey)
            headers["Signature"] = signature
            try:
                response=requests.get(url, headers=headers)
                if response.status_code == 200:
                    r=json.loads(response.content)
                    store['satangWallets'] = r['wallets']
                    thbAva = float(r['wallets']['thb']['available_balance'])
                    store['thbOnly'] = thbAva
                    if store['thbMax'] < thbAva:
                        store['thbMax'] = thbAva

                    coins = []
                    for c in store['coins']:
                        coin = c['name']
                        x = coin.lower()
                        available = float(r['wallets'][x]['available_balance'])
                        cc = {}
                        cc['asset'] = coin
                        cc['free'] = float(available)
                        coins.append(cc)
                        if c['monitor']:
                            coinAva = "satang_ava_%s" % coin
                            coinCap = "satang_cap_%s" % coin
                            capacity = float(r['limits'][x]['capacity'])
                            quota = float(r['limits'][x]['available'])
                            store[coinAva] = quota
                            store[coinCap] = capacity

                    if len(coins) > 0:
                        processStock(coins, q)
                else:
                    responseHandler(response)

            except Exception as e:
                logging.info("connection reset satangWallet")
                logging.info(e)
                pass

    q.put(store)

def satangConfig(q):
    '''
    https://satangcorp.com/api/configs/web/
    '''
    store = q.get()
    if store is not None:
        #logging.info('satangConfig')
        try:
            url = "https://satangcorp.com/api/configs/web/"
            response=requests.get(url)
            if response.status_code == 200:
                r=json.loads(response.content)
                #logging.info(json.dumps(r, indent=3))
                store['satangConfigs'] = r['networks']['networks']
            else:
                responseHandler(response)
        except Exception as e:
            logging.info(f"connection reset satangConfig\n{e}")
            pass
    q.put(store)

def openOrder(coin, q, buy=False):
    openning = False
    #log = "---check openning: %s\n" % coin
    #logging.info(log)
    store = q.get()
    if store is not None:
        apiKey = store['keySatang']['key']
        apiSecret = store['keySatang']['secret']
        endPoint = store['apiSatang']['endpoint']
        path = store['apiSatang']['orders']
        timeStamp = int(time.time()*1000)
        getVar = {
                "pair": coin.lower(),
                "limit": 10,
                "offset": 0,
                "status": "open",
                "side": "buy"
                }
        queryString = urllib.parse.urlencode(getVar, True)
        payload = {}
        x = urllib.parse.urlencode(payload, True)
        exchange = "satang"
        signature = getSignature(apiSecret, x, exchange)
        #logging.info(signature)
        if signature is not None:
            apiPath = "{0}/user?{1}".format(path, queryString)
            url="{0}/{1}".format(endPoint, apiPath)
            #logging.info(url)
            if True:
            #try:
                headers = {}
                headers["Authorization"] = "TDAX-API {0}".format(apiKey)
                headers["Signature"] = signature
                response=requests.get(url, headers=headers)
                if response.status_code == 200:
                    r=json.loads(response.content)
                    #logging.info(json.dumps(r, indent=3))
                    if len(r) > 0:
                        openning = True
                else:
                    responseHandler(response)
        #    except:
        #        logging.info("connection reset openOrder")
        #        pass

    log = "open check: %s result: %s" % (coin, openning)
    logging.info(log)
    q.put(store)
    return openning

def buyFirst(buyPair, buyPrice, openAmt, q):
    # overwrite for testing purpose
    #buyPair = "XRP_THB"
    #buyPrice = 20.45
    #openAmt = 3000
    #
    store = q.get()
    thb = tf(store['thbOnly'], 2)
    #thb = tf(store['thbAble'], 2)
    #if thb > store['thbOnly']:
    #    thb = tf(store['thbOnly'], 2)

    if float(thb) > store['thbMin']:
        #feeRat = store['satangFee']
        #fee = calcFee(thb, feeRate, 8)
        #remain = calcRemain(thb, fee, 8)

        amount = float(thb) / float(buyPrice)
        fee = (store['satangFee']/100) * amount
        amount = amount - fee
        precision = getBaseAssetPrecisionSatang(buyPair, q)
        amount = tf(amount, precision)
        log = "amount: %s precision: %s open: %s thb: %s" % (amount, precision, openAmt, thb)
        logging.info(log)
        if float(amount) > float(openAmt):
            amount = openAmt

        if float(amount) > 0:
            coinAva = "satang_ava_%s" % buyPair.split("_")[0]
            if float(store[coinAva]) > float(amount):
                log = "buying"
                logging.info(log)
                timeStamp = int(time.time()*1000)
                payload = {
                        "amount": str(amount),
                        "nonce": timeStamp,
                        "pair": str(buyPair.lower()),
                        "price": str(buyPrice),
                        "side": "buy",
                        "type": "limit"
                        }
                queryString = urllib.parse.urlencode(payload, True)

                apiKey = store['keySatang']['key']
                apiSecret = store['keySatang']['secret']
                endPoint = store['apiSatang']['endpoint']
                path = store['apiSatang']['orders']

                exchange = "satang"
                signature = getSignature(apiSecret, queryString, exchange)
                if signature is not None:
                    logging.info(queryString)
                    logging.info(signature)
                    url = "{}/{}/".format(endPoint, path)
                    logging.info(url)
                    headers = {}
                    headers['Authorization'] = "TDAX-API {0}".format(apiKey)
                    headers['Signature'] = signature
                    response = requests.post(url, headers=headers, json=payload)
                    if response.status_code == 200:
                        r = json.loads(response.content)
                        logging.info(json.dumps(r, indent=3))
                        # make Line notification
                        # update store to buyed
                        for i,s in enumerate(store['trades']):
                            if s['buy']['pair'] == buyPair:
                                x = s
                                x['status'] = "buy"
                                store['trades'][i] = x
                    else:
                        logging.info(response.status_code)
                        logging.info(response.content)

    # can not clear memory because binace need to sell and
    # satang need to sell BUSD
    #        else:
    #            # clear trades array in memory
    #            store['trades'] = []
    #    else:
    #        store['trades'] = []
    #else:
    #    store['trades'] = []

    q.put(store)

def satangBuy(q):
    store = q.get()
    if len(store['trades']) > 0:
        #logging.info(json.dumps(store['trades'], indent=3))
        if store['run']:
            for v in store['trades']:
                logging.info(v)
                buyPair = v['buy']['pair']
                buyPrice = v['buy']['price']
                openAmt = v['buy']['openAmt']
                if True:
                #if not openOrder(buyPair, q):
                    log = "buy first pair: %s" % buyPair
                    logging.info(log)
                    buyFirst(buyPair, buyPrice, openAmt, q)
                else:
                    log = "%s openning buy" % buyPair
                    logging.info(log)

                time.sleep(0.1)

            time.sleep(0.1)
            if not store['loop']:
                store['run'] = False
                logging.info("turn off run command")

        #else:
        #    logging.info("command run is not active")
    q.put(store)
    return


def wsCallSecond(sym, q):
    x = MarketUpdateSecond(sym, q)
    x.run()
    time.sleep(0.03)

def satangBids(limit, q):
    #logging.info("recall bids, asks Satang")
    store = q.get()
    if store is not None:
        if len(store['definedCoinsSatang']) > 0:
            pullings = store['pullingsSatang']
            #log = "pulling Second: %s" % len(pullings)
            #logging.info(log)
            processes = []
            for i,sym in enumerate(store['definedCoinsSatang']):
                if sym.lower() not in pullings:
                    #log = "%s %s" % (i, sym.lower())
                    #logging.info(log)
                    s = sym.lower()
                    wsCallSecond(s, q)

                    #pullings.append(sym.lower())
                    #store['pullingsSatang'] = pullings
                    q.put(store)
                    time.sleep(0.01)

            #log = "pulling Second: %s" % len(pullings)
            #logging.info(log)
        else:
            log = "Satang Coins is not defined"
            logging.info(log)

        if store['symbolsSecond'] is not None:
            log = " total second pairs: %s" % len(store['symbolsSecond'])
            #logging.info(log)

    q.put(store)

def exchangeInfoSatang(q):
    logging.info("exchangeInfoSatang")
    store = q.get()
    if store is not None:
        endPoint = store['apiSatang']['endpoint']
        path = store['apiSatang']['infoPath']
        try:
            apiPath = "{0}".format(path)
            url="{0}/v3/{1}".format(endPoint, apiPath)
            headers = {'User-Agent': Agent('brave')}
            getResp = requests.get(url, headers=headers)
            if getResp.status_code == 200:
                r = json.loads(getResp.content)
                #logging.info(json.dumps(r, indent=3))
                store['symbolsSecond'] = r['symbols']
                #logging.info(store['pairDefinedSatang'])
                if not store['pairDefinedSatang']:
                    #logging.info(r['symbols'])
                    pairDefinedSatang(r['symbols'], q)

            elif getResp.status_code == 400:
                logging.info(getResp)
            else:
                logging.info(getResp)
                logging.info("coinPrice get error")
                responseHandler(response)
        except Exception as e:
            logging.info("Satang Info Error")
            logging.info(e)
            pass

    q.put(store)

def pairDefinedSatang(rawSym, q):
    store = q.get()

    watchCoins = []
    for coin in store['coins']:
        if coin['monitor']:
            watchCoins.append(coin['name'])
            trans = "fee_%s_satang" % coin['name']
            posBuy = "satangBuyPosition_%s_thb" % coin['name'].lower()
            posSell = "satangSellPosition_%s_thb" % coin['name'].lower()
            coinAva = "satang_ava_%s" % coin['name']
            coinCap = "satang_cap_%s" % coin['name']
            store[coinAva] = None
            store[coinCap] = None
            store[trans] = None
            store[posBuy] = 0
            store[posSell] = 0

        trade = "trade_%s_satang" % coin['name']
        if coin['trade']:
            store[trade] = True
        else:
            store[trade] = False

    fixCoin = "THB"
    symbols = quoteAssets(rawSym, watchCoins, fixCoin)

    coins = []
    # special
    coin = {}
    coin['pair'] = "busd_thb"
    coins.append(coin)
    # --end
    for i,s in enumerate(symbols):
        coin = {}
        pair = "%s_%s" % (s['baseAsset'], fixCoin)
        coin['pair'] = pair.lower()
        coins.append(coin)

    log = "defined pairs Satang: %s" % len(coins)
    logging.info(log)
    if len(coins) > 0:
        c = []
        for a in coins:
            bidName = "bids_%s" % a['pair']
            store[bidName] = None
            askName = "asks_%s" % a['pair']
            store[askName] = None
            c.append(a['pair'])

        store['pairDefinedSatang'] = True
        store['definedCoinsSatang'] = c
        #store['actionCoinsSatang'] = watchCoins
    q.put(store)
    time.sleep(5)
    return



'''
/tmp/ltc.json
{
        "buySide": "satang",
        "sellPrice": 246.8,
        "busd": 33.4,
        "finish": false
        }

{
        "buySide": "binance",
        "sellPrice": 8500,
        "busd": false,
        "finish": true
        }
'''
