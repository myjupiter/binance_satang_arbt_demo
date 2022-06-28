#!/usr/bin/python3
import os
import time
import logging
import json
from screen import drawLine, preLoad
from queue import Queue
from threads import displayClock, initialValuesTask, binanceWalletThread, satangWalletThread, readKeyboardInput, busdRateThread, thbRateThread, binanceMarginThread, exchangeInfoBinanceThread, exchangeInfoSatangThread, binanceMarketsThread, binanceHistThread, cancelBuyThread, processTradesThread, satangMarginThread, k2faThread, satangBuyThread, binanceNetworkThread, satangNetworkThread
from threads import satangMarketsThread, satangConfigThread, satangHistThread, satangCancelBuyThread

def main():
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(filename='/var/log/bnst.log', format=format, level=logging.INFO, datefmt="%B,%d %H:%M:%S")
    logging.info("\nstarting...")
    os.system('clear')

    text = "Please wait..."
    preLoad(0,0, text, False)

    queue = Queue()

    clock = displayClock(1, queue); clock.start(); time.sleep(0.5)
    busd = busdRateThread(60, queue); busd.start(); time.sleep(0.5)
    #thbRate = thbRateThread(60, queue); thbRate.start(); time.sleep(0.5)
    initial = initialValuesTask(queue); initial.start(); time.sleep(0.5)
    exBinance = exchangeInfoBinanceThread(30, queue); exBinance.start(); time.sleep(0.5)
    exSatang = exchangeInfoSatangThread(30, queue); exSatang.start(); time.sleep(0.5)
    binanceNetwork = binanceNetworkThread(15, queue); binanceNetwork.start(); time.sleep(0.5)
    satangNetwork = satangNetworkThread(15, queue); satangNetwork.start(); time.sleep(0.5)
    k2fa = k2faThread(10, queue); k2fa.start(); time.sleep(0.5)
    binanceWallet = binanceWalletThread(1, queue); binanceWallet.start(); time.sleep(0.5)
    satangWallet = satangWalletThread(2, queue); satangWallet.start(); time.sleep(0.5)
    satangConfig = satangConfigThread(5, queue); satangConfig.start(); time.sleep(0.5)
    binanceBids = binanceMarketsThread(6, queue, 20); binanceBids.start(); time.sleep(0.5)
    satangBids = satangMarketsThread(6, queue, 20); satangBids.start(); time.sleep(0.5)
    binanceMargin = binanceMarginThread(0.04, queue); binanceMargin.start(); time.sleep(0.5)
    satangMargin = satangMarginThread(0.04, queue); satangMargin.start(); time.sleep(0.5)
    binanceHist = binanceHistThread(2, queue); binanceHist.start(); time.sleep(0.5)
    satangHist = satangHistThread(2, queue); satangHist.start(); time.sleep(0.5)
    satangCancelBuy = satangCancelBuyThread(10, queue); satangCancelBuy.start(); time.sleep(0.5)
    #cancelBuy = cancelBuyThread(15, queue); cancelBuy.start(); time.sleep(0.5)
    #processTrades = processTradesThread(3, queue); processTrades.start(); time.sleep(0.5)
    satangBuy = satangBuyThread(0.01, queue); satangBuy.start(); time.sleep(0.5)
    readkb = readKeyboardInput(queue); readkb.start(); time.sleep(0.5)
    # ------------------------------------------------
    busd.join(); time.sleep(0.5)
    #thbRate.join(); time.sleep(0.5)
    initial.join(); time.sleep(0.5)
    exBinance.join(); time.sleep(0.5)
    exSatang.join(); time.sleep(0.5)
    binanceNetwork.join(); time.sleep(0.5)
    satangNetwork.join(); time.sleep(0.5)
    k2fa.join(); time.sleep(0.5)
    binanceWallet.join(); time.sleep(0.5)
    satangWallet.join(); time.sleep(0.5)
    satangConfig.join(); time.sleep(0.5)
    ##stockCheck.join(); time.sleep(0.5)
    binanceBids.join(); time.sleep(0.5)
    satangBids.join(); time.sleep(0.5)
    binanceMargin.join(); time.sleep(0.5)
    satangMargin.join(); time.sleep(0.5)
    binanceHist.join(); time.sleep(0.5)
    satangHist.join(); time.sleep(0.5)
    #cancelBuy.join(); time.sleep(0.5)
    satangCancelBuyjoin(); time.sleep(0.5)
    satangBuy.join(); time.sleep(0.5)
    readkb.join(); time.sleep(0.5)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.info("CTRL-C pressed")
        print("Please use command `exit`\n")
        pass

