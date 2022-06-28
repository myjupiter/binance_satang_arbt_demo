import os
import time
import logging
import json
from threading import Thread
from utils import digitalClock, initialValues, binanceNetwork, satangNetwork, k2faCalc
from screen import preLoad
from commands import commandStructure, commandValid, commandExecute

from binance import binanceWallet, exchangeInfoBinance, binanceBids, binanceHist, cancelBuy, processTrades

from satang import satangWallet, satangBuy, satangBids, exchangeInfoSatang, satangConfig, satangHist, satangCancelBuy

from busd import busdRate
from thb import thbRate
from watches import marginWatchBinance, marginWatchSatang

class displayClock(Thread):
    def __init__(self, delay, q):
        Thread.__init__(self)
        self.running = True
        self.delay = delay
        self.q = q

    def run(self):
        while self.running:
            digitalClock(self.q)
            time.sleep(self.delay)

    def stop(self):
        self.running = False

class initialValuesTask(Thread):
    def __init__(self, q):
        Thread.__init__(self)
        self.running = True
        self.q = q

    def run(self):
        if self.running:
            initialValues(self.q)

    def stop(self):
        self.running = False

class binanceHistThread(Thread):
    def __init__(self, delay, q):
        Thread.__init__(self)
        self.running = True
        self.delay = delay
        self.q = q

    def run(self):
        while self.running:
            binanceHist(self.q)
            time.sleep(self.delay)

    def stop(self):
        self.running = False

#class binanceStockThread(Thread):
#    def __init__(self, delay, q):
#        Thread.__init__(self)
#        self.running = True
#        self.delay = delay
#        self.q = q
#
#    def run(self):
#        while self.running:
#            q = self.q
#            store = q.get()
#            if store is not None:
#                if not store['bncheck']:
#                    if len(store['actionCoinsBinance']) == len(store['pullingsBinance']) and len(store['pullingsBinance']) > 0:
#                        if not store['homePause']:
#                            time.sleep(1)
#                            store['bncheck'] = True
#                            time.sleep(1)
#                            stockCheckProcess(self.q)
#            q.put(store)
#            time.sleep(self.delay)
#
#    def stop(self):
#        self.running = False

class satangBuyThread(Thread):
    def __init__(self, delay, q):
        Thread.__init__(self)
        self.running = True
        self.delay = delay
        self.q = q

    def run(self):
        while self.running:
            satangBuy(self.q)
            time.sleep(self.delay)

    def stop(self):
        self.running = False

class satangHistThread(Thread):
    def __init__(self, delay, q):
        Thread.__init__(self)
        self.running = True
        self.delay = delay
        self.q = q

    def run(self):
        while self.running:
            satangHist(self.q)
            time.sleep(self.delay)

    def stop(self):
        self.running = False

class processTradesThread(Thread):
    def __init__(self, delay, q):
        Thread.__init__(self)
        self.running = True
        self.delay = delay
        self.q = q

    def run(self):
        while self.running:
            processTrades(self.q)
            time.sleep(self.delay)

    def stop(self):
        self.running = False

class binanceMarginThread(Thread):
    def __init__(self, delay, q):
        Thread.__init__(self)
        self.running = True
        self.delay = delay
        self.q = q

    def run(self):
        while self.running:
            marginWatchBinance(self.q)
            time.sleep(self.delay)

    def stop(self):
        self.running = False

class satangMarginThread(Thread):
    def __init__(self, delay, q):
        Thread.__init__(self)
        self.running = True
        self.delay = delay
        self.q = q

    def run(self):
        while self.running:
            marginWatchSatang(self.q)
            time.sleep(self.delay)

    def stop(self):
        self.running = False

class satangMarketsThread(Thread):
    def __init__(self, delay, q, limit):
        Thread.__init__(self)
        self.running = True
        self.limit = limit
        self.delay = delay
        self.q = q

    def run(self):
        while self.running:
            satangBids(self.limit, self.q)
            time.sleep(self.delay)

    def stop(self):
        self.running = False

class k2faThread(Thread):
    def __init__(self, delay, q):
        Thread.__init__(self)
        self.running = True
        self.delay = delay
        self.q = q

    def run(self):
        while self.running:
            k2faCalc(self.q)
            time.sleep(self.delay)

    def stop(self):
        self.running = False

class exchangeInfoBinanceThread(Thread):
    def __init__(self, delay, q):
        Thread.__init__(self)
        self.delay = delay
        self.running = True
        self.q = q

    def run(self):
        while self.running:
            exchangeInfoBinance(self.q)
            time.sleep(self.delay)

    def stop(self):
        self.running = False

class satangNetworkThread(Thread):
    def __init__(self, delay, q):
        Thread.__init__(self)
        self.delay = delay
        self.running = True
        self.q = q

    def run(self):
        while self.running:
            satangNetwork(self.q)
            time.sleep(self.delay)

    def stop(self):
        self.running = False

class binanceNetworkThread(Thread):
    def __init__(self, delay, q):
        Thread.__init__(self)
        self.delay = delay
        self.running = True
        self.q = q

    def run(self):
        while self.running:
            binanceNetwork(self.q)
            time.sleep(self.delay)

    def stop(self):
        self.running = False

class exchangeInfoSatangThread(Thread):
    def __init__(self, delay, q):
        Thread.__init__(self)
        self.delay = delay
        self.running = True
        self.q = q

    def run(self):
        while self.running:
            exchangeInfoSatang(self.q)
            time.sleep(self.delay)

    def stop(self):
        self.running = False

class cancelBuyThread(Thread):
    def __init__(self, delay, q):
        Thread.__init__(self)
        self.delay = delay
        self.running = True
        self.q = q

    def run(self):
        while self.running:
            cancelBuy(self.q)
            time.sleep(self.delay)

    def stop(self):
        self.running = False

class satangCancelBuyThread(Thread):
    def __init__(self, delay, q):
        Thread.__init__(self)
        self.delay = delay
        self.running = True
        self.q = q

    def run(self):
        while self.running:
            satangCancelBuy(self.q)
            time.sleep(self.delay)

    def stop(self):
        self.running = False

class satangWalletThread(Thread):
    def __init__(self, delay, q):
        Thread.__init__(self)
        self.delay = delay
        self.running = True
        self.q = q

    def run(self):
        while self.running:
            satangWallet(self.q)
            time.sleep(self.delay)

    def stop(self):
        self.running = False

class satangConfigThread(Thread):
    def __init__(self, delay, q):
        Thread.__init__(self)
        self.running = True
        self.delay = delay
        self.q = q

    def run(self):
        while self.running:
            satangConfig(self.q)
            time.sleep(self.delay)

    def stop(self):
        self.running = False

class binanceWalletThread(Thread):
    def __init__(self, delay, q):
        Thread.__init__(self)
        self.delay = delay
        self.running = True
        self.q = q

    def run(self):
        while self.running:
            binanceWallet(self.q)
            time.sleep(self.delay)

    def stop(self):
        self.running = False

class binanceMarketsThread(Thread):
    def __init__(self, delay, q, limit):
        Thread.__init__(self)
        self.running = True
        self.limit = limit
        self.delay = delay
        self.q = q

    def run(self):
        while self.running:
            binanceBids(self.limit, self.q)
            time.sleep(self.delay)

    def stop(self):
        self.running = False

class displayBinanceHist(Thread):
    def __init__(self, delay, q, limit):
        Thread.__init__(self)
        self.running = True
        self.delay = delay
        self.q = q
        self.limit = limit

    def run(self):
        while self.running:
            binanceHistory(self.q, self.limit)
            time.sleep(self.delay)

    def stop(self):
        self.running = False

class readKeyboardInput(Thread):
    def __init__(self, q):
        Thread.__init__(self)
        self.running = True
        self.q = q

    def commandHandler(self):
        text = "invalid"
        preLoad(1,10, text, True)
        if commandValid(self.command):
            text = "valid"
            commandExecute(self.command, self.q)

        #print('.', end='', flush=True)
        preLoad(1,10, text, False)
        preLoad(2,0, self.command, True)
        print("\033[%d;%dH" % (1, 0))

    def run(self):
        text = "Please wait..."
        preLoad(0,0, text, True)
        print("Ready.")
        q = self.q
        store = q.get()
        if store is not None:
            while self.running:
                self.command = input()
                if len(self.command) > 0:
                    if self.command == "exit":
                        logging.info("command exit received")
                        self.stop()
                        #if store['tradeBuy']:
                        #    print('\nPlease "stop buy" trade first\n')
                        #else:
                    #elif self.command == "reload":
                    #    print(chr(27) + "[2J")
                    else:
                        self.commandHandler()

                else:
                    print("\033[%d;%dH" % (1, 0))
                time.sleep(0.01)

    def stop(self):
        self.running = False
        #logging.info(self.running)
        '''
        1. check to see if no selling order
        2. send command to stop buying
        3. where there are no opening order
        4. then exit program
        '''
        os.system("clear")
        os._exit(1)

class busdRateThread(Thread):
    def __init__(self, delay, q):
        Thread.__init__(self)
        self.delay = delay
        self.running = True
        self.q = q

    def run(self):
        while self.running:
            busdRate(self.delay, self.q)
            time.sleep(self.delay)

    def stop(self):
        self.running = False

class thbRateThread(Thread):
    def __init__(self, delay, q):
        Thread.__init__(self)
        self.delay = delay
        self.running = True
        self.q = q

    def run(self):
        while self.running:
            thbRate(self.delay, self.q)
            time.sleep(self.delay)

    def stop(self):
        self.running = False

#class toggleTradeTask(Thread):
#    def __init__(self, delay, q):
#        Thread.__init__(self)
#        self.delay = delay
#        self.running = True
#        self.q = q
#
#    def run(self):
#        while self.running:
#            toggleTrade(self.q)
#            time.sleep(self.delay)
#
#    def stop(self):
#        self.running = False

#class reloadHistoryTask(Thread):
#    def __init__(self, delay, q, limit):
#        Thread.__init__(self)
#        self.delay = delay
#        self.running = True
#        self.q = q
#        self.limit = limit
#
#    def run(self):
#        while self.running:
#            reloadHistory(self.q, self.limit)
#            time.sleep(self.delay)
#
#    def stop(self):
#        self.running = False
#
#class reloadOrderTask(Thread):
#    def __init__(self, delay, q):
#        Thread.__init__(self)
#        self.delay = delay
#        self.running = True
#        self.q = q
#
#    def run(self):
#        while self.running:
#            reloadOrderStatus(self.q)
#            time.sleep(self.delay)
#
#    def stop(self):
#        self.running = False

#class reloadBalanceTask(Thread):
#    def __init__(self, delay, q):
#        Thread.__init__(self)
#        self.delay = delay
#        self.running = True
#        self.q = q
#
#    def run(self):
#        while self.running:
#            reloadBalances(self.q)
#            time.sleep(self.delay)
#
#    def stop(self):
#        self.running = False
#
