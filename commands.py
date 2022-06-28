import json
import logging

def commandExecute(commands, q):
    store = q.get()
    logging.info(commands)
    cmds = commands.split(" ")
    #commands = [
    #            {
    #            "run, loop": {
    #                "start": True,
    #                "stop" : False
    #                }
    #            },
    #            {
    #            "ws": {
    #                "start": True,
    #                "stop" : False
    #                }
    #            },
    #            {
    #            "home": {
    #                "start": True,
    #                "stop" : False
    #                }
    #            }
    #        ]

    if cmds[0] == "run":
        if cmds[1] == "start":
            store['run'] = True
        elif cmds[1] == "stop":
            store['run'] = False
            store['trades'] = []
        else:
            return False

    elif cmds[0] == "loop":
        if cmds[1] == "start":
            store['loop'] = True
        elif cmds[1] == "stop":
            store['loop'] = False
        else:
            return False

    elif cmds[0] == "btx":
        if cmds[1] == "start":
            store['btx'] = True
        elif cmds[1] == "stop":
            store['btx'] = False
        else:
            return False

    elif cmds[0] == "ws":
        if cmds[1] == "start":
            store['wsClose'] = False
        elif cmds[1] == "stop":
            store['wsClose'] = True
        else:
            return False

    elif cmds[0] == "home":
        if cmds[1] == "start":
            store['homePause'] = False
        elif cmds[1] == "stop":
            store['homePause'] = True
        else:
            return False
    else:
        return false

    #for command in cmds:
    #    return True
    #    #if command == "startBuy":
    #    #    store['tradeBuy'] = True
    #    #elif command == "startSell":
    #    #    store['tradeSell'] = True
    #    #elif command == "stopBuy":
    #    #    store['tradeBuy'] = False
    #    #elif command == "stopSell":
    #    #    store['tradeSell'] = False
    #    #else:
    #    #    logging.info("something wrong")
    #return False

    q.put(store)

def commandValid(string):
    array = string.split(" ")
    try:
        if type(float(array[-1])) is float:
            array = array[:-1]
    except:
        pass

    org = array
    defined = json.loads(commandStructure())

    valids = []
    for i,j in enumerate(array):
        if array[i:]:
            for c in array[i:]:
                for k,v in enumerate(defined):
                    if v['name'] == c:
                        if len(v['child']) > 0:
                            valids.append(False)
                            defined = v['child']
                        else:
                            valids.append(True)

    count = 0
    for v in valids:
        if v:
            count += 1

    if count == len(org):
        return True
    return False

def commandStructure():
    bools = [
                {
                "name": "stop",
                "child": []
                },
                {
                "name": "start",
                "child": []
                }
            ]

    commands = [
                    {
                        "name": "run",
                        "child": bools
                        },
                    {
                        "name": "loop",
                        "child": bools
                        },
                    {
                        "name": "btx",
                        "child": bools
                        },
                    {
                        "name": "ws",
                        "child": bools
                        },
                    {
                        "name": "home",
                        "child": bools
                        },
                    {
                        "name": "bnmax",
                        "child": False
                        }
                    ]

    #logging.info(json.dumps(commands, indent=3, sort_keys=True))
    return json.dumps(commands, sort_keys=False)

