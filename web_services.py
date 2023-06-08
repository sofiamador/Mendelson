import requests
import json

from Enteties import GroupOfOrders
host = "https://menprime.mendelson.co.il/odata/Priority/tabula.ini/a121204/"
#host = https://priweb.mendelson.co.il/odata/Priority/tabula.ini/a121204/
with open('auth.txt', 'rb') as f:
    auth = f.read()


def get_stock():
    url = host+"PARTBAL?$select=PARTNAME, LOCNAME, STZONECODE,BALANCE,ACTNAME&$filter=WARHSNAME eq '500' and (STZONECODE eq 'C1' or STZONECODE eq 'W1' or STZONECODE eq 'W2') and BALANCE ne 0 AND CUSTNAME eq 'Goods'"

    payload = {}
    headers = {
        'X-App-Id': 'APPSS04',
        'X-App-Key': '18B75A16244B4664BF5A3C5AD58BCAEA',
        'Authorization': auth
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.text


def get_stock2():
    f = open("AvailableStock", "r")
    text = f.read()
    f.close()
    return json.loads(text)


def get_wtasks():
    url = host+"WTASKS?$select=STZONECODE,WTASKNUM,PRIO,DOERLOGIN,STATDES,ADCSTARTED,WTASKTYPECODE&$filter=WARHSNAME eq '500' and CDES ne 'סניף*' and(STZONECODE eq 'C1' or STZONECODE eq 'W1' or STZONECODE eq 'W2') and DOERLOGIN ne 'dimitri' and (STATDES eq 'לביצוע' or STATDES eq 'מושהה') and (WTASKTYPECODE eq 'PIK' or WTASKTYPECODE eq 'RPI' or WTASKTYPECODE eq 'RPL' or WTASKTYPECODE eq 'MOV' or WTASKTYPECODE eq 'PUT') and ADCSTARTED ne 'Y'&$expand=WTASKITEMS_SUBFORM($select=PARTNAME, LOCNAME, PTQUANT,KLINE)"
    payload = {}
    headers = {
        'X-App-Id': 'APPSS04',
        'X-App-Key': '18B75A16244B4664BF5A3C5AD58BCAEA',
        'Authorization': auth
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    return response.text


def get_wtasks2():
    f = open("WTASKS", "r")
    text = f.read()
    f.close()
    return json.loads(text)["value"]


def post_transfer_tasks(schedule):
    for k, tasks in schedule.items():
        if len(tasks) == 0:
            continue
        url = host+"WTASKS"
        payload = {
            "WTASKTYPECODE": "MOV",
            "WARHSNAME": "500",
            "STZONECODE": "W1",
            "TOWARHSNAME": "500",
            "TOSTZONECODE": "RL",
            "DOERLOGIN": k,
            "STATDES": "לביצוע",
            "WTASKITEMS_SUBFORM": [
            ]
        }
        for t in tasks:
            payload["WTASKITEMS_SUBFORM"].append(
                {
                    "LOCNAME": t.location.loc_str,
                    "PARTNAME": t.item_id,
                    "PALLETNAME": t.location.pallet,
                    "TOLOCNAME": "RL.01",
                    "PTQUANT": 100  # TODO BEN
                })
        payload_json = json.dumps(payload)
        headers = {
            'X-App-Id': 'APPSS04',
            'X-App-Key': '18B75A16244B4664BF5A3C5AD58BCAEA',
            'Content-Type': 'application/json',
            'Authorization': auth
        }

    # response = requests.request("POST", url, headers=headers, data=payload_json)
    # print(response.text)
    f = open("transfer_task.txt", "w")
    f.write(url + "\n")
    f.write(str(payload_json) + "\n")
    f.close()


def patch_update_allocation(schedule):
    f = open("allocation_task.txt", "w")
    for k, tasks in schedule.items():
        for t in tasks:
            if isinstance(t,GroupOfOrders):
                for order in t.orders:
                    url = host+"WTASKS('" + order.order_id + "')"
                    payload = json.dumps({
                        "DOERLOGIN": k
                    })
                    headers = {
                        'X-App-Id': 'APPSS04',
                        'X-App-Key': '18B75A16244B4664BF5A3C5AD58BCAEA',
                        'Content-Type': 'application/json',
                        'Authorization': auth
                    }
                    f.write(url + "\n")
                    f.write(str(payload) + "\n")
                    # response = requests.request("PATCH", url, headers=headers, data=payload)
            else:
                url = host+"WTASKS('" + t.order_id + "')"
                payload = json.dumps({
                    "DOERLOGIN": k
                })
                headers = {
                    'X-App-Id': 'APPSS04',
                    'X-App-Key': '18B75A16244B4664BF5A3C5AD58BCAEA',
                    'Content-Type': 'application/json',
                    'Authorization': auth
                }
                f.write(url +"\n")
                f.write(str(payload) + "\n")
                # response = requests.request("PATCH", url, headers=headers, data=payload)

        # response = requests.request("PATCH", url, headers=headers, data=payload)
        # print(response.text)
    f.close()


def patch_upadate_location_for_items(schedule):
    f = open("update_allocation.txt", "w")
    for k, tasks in schedule.items():
        if len(tasks) == 0:
            continue
        for task in tasks:
            for item in task.lines:
                url = host+"WTASKS('" + 11111 + "')"  # TODO BEN

                payload = json.dumps({
                    "WTASKITEMS_SUBFORM": [
                        {
                            "KLINE": 1,  #TODO BEN
                            "LOCNAME": "RL.01"
                        }
                    ]
                })
                headers = {
                    'X-App-Id': 'APPSS04',
                    'X-App-Key': '18B75A16244B4664BF5A3C5AD58BCAEA',
                    'Content-Type': 'application/json',
                    'Authorization': auth
                }

        # response = requests.request("PATCH", url, headers=headers, data=payload)
        # print(response.text)
                f.write(url + "/n")
                f.write(str(payload) + "/n")
        f.close()
