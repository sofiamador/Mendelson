import requests
import json


with open('auth.txt', 'rb') as f:
    auth = f.read()


def get_stock():
    url = "https://priweb.mendelson.co.il/odata/Priority/tabula.ini/a121204/PARTBAL?$select=PARTNAME, LOCNAME, STZONECODE,BALANCE,ACTNAME&$filter=WARHSNAME eq '500' and (STZONECODE eq 'C1' or STZONECODE eq 'W1' or STZONECODE eq 'W2') and BALANCE ne 0 AND CUSTNAME eq 'Goods'"

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
    return text


def get_wtasks():
    url = "https://priweb.mendelson.co.il/odata/Priority/tabula.ini/a121204/WTASKS?$select=STZONECODE,WTASKNUM,PRIO,DOERLOGIN,STATDES,ADCSTARTED,WTASKTYPECODE&$filter=WARHSNAME eq '500' and CDES ne 'סניף*' and(STZONECODE eq 'C1' or STZONECODE eq 'W1' or STZONECODE eq 'W2') and DOERLOGIN ne 'dimitri' and (STATDES eq 'לביצוע' or STATDES eq 'מושהה') and (WTASKTYPECODE eq 'PIK' or WTASKTYPECODE eq 'RPI' or WTASKTYPECODE eq 'RPL' or WTASKTYPECODE eq 'MOV' or WTASKTYPECODE eq 'PUT') and ADCSTARTED ne 'Y'&$expand=WTASKITEMS_SUBFORM($select=PARTNAME, LOCNAME, PTQUANT,KLINE)"
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
    return text


def post_transfer_tasks(tasks):
    url = "https://priweb.mendelson.co.il/odata/Priority/tabula.ini/a121204/WTASKS"
    payload = {
        "WTASKTYPECODE": "MOV",
        "WARHSNAME": "500",
        "STZONECODE": "W1",
        "TOWARHSNAME": "500",
        "TOSTZONECODE": "RL",
        "DOERLOGIN": "בודק3",
        "STATDES": "לביצוע",
        "WTASKITEMS_SUBFORM": [
        ]
    }
    for t in tasks:
        payload["WTASKITEMS_SUBFORM"].append(
            {
                "LOCNAME": t.location,  # TODO
                "PARTNAME": t.item_id,  # TODO
                "PALLETNAME": t.pallet,  # TODO
                "TOLOCNAME": "RL.01",
                "PTQUANT": t.quantity  # TODO
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
    f.write(url + "/n")
    f.write(str(payload_json) + "/n")


def patch_update_allocation(allocation_tasks):
    f = open("allocation_task.txt", "w")
    for t in allocation_tasks:
        url = "https://priweb.mendelson.co.il/odata/Priority/tabula.ini/a121204/WTASKS('" + t.order_id + "')"
        payload = json.dumps({
            "DOERLOGIN": t.employee  # TODO
        })
        headers = {
            'X-App-Id': 'APPSS04',
            'X-App-Key': '18B75A16244B4664BF5A3C5AD58BCAEA',
            'Content-Type': 'application/json',
            'Authorization': auth
        }

        #response = requests.request("PATCH", url, headers=headers, data=payload)

        #print(response.text)



def patch_upadate_location_for_items(items):
    f = open("update_alocation.txt", "w")
    for i in items:
        url = "https://priweb.mendelson.co.il/odata/Priority/tabula.ini/a121204/WTASKS('" + i.order_id + "')" #TODO

        payload = json.dumps({
            "WTASKITEMS_SUBFORM": [
                {
                    "KLINE": i.line_number,  #TODO
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

        #response = requests.request("PATCH", url, headers=headers, data=payload)
        #print(response.text)
        f.write(url + "/n")
        f.write(str(payload) + "/n")

