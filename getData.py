import json
from Globals import *
import requests
from datetime import datetime
import pandas as pd

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
                 "$filter=ADCSUDATE ge " + date + "T00:00:00%2B03:00 and ADCSUDATE le " + date + "T23:00:00%2B03:00 and " \
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


def save_data(data):
    type_task_list = []
    employee_name_list = []
    zone_list = []
    count_of_lines_lst = []
    start_time_list = []
    end_time_list = []
    total_time_list = []
    avg_times_list = []
    date_list = []
    status_list = []
    employess_distinct_list = []
    for key, old_task_data in data.items():
        employee_name_list_for_day = []
        for task in old_task_data:
            if task['ADCFUDATE'] is None or int(task['LINES']) == 0:
                continue
            start_time = task['ADCSUDATE'].split("T")[1].split("+")[0][:5]
            hours, minutes = map(int, start_time.split(':'))
            start_time = hours + minutes / 60.0

            end_time = task['ADCFUDATE'].split("T")[1].split("+")[0][:5]
            hours, minutes = map(int, end_time.split(':'))
            end_time = hours + minutes / 60.0
            if start_time<10 or start_time>18:
                continue
            time_difference = end_time-start_time

            type_task_list.append(task['WTASKTYPECODE'])
            if task['DOERLOGIN'] in employee_name_list_for_day:
                employess_distinct_list.append(0)
            else:
                employess_distinct_list.append(1)
                employee_name_list_for_day.append(task['DOERLOGIN'])
            employee_name_list.append(task['DOERLOGIN'])
            zone_list.append(task["STZONECODE"])
            count_of_lines = int(task['LINES'])
            count_of_lines_lst.append(count_of_lines)

            start_time_list.append(start_time)
            end_time_list.append(end_time)
            total_time_list.append(time_difference)
            avg_time_per_line = time_difference / count_of_lines
            avg_times_list.append(avg_time_per_line)
            date_list.append(key[0])
            status_list.append(key[1])
    d = {'type': type_task_list, 'employee name': employee_name_list, "number of lines": count_of_lines_lst,
         "start time": start_time_list, "end time": end_time_list, "duration": total_time_list,
         "average time for line": avg_times_list, "date": date_list, "status": status_list,"employees_distinct":employess_distinct_list}
    df = pd.DataFrame(data=d)
    return df


def write_to_excel(pd_output, file_name_):
    pd_output.to_excel(file_name_ + ".xlsx",
                       sheet_name="file_name_", index=False)
    return


dic_old_data = {}
prev_dates = ["2023-08-06", "2023-08-07", "2023-08-08", "2023-08-09", "2023-08-10", "2023-08-27", "2023-08-28",
              "2023-08-29", "2023-08-30", "2023-08-31"]
curr_dates = ["2023-09-18", "2023-09-19", "2023-09-20", "2023-09-21", "2023-09-26", "2023-09-28", "2023-09-29"]
for date in prev_dates:
    old_data = get_old_tasks(date)
    dic_old_data[(date, 0)] = old_data
for date in curr_dates:
    old_data = get_old_tasks(date)
    dic_old_data[(date, 1)] = old_data
df_otput = save_data(dic_old_data)
write_to_excel(df_otput, "analytics")
