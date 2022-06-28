import os
import re
import time
import logging
import json
import random
import urllib
import requests
from useragent import Agent
from common import blockDraw, marginDraw
from utils import drawLine, averageDST, redigit, tf, findBid, colors, calcAmount, getCoinBUSD, getMarginBinance, getMarginSatang, calcTicketSizeBinance, calcTicketSizeSatang, calcQuotePrecisionSatang

#from binance import processTrades
#from satang import satangProcess

def marginWatchBinance(q):
    store = q.get()
    line = store['endWallet']
    if store['pairDefinedBinance'] and store['pairDefinedSatang']:
        wsCoins = store['actionCoinsBinance']
        #log = "action pairs: %s line: %s" % (len(wsCoins), line)
        #logging.info(log)
        if len(wsCoins) > 0:
            if len(wsCoins) == len(store['definedCoinsBinance']):
                if not store['homePause']:
                    showCoins = []
                    for _, coin in enumerate(wsCoins):
                        busdPair = "%sBUSD" % coin
                        thbPair = "%s_THB" % coin

                        coinTxt = colors(str(coin), 'YELLOW')
                        trans = "fee_%s_binance" % (coin)
                        if store[trans] is not None:
                            #if coin == "FLOW":
                            #    logging.info(store[trans])
                            withdraw = store[trans]['withdraw']
                            deposit = store[trans]['deposit']
                            if not withdraw or not deposit:
                                coinTxt = colors(str(coin), 'RED')

                        gMargin = json.loads(getMarginBinance(coin, q))

                        if gMargin['buyAmt'] is not None:

                            sellAmt = gMargin['sellAmt']
                            margin = gMargin['busd']

                            satangBuyPosition = store['satangBuyPosition']

                            buyPrice = gMargin['buyPrice']
                            buyPrice = calcTicketSizeBinance(float(buyPrice), busdPair, q)

                            sellPrice = gMargin['sellPrice']
                            sellPrice = calcTicketSizeSatang(float(sellPrice), thbPair, q)

                            busdTHB = float(sellPrice) / float(store['busd_thb'])
                            busdTHB = calcTicketSizeSatang(float(busdTHB), thbPair, q)

                            thbMargin = gMargin['thb']
                            buyAmt = gMargin['buyAmt']
                            fee = gMargin['fee']
                            openAmt = gMargin['openAmt']
                            percent = gMargin['percent']

                            thbTxt = "T"
                            if float(openAmt) < float(sellAmt):
                                thbTxt = colors(str("T"), "RED")

                            sCoin = {}
                            sCoin['margin'] = margin
                            sCoin['coin'] = coin
                            sCoin['buyPrice'] = buyPrice
                            sCoin['sellPrice'] = sellPrice
                            sCoin['percent'] = percent
                            sCoin['fee'] = fee

                            buyPriceTxt = colors(str(buyPrice), 'MAGENTA')
                            sellPriceTxt = colors(str(sellPrice), 'CYAN')
                            busdTHBTxt = colors(str(busdTHB), 'MAGENTA')

                            minCoin = gMargin['buyAmt']
                            sCoin['minCoin'] = minCoin
                            n = 0.00
                            if float(margin) > n:
                                margin = colors(str(margin), 'GREEN')
                                sCoin['color'] = 'G'
                            else:
                                margin = colors(str(margin), 'RED')
                                sCoin['color'] = 'R'

                            n = 0.00
                            if float(percent) > n:
                                percentTxt = colors(str(percent), 'GREEN')
                            else:
                                percentTxt = colors(str(percent), 'RED')

                            buyAmtTxt = colors(str(buyAmt), 'MAGENTA')
                            sellAmtTxt = str(sellAmt)
                            #sellAmtTxt = colors(str(sellAmt), 'BLUE')
                            feeTxt = colors(str(fee), 'YELLOW')
                            openAmtTxt = colors(str(openAmt), 'MAGENTA')

                            buyTxt = "[%s][%s][%s][%s" % (thbTxt, buyPriceTxt, coinTxt, busdTHBTxt)

                            cut = "%s %s][%s %s %s][%s][%s %s %s%%]" % (buyTxt, sellPriceTxt, buyAmtTxt, feeTxt, sellAmtTxt, openAmtTxt, margin, thbMargin, percentTxt)
                            sCoin['txt'] = cut
                            if float(percent) > store['showPercent']:
                                showCoins.append(sCoin)

                    if len(showCoins) > 0:
                        srt_coins = sorted(showCoins, key=lambda k: k['percent'], reverse=False)
                        fees = []
                        for coin in srt_coins:
                            if float(coin['fee']) == 0:
                                fees.append(0)

                        #logging.info(fees)
                        #logging.info(srt_coins)
                        #trades = []
                        #limit = len(srt_coins)
                        #limit = 1
                        #lookColors = ["G", "Y"]
                        #for i in range(0, limit):
                        #    if srt_coins[i]['color'] in lookColors:
                        #        buyPrice = srt_coins[i]['buyPrice']
                        #        pair = srt_coins[i]['coin']
                        #        minCoin = srt_coins[i]['minCoin']
                        #        x = {
                        #                "pair": pair,
                        #                "buyPrice": buyPrice,
                        #                'minCoin': minCoin
                        #                }
                        #        trades.append(x)

                        #store['trades'] = trades
                        #logging.info(json.dumps(trades, indent=3))

                        #if True:
                        if len(fees) == 0:
                            obj = json.dumps({
                                    "line": line,
                                    "coins": srt_coins
                                    })
                            exchange = "binance"
                            marginDraw(obj, exchange, q)

        q.put(store)

def marginWatchSatang(q):
    store = q.get()
    line = store['endBuyBinance']
    #if True:
    if line > 0:
        if store['pairDefinedBinance'] and store['pairDefinedSatang']:
            wsCoins = store['actionCoinsBinance']
            #log = "satang action pairs: %s line: %s" % (len(wsCoins), line)
            #logging.info(log)
            if len(wsCoins) > 0:
                if len(wsCoins) == len(store['definedCoinsBinance']):
                    if not store['homePause']:
                        showCoins = []
                        for _, coin in enumerate(wsCoins):
                            thbPair = "%s_THB" % coin
                            gMargin = json.loads(getMarginSatang(coin, q))
                            sCoin = {}

                            coinTxt = colors(str(coin), 'YELLOW')
                            sCoin['widthdrawal'] = True
                            trans = "fee_%s_satang" % (coin)
                            if store[trans] is not None:
                                withdraw = store[trans]['withdraw']
                                deposit = store[trans]['deposit']
                                if not withdraw or not deposit:
                                    coinTxt = colors(str(coin), 'RED')
                                    sCoin['widthdrawal'] = False

                            if gMargin['buyAmt'] is not None:

                                buyAmt = gMargin['buyAmt']
                                margin = gMargin['busd']

                                satangSellPosition = store['satangSellPosition']
                                #asks = "asks_%s" % thbPair.lower()
                                #bp = list(store[asks][satangSellPosition])[1]
                                ssp = "satangSellPosition_%s" % thbPair.lower()
                                busdTxt = "B"
                                sCoin['enough'] = True
                                # only consider first 3 order
                                if store[ssp] > 3:
                                    busdTxt = colors(str("B"), "RED")
                                    sCoin['enough'] = False

                                buyPrice = gMargin['buyPrice']
                                sellPrice = gMargin['sellPrice']
                                sellPriceTxt = colors(str(sellPrice), 'CYAN')

                                busdTHB = float(sellPrice) * float(store['busd_thb'])
                                busdTHB = calcTicketSizeSatang(float(busdTHB), thbPair, q)

                                openAmt = gMargin['openAmt']
                                #openAmt = "+"

                                openAmtTxt = colors(str(openAmt), 'MAGENTA')

                                thbMargin = gMargin['thb']
                                sellAmt = gMargin['sellAmt']
                                fee = gMargin['fee']
                                percent = gMargin['percent']

                                sCoin['margin'] = margin
                                sCoin['buyPair'] = "%s_THB" % (coin)
                                sCoin['buyPrice'] = buyPrice
                                sCoin['buyAmt'] = buyAmt
                                sCoin['openAmt'] = openAmt
                                sCoin['sellPair'] = "%sBUSD" % coin
                                sCoin['sellPrice'] = sellPrice
                                sCoin['percent'] = percent
                                sCoin['fee'] = fee

                                buyPriceTxt = colors(str(buyPrice), 'MAGENTA')
                                busdTHBTxt = colors(str(busdTHB), 'MAGENTA')
                                buyAmtTxt = colors(str(buyAmt), 'MAGENTA')
                                sellAmtTxt = str(sellAmt)
                                #sellAmtTxt = colors(str(sellAmt), 'BLUE')
                                feeTxt = colors(str(fee), 'YELLOW')

                                n = 0.00
                                if float(margin) > n:
                                    margin = colors(str(margin), 'GREEN')
                                    sCoin['color'] = True
                                else:
                                    margin = colors(str(margin), 'RED')
                                    sCoin['color'] = False

                                n = 0.00
                                if float(percent) > n:
                                    percentTxt = colors(str(percent), 'GREEN')
                                else:
                                    percentTxt = colors(str(percent), 'RED')

                                #thirdPair = "BUSD_THB"
                                #sCoin['thirdPair'] = thirdPair
                                #x = {
                                #        "pair": thirdPair,
                                #        "buy": True,
                                #        "exchange": "satang"
                                #        }
                                #thirdPrice = getCoinBUSD(json.dumps(x), q)
                                #sCoin['thirdPrice'] = thirdPrice

                                buyTxt = "[%s][%s][%s][%s" % (busdTxt, buyPriceTxt, coinTxt, busdTHBTxt)

                                cut = "%s %s][%s %s %s][%s][%s %s %s%%]" % (buyTxt, sellPriceTxt, buyAmtTxt, feeTxt, sellAmtTxt, openAmtTxt, margin, thbMargin, percentTxt)
                                cost = gMargin['cost']
                                costTxt = colors(str(cost), 'YELLOW')
                                profit = gMargin['profit']
                                proTxt = colors(str(profit), 'MAGENTA')

                                busdPro = gMargin['busdPro']
                                busdProTxt = str(busdPro)
                                #busdProTxt = colors(str(busdPro), "BLUE")
                                ebusd = gMargin['ebusd']
                                sCoin['ebusd'] = ebusd
                                ebusdTxt = colors(str(ebusd), "YELLOW")

                                backConv = gMargin['backConv']
                                backConvTxt = colors(str(backConv), "RED")
                                sCoin['backConv'] = False
                                constant = store['thbMinMargin']
                                if cost < (backConv - constant):
                                    backConvTxt = colors(str(backConv), "GREEN")
                                    sCoin['backConv'] = True

                                coinAva = "satang_ava_%s" % coin
                                coinCap = "satang_cap_%s" % coin
                                coinAvaTxt = ""
                                coinCapTxt = ""
                                if store[coinAva] is not None:
                                    coinCapTxt = colors(str(store[coinCap]), "RED")
                                    coinAvaTxt = colors(str(store[coinAva]), "MAGENTA")

                                extend = "%s[%s][%s][%s][%s][%s][%s/%s]" % (cut, costTxt, proTxt, busdProTxt, ebusdTxt, backConvTxt, coinAvaTxt, coinCapTxt)
                                sCoin['txt'] = extend
                                if float(percent) > store['showPercent']:
                                    showCoins.append(sCoin)

                        if len(showCoins) > 0:
                            srt_coins = sorted(showCoins, key=lambda k: k['percent'], reverse=True)
                            #logging.info(srt_coins)
                            fees = []
                            for coin in srt_coins:
                                if float(coin['fee']) == 0.0:
                                    fees.append(0)

                            trades = []
                            #percent = 0.30
                            percent = store['percentMargin']
                            #logging.info(srt_coins[0])
                            if store['run']:
                                for v in srt_coins:
                                    #if True:
                                    if v['color'] and v['backConv'] and v['enough'] and v['widthdrawal'] and float(v['percent']) > float(percent):
                                        buyPair = v['buyPair']
                                        buyPrice = v['buyPrice']

                                        sellPair = v['sellPair']
                                        sellPrice = v['sellPrice']

                                        openAmt = v['openAmt']

                                        coin = buyPair.split("_")[0]

                                        trade = "trade_%s_satang" % coin
                                        if store[trade]:
                                            timeStamp = int(time.time()*1000)
                                            if len(store['trades']) < 1:
                                                x = {
                                                        "coin": coin,
                                                        "buy": {
                                                            "price": buyPrice,
                                                            "pair": buyPair,
                                                            "openAmt": openAmt
                                                            },
                                                        "sell": {
                                                            "price": sellPrice,
                                                            "pair": sellPair
                                                            },
                                                        "ebusd": v['ebusd'],
                                                        "source": "satang",
                                                        "status": "queue",
                                                        "ts": timeStamp
                                                    }
                                                trades.append(x)
                                            break # for this time limit to single coin at the time

                            if len(trades) > 0:
                                #logging.info(trades)
                                thb = tf(store['thbOnly'], 2)
                                if float(thb) > store['thbMin']:
                                    store['trades'] = trades

                            #if True:
                            if len(fees) == 0: # error network fee zero protection
                                obj = json.dumps({
                                        "line": line,
                                        "coins": srt_coins
                                        })
                                exchange = "satang"
                                marginDraw(obj, exchange, q)

            q.put(store)
