import random

import pandas as pd
from Enteties import Line, TaskPick, StreetObj,Employee


def read_input(file_name):
    d = pd.read_excel(file_name, index_col=None, dtype="str")
    return d


def create_files_by_date(df):
    dates = df["תאריך"].unique()
    for date in dates:
        df_for_date = df[df["תאריך"] == date]
        # date_no_time = date.split(" ")[0]
        df_for_date.to_excel("input_" + df_for_date + ".xlsx", sheet_name=df_for_date)


def choose_records(data_, field_name, values):
    frames = []
    for v in values:
        data_temp = pd.DataFrame()
        data_temp = data_[data_[field_name] == v]
        frames.append(data_temp)
    data_2 = pd.concat(frames)
    return data_2


def create_files_by_date(df):
    dates = df["תאריך"].unique()
    for date in dates:
        df_for_date = df[df["תאריך"] == date]
        date_no_time = date.split(" ")[0]
        df_for_date.to_excel("input_" + date_no_time + ".xlsx", sheet_name=date_no_time)


def create_lines(lines_input_):
    lines = []
    for ind in lines_input_.index:
        order_id = lines_input_['הזמנה'][ind]
        item_id = lines_input_['מק_ט'][ind]
        quantity = int(lines_input_['כמות_בפועל'][ind])
        warehouse_id = lines_input_['אזור_במחסן'][ind]
        location = lines_input_['מאיתור'][ind]
        importance = 0
        weight = float(lines_input_['משקל'][ind])
        line = Line(item_id=item_id, order_id=order_id, quantity=quantity, warehouse_id=warehouse_id,
                    location_string=location, importance=importance, weight=weight)
        lines.append(line)
    return lines


def create_streets(lines_by_street_dict, min_amount_of_unique_items):
    streets = []
    for k, v in lines_by_street_dict.items():
        street = StreetObj(k, v)
        street_unique_items = street.number_of_unique_items
        if street_unique_items>min_amount_of_unique_items:
        #street.ratio_val = ratio_dict[k]
        #street.makat_amount = dict_amount_of_makat_per_street[k]
        #street.order_amount = dict_amount_of_makat_in_orders_per_street[k]
            streets.append(street)
    return streets


def get_lines_by_order(lines):
    dict_ = {}
    for line in lines:
        order_id = line.order_id
        if order_id not in dict_.keys():
            dict_[order_id] = []
        dict_[order_id].append(line)

    ans = []
    counter = 0
    for line_list in dict_.values():
        ans.append(TaskPick(id_=line_list[0].order_id, lines=line_list))

    return ans




def remove_pick_tasks_that_are_finished(pick_tasks):
    list_of_pick_ids_to_delete = get_list_of_pick_ids_to_delete()
    to_remove = []
    for id_to_delete in list_of_pick_ids_to_delete:
        the_task = get_task_by_id(id_to_delete, pick_tasks)
        if the_task is None:
            print(id_to_delete, "was not found and was not deleted")
        else:
            to_remove.append(the_task)
    ans = []
    for task in pick_tasks:
        if task not in to_remove:
            ans.append(task)
    return ans


def get_list_of_pick_ids_to_delete():
    pand_table = read_input("finished_tasks.xlsx")
    temp_ = pand_table["order_ids_to_remove"]
    temp2_ = []
    for i in range(len(temp_)):
        temp2_.append(pand_table["order_ids_to_remove"][i])
    return temp2_


def get_task_by_id(id_to_delete, pick_tasks):
    for task in pick_tasks:
        if task.id_ == id_to_delete:
            return task



def create_lines_by_street(lines):
    lines_by_street = {}

    for line in lines:
        if line.location.warehouse_id == "C1":
            street = line.location.street
            if street not in lines_by_street:
                lines_by_street[street] = []
            lines_by_street[street].append(line)
    return lines_by_street

def sort_streets_by_ratio_makat_per_street_amount_of_makat_in_orders_per_street(lines_input):
    lines_c1_by_street_df = lines_input.groupby('אזור_במחסן').get_group('C1').groupby('רחוב')

    ####---- get amount of makatim per steet----####
    dict_amount_of_makat_per_street = lines_c1_by_street_df['מק_ט'].nunique().to_dict()
    ####---- get amount of orders of makats per steet----####
    dict_amount_of_makat_in_orders_per_street = lines_c1_by_street_df['הזמנה'].nunique().to_dict()

    dict_street_ratio = {}
    for street in dict_amount_of_makat_per_street.keys():
        dict_street_ratio[street] = dict_amount_of_makat_per_street[street] / dict_amount_of_makat_in_orders_per_street[
            street]

    sorted_dict = dict(sorted(dict_street_ratio.items(), key=lambda item: item[1]))
    return sorted_dict,dict_amount_of_makat_per_street,dict_amount_of_makat_in_orders_per_street


def get_unique_orders(lines_for_transfer,orders_to_remove):
    for line in lines_for_transfer:
        order_id = line.order_id
        if order_id not in orders_to_remove:
            orders_to_remove.append(order_id)


def get_lines_by_task_transfer(max_makats_in_transfer_task,min_amount_of_unique_items,max_transfer_tasks,streets):
    lines_by_task_transfer = {}
    orders_to_remove = []
    while max_transfer_tasks != 0:
        street = streets[0]
        lines_for_transfer = street.get_lines_for_transfer_task(max_makats_in_transfer_task)
        get_unique_orders(lines_for_transfer,orders_to_remove)
        lines_by_task_transfer[street]= lines_for_transfer
        if street.number_of_unique_items < min_amount_of_unique_items:
            streets.remove(street)
        streets = sorted(streets, key=lambda x: x.ratio_for_fav_street)
        max_transfer_tasks = max_transfer_tasks - 1
        if len(streets) == 0:
            break
    return lines_by_task_transfer,orders_to_remove

def create_streets_from_lines(lines,min_amount_of_unique_items):
    lines_by_street_dict = create_lines_by_street(lines)
    streets = create_streets(lines_by_street_dict, min_amount_of_unique_items=min_amount_of_unique_items)
    return sorted(streets, key=lambda x: x.ratio_for_fav_street)

def create_order_lines_dict_without_transfer(lines_by_warehouse_and_order, order_ids_to_remove =[],warehouse_to_exclude = ""):
    #ans = {}
    for order_id,dict_warehouse_and_lines in lines_by_warehouse_and_order.items():
        if order_id in order_ids_to_remove:
            if warehouse_to_exclude in dict_warehouse_and_lines:
                del dict_warehouse_and_lines[warehouse_to_exclude]

        #for warehouse_id, lines in dic_.items():

        #order_id = line.order_id
        #if order_id not in order_ids_to_remove:
         #   if order_id not in ans:
          #      ans[order_id] = []
          #  ans[order_id].append(line)
    #return ans



def create_employees(employees_data):
    employees_ = []
    for ind in employees_data.index:
        employee_id = employees_data['שם מלא'][ind]
        role = employees_data['תפקיד'][ind]
        pick_grade = int(employees_data['ליקוט'][ind])
        transfer_grade = int(employees_data['רענון'][ind])
        pick_height_grade = int(employees_data['גובה'][ind])
        abilities = {}
        if pick_grade!=0:
            abilities["pick"] = pick_grade
        if transfer_grade!=0:
            abilities["transfer"] = transfer_grade
        if pick_height_grade!=0:
            abilities["pick_height"] = pick_height_grade
        employee = Employee(id_=employee_id, abilities=abilities,role=role)
        employees_.append(employee)
    return employees_


def get_random_schedule(employees,pick_tasks, transfer_tasks):
    schedule = {}
    for employee in employees:
        name = employee.id_
        schedule[name] = []

    for transfer_task in transfer_tasks:
        rnd_emp = random.choice(employees)
        schedule[rnd_emp.id_].append(transfer_task)

    for pick_task in pick_tasks:
        rnd_emp = random.choice(employees)
        schedule[rnd_emp.id_].append(pick_task)

    return schedule



def create_pandas_output(output_tasks):
    item_id_lst = []
    order_id_lst= []
    type_lst = []
    warehouse_id_lst = []
    for task in output_tasks:
        for l in task.lines:
            item_id_lst.append(l.item_id)
            order_id_lst.append(l.order_id)

            if isinstance(task,TaskPick):
                type_lst.append("ליקוט")
                warehouse_id_lst.append(task.warehouse_id)

            else:
                type_lst.append("העברה")
                warehouse_id_lst.append("C1")
        item_id_lst.append("000")
        order_id_lst.append("000")
        type_lst.append("000")
        warehouse_id_lst.append("000")
    d = {'מקט': item_id_lst, 'מספר הזמנה': order_id_lst,"סוג":type_lst,"אזור_במחסן":warehouse_id_lst}
    df = pd.DataFrame(data=d)
    return df


def write_to_excel(employee_id, pd_output, first):
    if first:
        pd_output.to_excel("output.xlsx",
                     sheet_name=employee_id, index=False)
        return

    with pd.ExcelWriter("output.xlsx",mode="a",engine="openpyxl") as writer:
        pd_output.to_excel(writer, sheet_name=employee_id,index=False)


def get_lines_by_warehouse_and_order(lines):
    ans = {}
    for line in lines:
        order_id = line.order_id
        warehouse_id = line.location.warehouse_id
        if order_id not in ans:
            ans[order_id] = {}
        if warehouse_id not in ans[order_id]:
            ans[order_id][warehouse_id] = []
        ans[order_id][warehouse_id].append(line)
    return ans

#
# def get_lines_by_item(lines):
#     dict_ = {}
#     for line in lines:
#         item_id = line.item_id
#         if item_id not in dict_.keys():
#             dict_[item_id] = []
#         dict_[item_id].append(line)
#     ans = []
#     for line_list in dict_.values():
#         ans.append(GroupOfItem(item_id=line_list[0].item_id, lines=line_list))
#     return ans
#
# def get_dict_by_street(item_groups,werehouse_id):
#     ans = {}
#     for item_group in item_groups:
#         item_aisle = item_group.street
#         if item_aisle not in ans.keys():
#             ans[item_aisle] = []
#         ans[item_aisle].append(item_group)
#     return ans
#
# def get_item_groups_by_aisle(item_groups, max_groups_per_task, max_transfer_task, max_weight):
#     dict_by_aisle = get_dict_by_aisle(item_groups)
#     aisle_couples = get_aisle_couples()
#     dict_by_aisle_connection = get_dict_by_aisle_connection(dict_by_aisle, aisle_couples)
#     dict_sorted_value_by_volume = get_sorted_value_list_by_volume(dict_by_aisle_connection)
#     transfer_groups_per_aisle = get_transfer_groups_per_aisle(dict_sorted_value_by_volume, max_groups_per_task,
#                                                               max_volume)
#     transfer_groups_list = get_transfer_groups_list(transfer_groups_per_aisle)
#     transfer_groups_list_sorted = sorted(transfer_groups_list, key=lambda x: x.total_volume, reverse=True)
#
#     # --------------
#     selected_transfer_tasks = select_transfer_tasks(transfer_groups_list_sorted, max_transfer_task)
#     selected_transfer_tasks = fix_selected_transfer_tasks(selected_transfer_tasks, dict_sorted_value_by_volume,
#                                                           max_groups_per_task, max_volume)
#     return selected_transfer_tasks
#

def create_pandas_output2(output_):
    item_id_lst = []
    from_lst = []
    to_lst = []
    quantity_lst = []
    order_id_lst = []
    type_lst = []
    employee_id_list = []
    for e in output_:
        for task in output_[e]:
            if isinstance(task, TaskPick):
                item_id_lst.append("")
                from_lst.append("")
                to_lst.append("")
                quantity_lst.append(" ")
                order_id_lst.append(task.id_)
                type_lst.append("ליקוט")
                employee_id_list.append(e)
            else:
                for gi in task.grouped_items:
                    item_id_lst.append(gi.item_id)
                    from_lst.append(gi.location.loc_str)
                    to_lst.append("xx.xx.xx.xx")
                    quantity_lst.append(gi.total_quantity)
                    order_id_lst.append(" ")
                    type_lst.append("העברה")
                    employee_id_list.append(e)
            item_id_lst.append("000")
            from_lst.append("000")
            to_lst.append("000")
            quantity_lst.append("000")
            order_id_lst.append("000")
            type_lst.append("000")
            employee_id_list.append("000")
    d = {'מקט': item_id_lst, 'מאיתור': from_lst, 'לאיתור': to_lst, "כמות": quantity_lst, 'מספר הזמנה': order_id_lst,
         "סוג": type_lst, "עובד": employee_id_list}
    df = pd.DataFrame(data=d)
    return df

def write_to_excel2(pd_output):
    pd_output.to_excel("output_tasks.xlsx", index=False)
