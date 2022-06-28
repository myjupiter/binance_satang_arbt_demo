import ssl
import websocket
import time
import json
import logging
import threading


'''
{'lastUpdateId': 167213002, 'bids': [['0.69370000', '352.97000000'], ['0.69360000', '420.00000000'], ['0.69350000', '945.47000000'], ['0.69340000', '28.93000000'], ['0.69330000', '907.92000000']], 'asks': [['0.69470000', '1871.84000000'], ['0.69490000', '1767.98000000'], ['0.69500000', '1424.73000000'], ['0.69510000', '987.97000000'], ['0.69530000', '989.48000000']]}


{'lastUpdateId': 467942737, 'bids': [['3405', '1'], ['3350', '0.519'], ['3201', '1'], ['3200.01', '0.2806'], ['3200', '3.4921']], 'asks': [['4800', '4.091'], ['4898', '0.3346'], ['4900', '0.1308'], ['5100', '0.181'], ['5120', '2.315']]}


'''

def marketStore(message, sym, q):
    r = json.loads(message)
    #logging.info(r)
    store = q.get()
    # store asks and bids
    asks = "asks_%s" % (sym)
    store[asks] = r['asks']
    bids = "bids_%s" % (sym)
    store[bids] = r['bids']
    #if "rub" in sym:
    #    log = "store: %s" % bids
    #    logging.info(log)
    q.put(store)

class MarketUpdate(threading.Thread):
    def __init__(self, sym, q):
        self.q = q
        self.sym = sym
        store = q.get()
        self.wsLimit = store['wsLimit']
        q.put(store)

    def on_message(self, ws, message):
        #logging.info(message)
        #x = message
        marketStore(message, self.sym, self.q)
        #try:
        #    marketStore(message, self.sym, self.q)
        #except Exception as e:
        #    logging.info(e)
        #    log = "Closing ws for %s" % self.sym
        #    self.ws.close()
        #    ws.close()

    def on_error(self, ws, error):
        logging.info(error)
        self.remove()

    def on_close(self, ws):
        logging.info(f'--- closed {self.sym}')
        self.remove()

    def on_open(self, ws):
        logging.info(f'--- opened {self.sym}')
        store = self.q.get()
        pullings = store['pullingsBinance']
        pullings.append(self.sym)
        store['pullingsBinance'] = pullings
        logging.info(f'added ws pulling: {self.sym}')
        self.q.put(store)

    def remove(self):
        store = self.q.get()
        if self.sym in store['pullingsBinance']:
            logging.info(f'Removing ws {self.sym}')
            store['pullingsBinance'].remove(self.sym) # very important
        #pullings = store['pullingsBinance']
        self.q.put(store)

    def run(self):
        try:
            ws_api = "wss://stream.binance.com:9443/ws/%s@depth%s@100ms" % (self.sym, self.wsLimit)
            #logging.info(ws_api)
            #websocket.enableTrace(True)
            self.ws = websocket.WebSocketApp(ws_api,
                    on_message = lambda ws,msg: self.on_message(ws, msg),
                    on_error = lambda ws,msg: self.on_error(ws, msg),
                    on_close = lambda ws: self.on_close(ws),
                    on_open = lambda ws: self.on_open(ws))

            #self.ws.keep_running = True
            ##self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            self.wst = threading.Thread(target=self.ws.run_forever)
            self.wst.daemon = True
            self.wst.start()
        except Exception as e:
            logging.info(e)

def storeBusd(bids, q):
    store = q.get()
    for b in bids:
        aBusd = float(list(b)[1])
        pBusd = float(list(b)[0])
        if aBusd > store['busdOnly']:
            #log = "%s %s" % (pBusd, aBusd)
            #logging.info(log)
            store['busd_thb'] = pBusd
            break
    q.put(store)
    return

def marketStoreSecond(message, sym, q):
    #logging.info(message)
    #x = str(message).rstrip()
    ##logging.info(x.split()[0])
    #r = json.loads(x.split()[0])
    try:
        r = json.loads(message)
        #logging.info(r)
        store = q.get()
        # store asks and bids
        asks = "asks_%s" % (sym)
        store[asks] = r['asks']
        bids = "bids_%s" % (sym)
        store[bids] = r['bids']
        if "busd_thb" in sym:
            #log = "store: %s %s" % (bids, r['bids'])
            #logging.info(log)
            storeBusd(r['bids'], q)
        q.put(store)
    except Exception as e:
        logging.info(e)
    #store = q.get()
    ## store asks and bids
    #asks = "asks_%s" % (sym)
    #store[asks] = r['asks']
    #bids = "bids_%s" % (sym)
    #store[bids] = r['bids']
    #if "busd_thb" in sym:
    #    #log = "store: %s %s" % (bids, r['bids'])
    #    #logging.info(log)
    #    storeBusd(r['bids'], q)
    #q.put(store)

class MarketUpdateSecond(threading.Thread):
    def __init__(self, sym, q):
        self.q = q
        self.sym = sym
        store = q.get()
        if sym == "busd_thb":
            self.wsLimit = 20
        else:
            self.wsLimit = store['wsLimit']
        q.put(store)

    def on_message(self, ws, message):
        #logging.info(message)
        #x = message
        marketStoreSecond(message, self.sym, self.q)
        #try:
        #    marketStoreSecond(message, self.sym, self.q)
        #except Exception as e:
        #    logging.info(e)
        #    log = "Closing ws for %s" % self.sym
        #    logging.info(log)
        #    self.ws.close()
        #    ws.close()

    def on_error(self, ws, error):
        logging.info(error)
        self.remove()

    def on_close(self, ws):
        logging.info(f'--- closed {self.sym}')
        self.remove()

    def on_open(self, ws):
        logging.info(f'--- opened {self.sym}')
        store = self.q.get()
        pullings = store['pullingsSatang']
        pullings.append(self.sym)
        store['pullingsSatang'] = pullings
        logging.info(f'added ws pulling: {self.sym}')
        self.q.put(store)

    def remove(self):
        store = self.q.get()
        if self.sym in store['pullingsSatang']:
            logging.info(f'Removing ws {self.sym}')
            store['pullingsSatang'].remove(self.sym) # very important
        #pullings = store['pullingsSatang']
        self.q.put(store)

    def run(self):
        try:
            ws_api = "wss://ws.satangcorp.com/ws/%s@depth%s@100ms" % (self.sym, self.wsLimit)
            #logging.info(ws_api)
            #websocket.enableTrace(True)
            self.ws = websocket.WebSocketApp(ws_api,
                    on_message = lambda ws,msg: self.on_message(ws, msg),
                    on_error = lambda ws,msg: self.on_error(ws, msg),
                    on_close = lambda ws: self.on_close(ws),
                    on_open = lambda ws: self.on_open(ws))

            #self.ws.keep_running = True
            ##self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            self.wst = threading.Thread(target=self.ws.run_forever)
            self.wst.daemon = True
            self.wst.start()
        except Exception as e:
            logging.info(e)


