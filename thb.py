import json
import logging
import requests
from useragent import Agent
from bs4 import BeautifulSoup
from screen import drawLine, clearLine
from utils import getLength

def getRate(tr):
    rate = 0.00
    try:
        #logging.info(tr)
        html = "<html>%s</html>" % tr
        soup = BeautifulSoup(html, "html.parser")
        sell = soup.find_all('td')[-1].text
        #logging.info(sell)
        rate = float(sell)
    except:
        pass
    return rate

def thbRate(delay, q):
    store = q.get()
    if store is not None:
        rates = store['rates'].split(",")
        url = "https://www.exch.ktb.co.th/exchangerate/pages/travelCardRate"
        headers = {'User-Agent': Agent('brave')}
        try:
            getResp = requests.get(url, headers=headers)
            if getResp.status_code == 200:
                reverse = False
                nextColumn = 25
                space = 3
                start = 1
                lines = {}
                start += 1
                lines['label'] = start
                start += 1
                lines['rate'] = start

                soup = BeautifulSoup(getResp.content, "html.parser")
                #logging.info(soup.prettify())
                table = soup.find_all('table', {"class": "table"})
                html = "<html>%s</html>" % table
                soup = BeautifulSoup(html, "html.parser")
                trs = soup.find_all('tr')
                for j,tr in enumerate(trs):
                    html = "<html>%s</html>" % tr
                    soup = BeautifulSoup(html, "html.parser")
                    tds = soup.find_all('td')
                    for i,x in enumerate(tds):
                        if i == 1:
                            html = "<html>%s</html>" % x
                            soup = BeautifulSoup(html, "html.parser")
                            span = soup.find('span')
                            if span is not None:
                                found = span.text.strip()
                                if found in rates:
                                    #logging.info(rates)
                                    endColumn = "endColumn_thb_%s" % (found.lower())
                                    for x in lines:
                                        clearLine(lines[x], store[endColumn], reverse)
                                    #text = "thb_%s" % found
                                    rate = getRate(tr) #store[text] = rate

                                    ##rate = r['data']['price']
                                    reRate = "{:,.4f}".format(float(rate))
                                    label = "THB_{}".format(found)

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
                                    endCheck = "endColumn_thb_%s" % rates[-1].lower()
                                    if store[endCheck] > 0:
                                        for x in rates:
                                            end = "endColumn_thb_%s" % x.lower()
                                            store[end]= 0

                                    thb = "busd_%s" % found.lower()
                                    store[thb] = rate
        except:
            logging.info('thbRate error')
            pass

    q.put(store)

