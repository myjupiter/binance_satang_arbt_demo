import os
import sys
import time
import json
import hmac
import hashlib
import requests
import urllib
#import codecs
import logging
from useragent import Agent
from utils import getLength, redigit, tstodate, getSignature, getHeaders, busdTotal, green, red, pink
from screen import drawLine, clearLine

usleep = lambda x: time.sleep(x/1000000.0)

def marginDraw(js, exchange, q):
    store = q.get()
    obj = json.loads(js)
    if len(obj['coins']) > 0: # bug just happen
        #line = 10
        line = obj['line']
        nextColumn = 0
        size = os.get_terminal_size()
        # screen size bug at the end of border
        columns = size.columns + 1
        rows = size.lines
        reverse = False
        for i,v in enumerate(obj['coins']):
            #clearLine(line, nextColumn)
            line += 1
            obj = {
                    "line": line,
                    "column": nextColumn,
                    "text": v['txt'],
                    "length": size.columns,
                    "reverse": reverse
                    }
            #if line + 40 < rows:
            if True:
                drawLine(json.dumps(obj))
            else:
                break

        # -- draw single line but it over last row
        # -- still bug
        #obj = {
        #        "line": line,
        #        "column": nextColumn,
        #        "text": "",
        #        "length": size.columns,
        #        "reverse": reverse
        #        }
        #drawLine(json.dumps(obj))

        if exchange == "binance":
            store['endBuyBinance'] = line + 1
            x = line + 1
            obj = {
                    "line": x,
                    "column": nextColumn,
                    "text": "",
                    "length": size.columns,
                    "reverse": reverse
                    }
            drawLine(json.dumps(obj))

    q.put(store)

def blockDraw(obj, combine=False):
    j = json.loads(obj)
    lines = j['lines']
    nextColumn = j['nextColumn']
    space = j['space']
    lst = j['lst']
    reverse = j['reverse']

    t = []
    for x in lines:
        t.append(x)

    texts = {}
    for i,v in enumerate(lst):
        texts[t[i]] = v

    array = []
    allLength = 0
    for x in lines:
        array.append(texts[x])
        allLength += len(array)
    maxLength = getLength(array)
    if combine:
        maxLength = allLength + space

    #size = os.get_terminal_size()
    #fixWidth = 90
    for x in lines:
        #c = size.columns
        #clearLine(x, c)
        #time.sleep(1)
        #clearLine(x, fixWidth)

        obj = json.dumps({
                "text": texts[x],
                "line": lines[x],
                "column": nextColumn,
                "length": maxLength,
                "reverse": reverse
                })

        drawLine(obj)

    nextColumn = nextColumn + maxLength
    nextColumn += space
    return nextColumn

#def displayBids(obj, q, store):
#    j = json.loads(obj)
#    limit = j['limit']
#    exchange = j['exchange']
#    const = j['const']
#    #statistic = j['statistic']
#    statistic = False
#
#    apiKey = store[exchange]['key']
#    apiSecret = store[exchange]['secret']
#    endPoint = store[exchange]['endpoint']
#    path = store[exchange]['bidPath']
#    if store['monitorCoins'] is not None:
#        try:
#            for k,coin in enumerate(store['monitorCoins']):
#                endColumn = "endColumn_%s_%s" % (exchange, coin.lower())
#                start = ((9/const) * (const * k)) + (4*const)
#                symbol = "{}BUSD".format(coin) # binance
#                #symbol = "{}EUR".format(coin) # euro
#                if exchange == "satang":
#                    symbol = "%s_thb" % coin.lower()
#
#                queryObj = {
#                    "symbol": symbol,
#                    "limit": limit
#                }
#                queryString = urllib.parse.urlencode(queryObj, doseq=False)
#                apiPath = "{0}?{1}".format(path, queryString)
#                url="{0}/{1}".format(endPoint, apiPath)
#                headers = {'User-Agent': Agent('brave')}
#                getResp = requests.get(url, headers=headers)
#                if getResp.status_code == 200:
#                    r = json.loads(getResp.content)
#                    # store asks
#                    asks = "asks_%s_%s" % (exchange, coin.lower())
#                    store[asks] = r['asks']
#                    # do normal procedure
#                    if statistic:
#                        reverse = True
#                        text = "{0} {1}".format(exchange.upper(), coin)
#                        obj = json.dumps({
#                                "text": text,
#                                "line": start,
#                                "column": 0,
#                                "length": len(text),
#                                "reverse": reverse
#                                })
#
#                        drawLine(obj)
#
#                        space = 3
#                        maxLength = 0
#                        nextColumn = 0
#
#                        lines = {}
#                        lst = ['rate', 'amount', 'total']
#                        for v in lst:
#                            start += 1
#                            lines[v] = start
#
#                        store['vBids'] = start
#                        for x in lines:
#                            clearLine(lines[x], store[endColumn], reverse)
#                    for i,bid in enumerate(r['bids']):
#                        if i > store['showLimit']:
#                            break
#                        rate = list(bid)[0]
#                        if statistic:
#                            amount = list(bid)[1]
#                            total = float("{:.8f}".format( float(rate) * float(amount) ))
#
#                            reAmount = redigit(amount, 6, True)
#                            reRate = redigit(rate, 6, True)
#                            reTotal = redigit(total, 8, True)
#
#                            lst = [reRate, reAmount, reTotal]
#                            obj = {
#                                    "lines": lines,
#                                    "nextColumn": nextColumn,
#                                    "space": space,
#                                    "lst": lst,
#                                    "reverse": reverse
#                                    }
#                            nextColumn = blockDraw(json.dumps(obj))
#
#                            store[endColumn] = nextColumn
#                        if i == 0:
#                            lastPrice = "lastPrice_%s_%s" % (exchange, coin.lower())
#                            store[lastPrice] = rate
#                    bids = "bids_%s_%s" % (exchange, coin.lower())
#                    store[bids] = r['bids']
#                    q.put(store)
#
#                time.sleep(0.1)
#        except:
#            pass
#
#
