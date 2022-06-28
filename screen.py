import os
import sys
import time
import json
import logging

usleep = lambda x: time.sleep(x/1000000.0)

def clearLine(line, ended, reverse=False):
    for column in range(ended):
        if reverse:
            size = os.get_terminal_size()
            column = size.columns - column - 1

        sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (line, column, "·"))
        sys.stdout.flush()

def preLoad(line, column, text, clear=False):
    length = len(text)
    if clear:
        whitespace = []
        for _ in range(length):
            whitespace.append("·")

        text = "".join(whitespace)

    reverse = False
    obj = json.dumps({
            "text": text,
            "line": line,
            "column": column,
            "length": len(text),
            "reverse": reverse
            })
    drawLine(obj)

def drawing(text, line, column):
    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (line, column, text))
    sys.stdout.flush()

def drawLine(obj, clear=False):
    j = json.loads(obj)
    line = j['line']
    column = j['column']
    text = j['text']
    maxLength = j['length']
    reverse = j['reverse']
    text = str(text)

    if reverse:
        size = os.get_terminal_size()
        column = size.columns - column - maxLength

    # clear
    whitespace = []
    for _ in range(maxLength):
        whitespace.append("·")

    clear = "".join(whitespace)
    drawing(clear, line, column)

    #time.sleep(0.02)
    usleep(1000)
    # write
    drawing(text, line, column)


