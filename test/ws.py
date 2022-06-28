#!/usr/bin/python3

import websocket
import time
import logging
import argparse

def on_message(ws, message):
    print(message)

def on_error(ws, message):
    print(message)

def on_close(ws):
    print("-- closed --")

def on_open(ws):
    prnt("-- opened --")
    #msg = {
    #    "method": "SUBSCRIBE",
    #    "params": [
    #        #"btcusdt@aggTrade",
    #        "btcusdt@depth"
    #    ],
    #    "id": 1
    #}
    #print(msg)
    #time.sleep(1)
    #ws.send(msg)

if __name__ == '__main__':
    #parser = argparse.ArgumentParser()
    #parser.add_argument("-s", "--symbol", required=True, help="symbol requited")
    #args = parser.parse_args()

    #ws_api = "wss://stream.binance.com:9443/ws/bnbbtc@depth"
    #ws_api = "wss://stream.binance.com:9443/ws/%s@depth5@100ms" % args.symbol.lower()
    #ws_api = "wss://ws.satangcorp.com/ws/%s@depth20@100ms" % args.symbol.lower()
    #ws_api = "wss://api.bitkub.com/websocket-api/market.trade.thb_btc,market.ticker.thb_btc"
    ws_api = "wss://api.bitkub.com/websocket-api/market.trade.thb_btc"
    print(ws_api)
    time.sleep(3)
    ##ws_api = "wss://stream.binance.com:9443/ws/!bookTicker"
    #print(ws_api)
    ws = websocket.WebSocketApp(ws_api,
            on_message = lambda ws,msg: on_message(ws, msg),
            on_error = lambda ws,msg: on_error(ws, msg),
            on_close = lambda ws: on_close(ws),
            on_open = lambda ws: on_open(ws))

    ws.keep_running = True
    while True:
        print('thread running')
        ws.run_forever(ping_interval=1)
        time.sleep(3)
