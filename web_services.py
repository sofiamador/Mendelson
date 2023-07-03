import requests
import json

from Enteties import GroupOfOrders
number_of_allocation_per_employee = 5
host = "https://menprime.mendelson.co.il/odata/Priority/tabula.ini/a121204/"
# host = https://priweb.mendelson.co.il/odata/Priority/tabula.ini/a121204/
with open('auth.txt', 'rb') as f:
    auth = f.read()


def get_stock():
    url = host + "PARTBAL?$select=PARTNAME, LOCNAME, STZONECODE,BALANCE,ACTNAME&$filter=WARHSNAME eq '500' and (STZONECODE eq 'C1' or STZONECODE eq 'W1' or STZONECODE eq 'W2') and BALANCE ne 0 AND CUSTNAME eq 'Goods'"

    payload = {}
    headers = {
        'X-App-Id': 'APPSS04',
        'X-App-Key': '18B75A16244B4664BF5A3C5AD58BCAEA',
        'Authorization': auth
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return json.loads(response.text)["value"]


def get_stock2():
    f = open("AvailableStock", "r")
    text = f.read()
    f.close()
    return json.loads(text)["value"]


def get_wtasks():
    url = host +"WTASKS?$select=STZONECODE,WTASKNUM,PRIO,DOERLOGIN,STATDES,ADCSTARTED,WTASKTYPECODE,MEND_PRIO2,ADCSUDATE&$filter=WARHSNAME eq '500' and(STZONECODE eq 'C1' or STZONECODE eq 'W1' or STZONECODE eq 'W2') and DOERLOGIN eq 'בודק3' and (STATDES eq 'לביצוע' or STATDES eq 'מושהה') and (WTASKTYPECODE eq 'PIK' or WTASKTYPECODE eq 'RPI' or WTASKTYPECODE eq 'RPL' or WTASKTYPECODE eq 'MOV' or WTASKTYPECODE eq 'PUT')&$expand=WTASKITEMS_SUBFORM($select=PARTNAME, LOCNAME, PTQUANT,KLINE)"
    payload = {}
    headers = {
        'X-App-Id': 'APPSS04',
        'X-App-Key': '18B75A16244B4664BF5A3C5AD58BCAEA',
        'Authorization': auth
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    return json.loads(response.text)["value"]


def get_wtasks2():
    f = open("WTASKS", "r")
    text = f.read()
    f.close()
    return json.loads(text)["value"]


def get_old_tasks():
    url = "https://menprime.mendelson.co.il/odata/Priority/tabula.ini/a121204/WTASKS?$select=STZONECODE,WTASKNUM,PRIO,DOERLOGIN,STATDES,ADCSTARTED,WTASKTYPECODE,MEND_PRIO2,ADCSUSERLOGIN,ADCSUDATE,LINES&$filter=ADCSUDATE ge 2023-05-25T00:00:00%2B03:00 and (STATDES eq 'הושלמה' or STATDES eq 'לביצוע' ) and WTASKTYPECODE eq 'PIK' and(STZONECODE eq 'C1' or STZONECODE eq 'W1' or STZONECODE eq 'W2') and ADCSTARTED eq 'Y'&$expand="
    payload = {}
    headers = {
        'X-App-Id': 'APPSS04',
        'X-App-Key': '18B75A16244B4664BF5A3C5AD58BCAEA',
        'Authorization': auth
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    return json.loads(response.text)["value"]


def post_transfer_tasks(schedule):
    f = open("transfer_task.txt", "w")
    for k, tasks in schedule.items():
        if len(tasks) == 0:
            continue
        url = host + "WTASKS"
        for t in tasks:
            for l in t.selected_locations:
                payload = {
                    "WTASKTYPECODE": "MOV",
                    "WARHSNAME": "500",
                    "STZONECODE": l.warehouse_id,
                    "TOWARHSNAME": "500",
                    "TOSTZONECODE": "RL",
                    "DOERLOGIN": k,
                    "STATDES": "לביצוע",
                    "WTASKITEMS_SUBFORM": [
                    ]
                }
                payload["WTASKITEMS_SUBFORM"].append(
                    {
                        "LOCNAME": l.loc_str,
                        "PARTNAME": t.item_id,
                        "PALLETNAME": l.pallet,
                        "TOLOCNAME": "RL.01",
                        "PTQUANT": l.quantity
                    })
                payload_json = json.dumps(payload)
                headers = {
                    'X-App-Id': 'APPSS04',
                    'X-App-Key': '18B75A16244B4664BF5A3C5AD58BCAEA',
                    'Content-Type': 'application/json',
                    'Authorization': auth
                }
                f.write(url + "\n")
                f.write(str(payload_json) + "\n")

                response = requests.request("POST", url, headers=headers, data=payload_json)
                print(response.text)

    f.close()


def patch_update_allocation(schedule):
    f = open("allocation_task.txt", "w")
    for k, tasks in schedule.items():
        prio = 1
        for t in tasks:
            if prio == number_of_allocation_per_employee:
                break
            if isinstance(t, GroupOfOrders):
                for order in t.orders:
                    url = host + "WTASKS('" + order.order_id + "')"
                    payload = json.dumps({
                        "MEND_PRIO2": order.priority,
                        "DOERLOGIN": k,
                        "PRIO": prio
                    })
                    headers = {
                        'X-App-Id': 'APPSS04',
                        'X-App-Key': '18B75A16244B4664BF5A3C5AD58BCAEA',
                        'Content-Type': 'application/json',
                        'Authorization': auth
                    }
                    f.write(url + "\n")
                    f.write(str(payload) + "\n")
                    response = requests.request("PATCH", url, headers=headers, data=payload)
                    print(response.text)
                prio += 1
            else:
                url = host + "WTASKS('" + t.order_id + "')"
                payload = json.dumps({
                    "MEND_PRIO2": t.priority,
                    "DOERLOGIN": k,
                    "PRIO": prio

                })
                prio += 1
                headers = {
                    'X-App-Id': 'APPSS04',
                    'X-App-Key': '18B75A16244B4664BF5A3C5AD58BCAEA',
                    'Content-Type': 'application/json',
                    'Authorization': auth
                }
                f.write(url + "\n")
                f.write(str(payload) + "\n")
                response = requests.request("PATCH", url, headers=headers, data=payload)
                print(response.text)

        response = requests.request("PATCH", url, headers=headers, data=payload)

    f.close()


def patch_upadate_location_for_items(schedule):
    f = open("update_allocation.txt", "w")
    for k, tasks in schedule.items():
        if len(tasks) == 0:
            continue
        for task in tasks:
            for item in task.lines:
                url = host + "WTASKS('" + item.order_id + "')"

                payload = json.dumps({
                    "WTASKITEMS_SUBFORM": [
                        {
                            "KLINE": item.line_number,
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

                response = requests.request("PATCH", url, headers=headers, data=payload)
                print(response.text)
                f.write(url + "\n")
                f.write(str(payload) + "\n")
    f.close()
