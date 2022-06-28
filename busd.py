import os
import sys
import time
import json
import requests
import logging
from useragent import Agent
from screen import drawLine, clearLine
from utils import getLength

endpoint = "https://www.binance.com/gateway-api/v2/public/ocbs/fiat-channel-gateway/get-quotation?channelCode=card&cryptoAsset=BUSD&fiatCode="

def busdRate(delay, q):
    headers = {'User-Agent': Agent('brave')}
    store = q.get()
    if store is not None:
        #logging.info(store['busd'])
        rates = store['rates'].split(",")
        reverse = True
        nextColumn = 20
        space = 3

        #size = os.get_terminal_size()
        #start = size.lines - 5
        start = 1

        lines = {}
        start += 1
        lines['label'] = start
        start += 1
        lines['rate'] = start

        for a,b in enumerate(rates):
            endColumn = "endColumn_busd_%s" % (b.lower())
            for x in lines:
                clearLine(lines[x], store[endColumn], reverse)

            url = "{0}{1}".format(endpoint, b)
            try:
                response=requests.get(url, headers=headers)
                if response.status_code == 200:
                    r = json.loads(response.content)
                    if r['success'] == True:
                        #logging.info(r['data']['price'])

                        rate = r['data']['price']
                        reRate = "{:,.8f}".format(float(rate))
                        label = "BUSD_{}".format(b)

                        t = []
                        for x in lines:
                            t.append(x)

                        texts = {}
                        texts[t[0]] = label
                        texts[t[1]] = reRate

                        array = [label, reRate]
                        maxLength = getLength(array)
                        for x in lines:
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
                        store[endColumn] = nextColumn
                        endCheck = "endColumn_busd_%s" % rates[-1].lower()
                        if store[endCheck] > 0:
                            for x in rates:
                                end = "endColumn_busd_%s" % x.lower()
                                store[end]= 0

                        busd = "busd_%s" % b.lower()
                        store[busd] = rate
                        q.put(store)

            except:
                pass
        time.sleep(1)


