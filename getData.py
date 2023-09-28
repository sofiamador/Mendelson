import json
from Globals import *
import requests


with open('auth.txt', 'r') as f:
    auth = f.read()

def get_old_tasks(date):
    names_to_ignore = ""
    if len(employees_to_ignore) > 0:
        names_to_ignore = "and("
        i = 0
        for name in employees_to_ignore:
            names_to_ignore += "DOERLOGIN ne '" + name + "'"
            i += 1
            if i == len(employees_to_ignore):
                names_to_ignore += ")"
            else:
                names_to_ignore += " and "
    # print(names_to_ignore)
    url = host + "WTASKS?$select=STZONECODE,WTASKNUM,PRIO,DOERLOGIN,STATDES,ADCSTARTED,WTASKTYPECODE,MEND_PRIO2,ADCSUSERLOGIN,ADCSUDATE,LINES,ADCFUDATE,CDES&" \
                 "$filter=ADCSUDATE ge 2023-09-26T00:00:00%2B03:00 and ADCSUDATE le 2023-09-26T23:00:00%2B03:00 and " \
                 "ADCSTARTED eq 'Y' and WTASKTYPECODE eq 'PIK'  and(STZONECODE eq 'C1' or STZONECODE eq 'W1' or STZONECODE eq 'W2' " \
                 "or STZONECODE eq 'A2') &$expand="
    payload = {}
    headers = {
        'X-App-Id': 'APPSS04',
        'X-App-Key': '18B75A16244B4664BF5A3C5AD58BCAEA',
        'Authorization': auth
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    return json.loads(response.text)["value"]




print(get_old_tasks("2023-09-26"))

