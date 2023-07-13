import csv
import random,datetime
import statistics

import pandas as pd
from Enteties import Line, TaskPick, StreetObj, Employee, Location, LineNoLocation, GroupOfItem, TaskTransfer, Order, \
    GroupOfOrders
import matplotlib.pyplot as plt


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


def choose_records_not(data_, field_name, values):
    frames = []
    for v in values:
        data_temp = pd.DataFrame()
        data_temp = data_[data_[field_name] != v]
        frames.append(data_temp)
    data_2 = pd.concat(frames)
    return data_2


def create_files_by_date(df, file_name):
    dates = df["תאריך"].unique()
    for date in dates:
        df_for_date = df[df["תאריך"] == date]
        date_no_time = date.split(" ")[0]
        file_output_name = file_name + "_" + date_no_time + ".xlsx"
        df_for_date.to_excel(file_output_name, sheet_name=date_no_time)


# def fix_normalized_manhattan(locations_list,ans):
#     location_with_max_distance = max(locations_list, key=lambda x: x.manhattan)
#     manhattan_max = location_with_max_distance.manhattan
#
#     for distances in ans.values():
#         for distance in distances:
#             distance.update_normalized_manhattan(manhattan_max)


def create_inventory_dict(lines_input_, center_street):
    ans = {}
    locations_list = []
    for ind in lines_input_.index:
        pallet = lines_input_['פעולה_משטח'][ind]
        item_id = lines_input_['מק_ט'][ind]
        warehouse_id = lines_input_['אזור_במחסן'][ind]
        quantity = lines_input_['יתרה_ביח_קניה_מכירה'][ind]
        location = Location(loc_str=lines_input_['איתור'][ind], warehouse_id=warehouse_id, quantity=quantity,
                            x=center_street, pallet=pallet)
        locations_list.append(location)
        if item_id not in ans:
            ans[item_id] = []
        ans[item_id].append(location)

    # fix_normalized_manhattan(locations_list,ans)

    return ans


def create_inventory_dict_from_json(lines_input_, center_street):
    ans = {}
    locations_list = []
    for line in lines_input_:

        pallet = line["ACTNAME"]
        item_id = line["PARTNAME"]
        warehouse_id = line["STZONECODE"]
        quantity = line["BALANCE"]
        location = Location(loc_str=line["LOCNAME"], warehouse_id=warehouse_id, quantity=quantity,
                            x=center_street, pallet=pallet)
        locations_list.append(location)
        if item_id not in ans:
            ans[item_id] = []
        ans[item_id].append(location)

    # fix_normalized_manhattan(locations_list,ans)
    return ans

def create_employees_lines_dic(old_task_data):
    employee_line = {}
    for task in old_task_data:
        name = task['DOERLOGIN']
        count_of_lines = task['LINES']
        employee_line[name]=employee_line.get(name,0)+count_of_lines
    return employee_line

def create_lines_before_gal(lines_input_):
    lines = []
    for ind in lines_input_.index:
        order_id = lines_input_['הזמנה'][ind]
        item_id = lines_input_['מק_ט'][ind]
        quantity = float(lines_input_['כמות_לליקוט'][ind])

        line = LineNoLocation(item_id=item_id, quantity=quantity, order_id=order_id)
        lines.append(line)
    return lines


def create_lines_from_gal_output(lines_input_):
    lines = []
    for ind in lines_input_.index:
        item_id = lines_input_['מק_ט'][ind]
        order_id = lines_input_['מספר_משימת_מחסן'][ind]
        quantity = float(lines_input_['כמות_בפועל'][ind])
        warehouse_id = lines_input_['אזור_במחסן'][ind]
        location_string = lines_input_['מאיתור'][ind]
        priority = lines_input_['עדיפות'][ind]

        line = Line(item_id, order_id, quantity, warehouse_id, location_string, priority)
        lines.append(line)
    return lines


def create_lines_from_json_after_gal(lines_input_):
    lines = []
    ids_in_move = []
    for task in lines_input_:
        if task["WTASKTYPECODE"]=="PIK":
            order_id = task["WTASKNUM"]
            warehouse_id = task["STZONECODE"]
            if( task["MEND_PRIO2"]>0):
                priority = task["MEND_PRIO2"]
            else:
                priority = task["PRIO"]
            for item in task["WTASKITEMS_SUBFORM"]:
                item_id = item["PARTNAME"]
                quantity = float(item["PTQUANT"])
                location_string = item["LOCNAME"]
                line_number = item["KLINE"]

                line = Line(item_id, order_id, quantity, warehouse_id, location_string, line_number, priority)
                lines.append(line)
        elif task["WTASKTYPECODE"]=="RPI" or task["WTASKTYPECODE"]=="RPL" or task["WTASKTYPECODE"]=="MOV":
            for item in task["WTASKITEMS_SUBFORM"]:
                ids_in_move.append(item["PARTNAME"])

    return lines,ids_in_move


def get_lines_by_items(lines):
    lines_by_item = {}
    for line in lines:
        item_id = line.item_id
        if item_id not in lines_by_item:
            lines_by_item[item_id] = []
        lines_by_item[item_id].append(line)
    return lines_by_item


def fix_normalized_number_of_lines(groupsOfItems):
    goi_max = max(groupsOfItems, key=lambda x: x.number_of_lines)
    number_of_lines_max = goi_max.number_of_lines
    for goi in groupsOfItems:
        goi.update_normalized_number_of_lines(number_of_lines_max)


def fix_normalized_c1_location(groupsOfItems):
    goi_max = max(groupsOfItems, key=lambda x: x.location_c1.manhattan)
    manhattan_max = goi_max.location_c1.manhattan
    for goi in groupsOfItems:
        goi.update_normalized_location_c1(manhattan_max)


def update_the_measure(groupsOfItems):
    for goi in groupsOfItems:
        goi.update_the_measure()


def get_locations_lines_dict(lines_of_item):
    ans = {}
    for line in lines_of_item:
        if line.location not in ans.keys():
            ans[line.location] = []
        ans[line.location].append(line)
    return ans


def get_is_W_in_inventory(locations):
    # TODO GROUP OF ITEMS THAT HAVE NO LOCATION IN W1 W2 ARE NOT IN TRANSFER
    if locations is None:
        return False
    for location in locations:
        if location.warehouse_id!="C1":
            return True
    return False



def create_group_by_items(lines, inventory_dict,refresh_ids,min_number_of_lines_for_transfer):
    groupsOfItems = []
    item_ids_not_in_inventory = []
    lines_by_item = get_lines_by_items(lines)
    for item_id, lines_of_item in lines_by_item.items():
        locations_lines_dict = get_locations_lines_dict(lines_of_item)
        goi = GroupOfItem(item_id, lines_of_item,locations_lines_dict)

        is_W_in_inventory = get_is_W_in_inventory (inventory_dict.get(item_id,None))
        if goi.item_id not in refresh_ids:
            if goi.is_in_c1 and goi.number_of_lines>min_number_of_lines_for_transfer and is_W_in_inventory :
                groupsOfItems.append(goi)
    if len(groupsOfItems)!=0:
        fix_normalized_c1_location(groupsOfItems)

        fix_normalized_number_of_lines(groupsOfItems)

        update_the_measure(groupsOfItems)

        groupsOfItems = sorted(groupsOfItems, key=lambda x: x.the_measure, reverse=True)

    return groupsOfItems, item_ids_not_in_inventory


def create_histogram(objects_list, attribute):
    # Get the values of the attribute for each object in the list
    values = [getattr(obj, attribute) for obj in objects_list]

    # Create the histogram
    plt.hist(values, bins=20)
    plt.xlabel(attribute)
    plt.ylabel('Frequency')
    plt.title('Histogram of ' + attribute)
    plt.show()
    # fig = plt.gcf()
    # fig.savefig(filename)


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
        if street_unique_items > min_amount_of_unique_items:
            # street.ratio_val = ratio_dict[k]
            # street.makat_amount = dict_amount_of_makat_per_street[k]
            # street.order_amount = dict_amount_of_makat_in_orders_per_street[k]
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
    return sorted_dict, dict_amount_of_makat_per_street, dict_amount_of_makat_in_orders_per_street


def get_unique_orders(lines_for_transfer, orders_to_remove):
    for line in lines_for_transfer:
        order_id = line.order_id
        if order_id not in orders_to_remove:
            orders_to_remove.append(order_id)


def get_lines_by_task_transfer(max_makats_in_transfer_task, min_amount_of_unique_items, max_transfer_tasks, streets):
    lines_by_task_transfer = {}
    orders_to_remove = []
    while max_transfer_tasks != 0:
        street = streets[0]
        lines_for_transfer = street.get_lines_for_transfer_task(max_makats_in_transfer_task)
        get_unique_orders(lines_for_transfer, orders_to_remove)
        lines_by_task_transfer[street] = lines_for_transfer
        if street.number_of_unique_items < min_amount_of_unique_items:
            streets.remove(street)
        streets = sorted(streets, key=lambda x: x.ratio_for_fav_street)
        max_transfer_tasks = max_transfer_tasks - 1
        if len(streets) == 0:
            break
    return lines_by_task_transfer, orders_to_remove


def create_streets_from_lines(lines, min_amount_of_unique_items):
    lines_by_street_dict = create_lines_by_street(lines)
    streets = create_streets(lines_by_street_dict, min_amount_of_unique_items=min_amount_of_unique_items)
    return sorted(streets, key=lambda x: x.ratio_for_fav_street)


def create_order_lines_dict_without_transfer(lines_by_order, order_ids_to_remove=[], warehouse_to_exclude=""):
    for order_id, dict_warehouse_and_lines in lines_by_order.items():
        if order_id in order_ids_to_remove:
            del lines_by_order[order_id]


def calculate_average_lines_per_hour(employees):
    # Extract the amount_of_lines_in_shift_per_hour values from employees

    ability_dict = {'pick':[],'pick_height':[]}
    for employee in employees:
        if 'pick' in employee.abilities:
            ability_dict['pick'].append(employee)
        if 'pick_height' in employee.abilities:
            ability_dict['pick_height'].append(employee)

    ans = {'pick':0,'pick_height':0}
    for ability, employees_with_ability in ability_dict.items():
        if len(employees_with_ability)!=0:
            lines_per_hour = [employee.amount_of_lines_in_shift_per_hour for employee in employees_with_ability]
            average_lines_per_hour = statistics.mean(lines_per_hour)
            ans[ability] = average_lines_per_hour
    # Calculate the average using the statistics module

    return ans

def create_employees(employees_data,old_tasks, max_hour_to_ignore_noon):
    employees_ = []
    HOUR = datetime.datetime.now().hour  # the current hour
    MINUTE = datetime.datetime.now().minute  # the current minute
    tnow = HOUR + (MINUTE/60)

    #HOUR = 11
    #MINUTE = 30
    #tnow = HOUR + (MINUTE/60)

    start_time_dict = {}
    for ind in employees_data.index:
        employee_id = employees_data['שם מלא'][ind]
        role = employees_data['תפקיד'][ind]
        pick_grade = int(employees_data['ליקוט'][ind])
        transfer_grade = int(employees_data['רענון'][ind])
        pick_height_grade = int(employees_data['גובה'][ind])
        start_time = float(employees_data['שעת_התחלה'][ind])

        end_shift_time = float(employees_data['שעת_סיום'][ind])
        amount_of_lines = old_tasks.get(employee_id,0)
        abilities = {}
        if pick_grade != 0:
            abilities["pick"] = pick_grade
        if transfer_grade != 0:
            abilities["transfer"] = transfer_grade
        if pick_height_grade != 0:
            abilities["pick_height"] = pick_height_grade

        if start_time<tnow<end_shift_time:
            employee = Employee(id_=employee_id, abilities=abilities, role=role,start_time=start_time,end_shift_time = end_shift_time,amount_of_lines=amount_of_lines)
            employee.update_amount_of_lines_in_shift_per_hour(tnow)
            employees_.append(employee)

            if start_time not in start_time_dict.keys():
                start_time_dict[start_time] = []
            start_time_dict[start_time].append(employee)

    if 12<=HOUR<=max_hour_to_ignore_noon:
        min_start_time = min(start_time_dict.keys())
        max_start_time = max(start_time_dict.keys())

        employees_min = start_time_dict[min_start_time]
        dict_ability_avg = calculate_average_lines_per_hour(employees_min)

        employees_max = start_time_dict[max_start_time]
        for employee in employees_max:
            if 'pick' in  employee.abilities.keys():
                employee.amount_of_lines_in_shift_per_hour = dict_ability_avg['pick']
            elif "pick_height" in  employee.abilities.keys():
                employee.amount_of_lines_in_shift_per_hour = dict_ability_avg["pick_height"]
            else:
                raise Exception("something is wrong with abilities")

    return employees_


def get_random_schedule(employees, pick_tasks, transfer_tasks):
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
    order_id_lst = []
    type_lst = []
    warehouse_id_lst = []
    locations = []
    pallets = []

    for task in output_tasks:
        if isinstance(task, Order):
            if isinstance(task, GroupOfOrders):
                counter = 0
                for order in task.orders:
                    counter = counter + 1
                    if counter == len(task.orders):
                        item_id_lst = item_id_lst + [order.lines[0].item_id]
                        type_lst = type_lst + ["ליקוט_מחובר"]
                        warehouse_id_lst = warehouse_id_lst + [order.lines[0].location.warehouse_id]
                        order_id_lst = order_id_lst + [task.order_id]
                        locations = locations + [order.lines[0].location.loc_str]
                        pallets.append("000")
                    else:
                        item_id_lst = item_id_lst + [order.lines[0].item_id, "xxx"]
                        type_lst = type_lst + ["ליקוט_מחובר", "xxx"]
                        warehouse_id_lst = warehouse_id_lst + [order.lines[0].location.warehouse_id, "xxx"]
                        order_id_lst = order_id_lst + [task.order_id, "xxx"]
                        locations = locations + [order.lines[0].location.loc_str, "xxx"]
                        pallets = pallets + ["000", "xxx"]
            else:
                for line in task.lines:
                    item_id_lst.append(line.item_id)
                    type_lst.append("ליקוט")
                    warehouse_id_lst.append(line.location.warehouse_id)
                    order_id_lst.append(task.order_id)
                    locations.append(line.location.loc_str)
                    pallets.append("000")
        else:
            item_id_lst.append(task.item_id)
            type_lst.append("העברה")
            warehouse_id_lst.append(task.location.warehouse_id)
            order_id_lst.append("000")
            locations.append(task.location.loc_str)
            pallets.append(task.location.pallet)
        item_id_lst.append("000")
        order_id_lst.append("000")
        type_lst.append("000")
        warehouse_id_lst.append("000")
        locations.append("000")
        pallets.append("000")

    d = {'מקט': item_id_lst, 'מספר הזמנה': order_id_lst, "סוג": type_lst, "אזור_במחסן": warehouse_id_lst,
         "מיקום": locations, "משטח": pallets}
    df = pd.DataFrame(data=d)
    return df


def write_to_excel(employee_id, pd_output, first, file_name_):
    if first:
        pd_output.to_excel(file_name_ + ".xlsx",
                           sheet_name=employee_id, index=False)
        return

    with pd.ExcelWriter(file_name_ + ".xlsx", mode="a", engine="openpyxl") as writer:
        pd_output.to_excel(writer, sheet_name=employee_id, index=False)


def get_lines_by_order_v2(lines):
    ans = {}
    for line in lines:
        order_id = line.order_id
        if order_id not in ans:
            ans[order_id] = []
        ans[order_id].append(line)
    return ans


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
    order_id_lst = []
    type_lst = []
    employee_id_list = []
    pallets = []
    for e in output_:
        for task in output_[e]:
            if isinstance(task, GroupOfOrders):
                for order in task.orders:
                    item_id_lst.append("")
                    from_lst.append("")
                    to_lst.append("")
                    order_id_lst.append(order.order_id)
                    type_lst.append("ליקוט יחד")
                    employee_id_list.append(e)
                    pallets.append("000")
            elif isinstance(task, TaskTransfer):
                item_id_lst.append(task.item_id)
                from_lst.append(task.location.loc_str)
                to_lst.append("RL.01")
                order_id_lst.append(" ")
                type_lst.append("העברה")
                employee_id_list.append(e)
                pallets.append(task.location.pallet)
            else:
                item_id_lst.append("")
                from_lst.append("")
                to_lst.append("")
                order_id_lst.append(task.order_id)
                type_lst.append("ליקוט")
                employee_id_list.append(e)
                pallets.append("000")
            # item_id_lst.append("000")
            # from_lst.append("000")
            # to_lst.append("000")
            # order_id_lst.append("000")
            # type_lst.append("000")
            # employee_id_list.append("000")
            # pallets.append("000")
    d = {'מקט': item_id_lst, 'מאיתור': from_lst, 'לאיתור': to_lst, 'מספר הזמנה': order_id_lst,
         "סוג": type_lst, "עובד": employee_id_list, "משטח": pallets}
    df = pd.DataFrame(data=d)
    return df


def write_to_excel2(pd_output, file_name):
    pd_output.to_excel(file_name, index=False)


def get_group_of_items_for_tasks_list(group_of_items_list, max_transfer_tasks):
    groups_for_transfer = []
    for i in range(max_transfer_tasks):
        max_group_of_items = max(group_of_items_list, key=lambda x: x.the_measure)
        groups_for_transfer.append(max_group_of_items)
        group_of_items_list.remove(max_group_of_items)
    return groups_for_transfer


#
# def get_max_location_in_groupOfItems(goi):
#     locations = goi.locations
#     distance_max = max(locations, key=lambda x: x.manhattan).manhattan
#     quantity_max = max(locations, key=lambda x: x.quantity).quantity
#     for location in locations:
#         if  location.warehouse_id == "C1":
#             goi.locations.remove(location)
#         else:
#             location.update_measure_for_group_of_items(distance_max, quantity_max)
#     max_location = max(locations, key=lambda x: x.measure_for_group_of_items)
#     return max_location


def clear_orders(lines_by_order, item_ids_in_transfer):
    orders_to_remove = []
    for order_id, lines in lines_by_order.items():
        for line in lines:
            if line.item_id in item_ids_in_transfer:
                orders_to_remove.append(order_id)
                break

    for order_id in orders_to_remove:
        del lines_by_order[order_id]


def get_w_locations(locations_no_c1):
    ans = {"W1": [], "W2": []}
    for location in locations_no_c1:
        ans[location.warehouse_id].append(location)

    return ans


def get_locations_to_cover_quantities(goi):
    ans = []
    quantity_required = goi.total_quantity_required_from_w
    locations_by_warehouse_id = get_w_locations(goi.locations_no_c1)

    locations_w1 = sorted(locations_by_warehouse_id["W1"], key=lambda x: x.quantity, reverse=True)
    for location in locations_w1:
        goi.get_lines_per_location(location)
        quantity_required = quantity_required - location.quantity
        ans.append(location)
        if quantity_required <= 0:
            return ans

    locations_w2 = sorted(locations_by_warehouse_id["W2"], key=lambda x: x.quantity, reverse=True)
    for location in locations_w2:
        quantity_required = quantity_required - location.quantity
        ans.append(location)
        if quantity_required <= 0:
            return ans

    return ans



def create_transfer_tasks(lines, inventory_dict, max_transfer_tasks,refresh_ids,min_number_of_lines_for_transfer):
    transfer_tasks = []
    group_of_items_list, item_ids_not_in_inventory = create_group_by_items(lines, inventory_dict,refresh_ids,min_number_of_lines_for_transfer)
    # create_histogram(group_of_items_list, "the_measure")
    number_of_transfer_tasks = min(len(group_of_items_list), max_transfer_tasks)
    group_of_items_for_tasks_list = get_group_of_items_for_tasks_list(group_of_items_list,number_of_transfer_tasks)
    item_ids_in_transfer = []
    counter = 0
    locations_in_tasks = []

    for goi in group_of_items_for_tasks_list:
        item_ids_in_transfer.append(goi.item_id)
        item_id = goi.item_id
        total_quantity = 0
        for line in goi.lines:
            total_quantity += line.quantity
        locations = inventory_dict.get(item_id,None)
        locations = sorted(locations,key = lambda x: x.quantity,reverse=True)

        selected_locations = []
        for location in locations:
            selected_locations.append(location)
            total_quantity = total_quantity-location.quantity
            if total_quantity<=0:
                break
        transfer_tasks.append(TaskTransfer(item_id, selected_locations,goi.lines, counter))
    return transfer_tasks, item_ids_in_transfer


def get_order_by_ability(lines_after_gal_by_order):
    pick_orders = []
    pick_height_orders = []
    for order, lines in lines_after_gal_by_order.items():
        order_pick_lines = []
        order_pick_height_lines = []
        for line in lines:
            warehouse_id = line.location.warehouse_id
            if warehouse_id == "C1":
                order_pick_lines.append(line)
            else:
                order_pick_height_lines.append(line)

        if len(order_pick_lines) != 0:
            pick_orders.append(Order(order, 'pick', order_pick_lines))

        if len(order_pick_height_lines) != 0:
            pick_height_orders.append(Order(order, 'pick_height', order_pick_height_lines))

    return pick_orders, pick_height_orders


def get_employees_by_skill(employees):
    employees_height_transfer = []
    employees_pick = []
    for employee in employees:
        if "pick" in employee.abilities:
            employees_pick.append(employee)
        else:
            employees_height_transfer.append(employee)
    return employees_height_transfer, employees_pick


def get_attribute_list(objects, attribute):
    attribute_list = []
    for obj in objects:
        attribute_value = getattr(obj, attribute, None)
        if attribute_value is not None:
            attribute_list.append(attribute_value)
    return attribute_list



def allocate_tasks_to_employees(transfer_tasks, schedule, employees_height_transfer, ability_str):
    ids_ = get_attribute_list(employees_height_transfer, "id_")
    employees_tasks_amount = {}
    for employee_id, tasks in schedule.items():
        if employee_id in ids_:
            employees_tasks_amount[employee_id] = 0  # len(schedule[employee_id])

    for task in transfer_tasks:
        if (len(employees_tasks_amount) > 0):  # TODO @BEN
            min_amount_of_tasks = min(employees_tasks_amount.values())
            employees_with_min_tasks = []
            for employee in employees_height_transfer:
                if employees_tasks_amount[employee.id_] == min_amount_of_tasks:
                    employees_with_min_tasks.append(employee)
            employee_selected = max(employees_with_min_tasks, key=lambda x: x.abilities[ability_str])
            schedule[employee_selected.id_].append(task)
            employees_tasks_amount[employee_selected.id_] = employees_tasks_amount[employee_selected.id_] + 1


def get_employee_object(employees,employee_id):
    for employee in employees:
        if employee.id_ ==employee_id:
            return employee
    raise Exception("did not find employee with relevant id")


def allocate_tasks_to_employees_v2(tasks, schedule, employees, ability_str):
    ids_ = get_attribute_list(employees, "id_")
    employees_lines_amount_up_to_now_normalized = {}
    amount_of_lines_in_schedule_per_emp = {}

    for employee_id in schedule.keys():
        if employee_id in ids_:
            employee = get_employee_object(employees,employee_id)
            employees_lines_amount_up_to_now_normalized[employee_id] = employee.amount_of_lines_in_shift_per_hour  # len(schedule[employee_id])
            amount_of_lines_in_schedule_per_emp[employee_id] = 0

    grade_to_distribute = {}

    max_amount_of_lines =  max(employees_lines_amount_up_to_now_normalized.values())
    for employee_id in employees_lines_amount_up_to_now_normalized.keys():
        if max_amount_of_lines ==0:
            employees_lines_amount_up_to_now_normalized[employee_id] = 0  # len(schedule[employee_id])
        else:
            employees_lines_amount_up_to_now_normalized[employee_id] = employee.amount_of_lines_in_shift_per_hour/max_amount_of_lines  # len(schedule[employee_id])
        grade_to_distribute[employee_id] = employees_lines_amount_up_to_now_normalized[employee_id] * amount_of_lines_in_schedule_per_emp[employee_id]

    max_lines_distribute_in_schedule = None

    for task in tasks:
        if (len(employees_lines_amount_up_to_now_normalized) > 0):  # TODO @BEN

            min_amount_of_tasks = min(grade_to_distribute.values())
            employees_with_min_tasks = []
            for employee in employees:
                if grade_to_distribute[employee.id_] == min_amount_of_tasks:
                    employees_with_min_tasks.append(employee)


            employee_selected = max(employees_with_min_tasks, key=lambda x: x.abilities[ability_str])
            schedule[employee_selected.id_].append(task)
            amount_of_lines_in_schedule_per_emp[employee_selected.id_] =  amount_of_lines_in_schedule_per_emp[employee_selected.id_] + task.amount_of_lines
            max_lines_distribute_in_schedule = max(amount_of_lines_in_schedule_per_emp.values())
            for employee in employees:
                id_ = employee.id_
                if max_lines_distribute_in_schedule!=0:
                    grade_to_distribute[id_]  = employees_lines_amount_up_to_now_normalized[id_]+(amount_of_lines_in_schedule_per_emp[employee_selected.id_]/max_lines_distribute_in_schedule)

            #employees_lines_amount_up_to_now_normalized[employee_selected.id_] = employees_lines_amount_up_to_now_normalized[employee_selected.id_] + task.amount_of_lines

def init_schedule(employees):
    schedule = {}
    for e in employees:
        schedule[e.id_] = []
    return schedule


def cumulative_distribution_function(pick_orders):
    sum_of_all_lines = sum(getattr(obj, "amount_of_lines") for obj in pick_orders)
    pick_orders_sorted = sorted(pick_orders, key=lambda x: x.amount_of_lines)
    sum_of_lines = 0
    for pick_order in pick_orders_sorted:
        sum_of_lines = sum_of_lines + pick_order.amount_of_lines
        pick_order.update_cumulative_distribution(sum_of_lines, sum_of_all_lines)


def get_employees_by_cut_off(employees_pick, pick_employee_grade_cut_off, ability_str):
    skilled_employees = []
    other_employees = []

    for e in employees_pick:
        if ability_str in e.abilities: # BEN
            pick_grade = e.abilities[ability_str]
            if pick_grade < pick_employee_grade_cut_off:
                other_employees.append(e)
            else:
                skilled_employees.append(e)

    return skilled_employees, other_employees


def get_orders_by_cut_off(pick_orders, pick_percentage_cut_off):
    large_amount_line_orders = []
    other_amount_line_orders = []
    for order in pick_orders:
        cumulative_value = order.cumulative_value
        if cumulative_value < pick_percentage_cut_off:
            other_amount_line_orders.append(order)
        else:
            large_amount_line_orders.append(order)

    return large_amount_line_orders, other_amount_line_orders


def sum_attribute(objects, attribute):
    """Sums the value of a specified attribute for each object in a list."""
    total = 0
    for obj in objects:
        total += getattr(obj, attribute)
    return total


def filter_list_by_attribute(lst, attribute, value):
    larger_values = []
    smaller_values = []
    """Filters a list of objects based on a given attribute value."""
    # Create an empty list to store the filtered objects
    filtered_lst = []
    # Loop through the objects in the list
    for obj in lst:
        # Check if the object has the given attribute and value
        if hasattr(obj, attribute) and getattr(obj, attribute) > value:
            # If the object has the attribute and value, add it to the filtered list
            larger_values.append(obj)
        else:
            smaller_values.append(obj)
    # Return the filtered list
    return larger_values, smaller_values


def cut_orders_by_skill(orders, skilled_employees, other_employees, tail_percantage_to_reallocate):
    orders, orders_to_fix = filter_list_by_attribute(orders, "cumulative_value", tail_percantage_to_reallocate)
    total_amount_of_lines = sum_attribute(orders, "amount_of_lines")
    lines_per_employee = total_amount_of_lines / (len(skilled_employees) + len(other_employees))

    orders = sorted(orders, key=lambda x: x.amount_of_lines)
    amount_of_lines_for_other_employees = len(other_employees) * lines_per_employee
    orders_for_others = []
    orders_for_skilled = []
    sum_ = 0
    for order in orders:
        sum_ = sum_ + order.amount_of_lines
        if sum_ < amount_of_lines_for_other_employees or order.priority>5:
            orders_for_others.append(order)
        else:
            orders_for_skilled.append(order)

    return orders_for_skilled, orders_for_others, orders_to_fix


def find_min_key_by_attr_sum(data, attr):
    """Returns the key with the minimum sum of the specified attribute in each list."""
    min_key = None
    min_sum = float('inf')  # initialize with a high value

    for key, lst in data.items():
        attr_sum = sum(getattr(obj, attr) for obj in lst)

        if attr_sum < min_sum:
            min_key = key
            min_sum = attr_sum

    return min_key


def use_list_of_order_to_fix_for_balance(schedule, orders_to_fix):
    for order in orders_to_fix:
        min_key = find_min_key_by_attr_sum(schedule, "amount_of_lines")
        schedule[min_key].append(order)


def allocate_pick_orders(pick_orders, schedule, employees_pick, pick_employee_grade_cut_off,
                         tail_percantage_to_reallocate):
    cumulative_distribution_function(pick_orders)
    # create_histogram(pick_orders, "amount_of_lines", filename="hist_pick_amount_of_lines")
    # create_histogram(pick_orders, "cumulative_value", filename="hist_pick_cumulative_value")
    skilled_employees, other_employees = get_employees_by_cut_off(employees_pick, pick_employee_grade_cut_off, "pick")
    # if is_calculate_percentage_cut_off:
    orders_for_skilled, orders_for_other, orders_to_fix = cut_orders_by_skill(pick_orders, skilled_employees,
                                                                              other_employees,
                                                                              tail_percantage_to_reallocate)
    # else:
    #    large_amount_line_orders,other_amount_line_orders = get_orders_by_cut_off(pick_orders,pick_percentage_cut_off)

    allocate_tasks_to_employees_v2(tasks=orders_for_skilled, schedule=schedule, employees=skilled_employees, ability_str ="pick" )
    allocate_tasks_to_employees_v2(orders_for_other, schedule, other_employees, "pick")

    #allocate_tasks_to_employees(orders_for_skilled, schedule, skilled_employees, "pick")
    #allocate_tasks_to_employees(orders_for_other, schedule, other_employees, "pick")
    use_list_of_order_to_fix_for_balance(schedule, orders_to_fix)


def allocate_pick_height_orders(pick_height_orders, schedule, employees_height_transfer,
                                pick_height_employee_grade_cut_off, tail_percantage_to_reallocate):
    cumulative_distribution_function(pick_height_orders)
    # create_histogram(pick_height_orders, "amount_of_lines", filename="hist_pick_height_amount_of_lines")
    # create_histogram(pick_height_orders, "cumulative_value",filename="hist_pick_height_cumulative_value")
    skilled_employees, other_employees = get_employees_by_cut_off(employees_height_transfer,
                                                                  pick_height_employee_grade_cut_off, "pick_height")
    # if is_calculate_percentage_cut_off:
    orders_for_skilled, orders_for_other, orders_to_fix = cut_orders_by_skill(pick_height_orders, skilled_employees,
                                                                              other_employees,
                                                                              tail_percantage_to_reallocate)
    # else:
    #    large_amount_line_orders,other_amount_line_orders = get_orders_by_cut_off(pick_height_orders,pick_height_percentage_cut_off)
    if len(skilled_employees)!=0:
        allocate_tasks_to_employees_v2(orders_for_skilled, schedule, skilled_employees, "pick_height")
    if len(other_employees) != 0:
        allocate_tasks_to_employees_v2(orders_for_other, schedule, other_employees, "pick_height")
    use_list_of_order_to_fix_for_balance(schedule, orders_to_fix)


def create_data_dict(schedule):
    data_dict = {}
    for emp, tasks in schedule.items():
        sum_ = 0
        for task in tasks:
            if isinstance(task, Order):
                sum_ = sum_ + task.amount_of_lines
            else:
                sum_ = sum_ + 1
        data_dict[emp] = sum_
    return data_dict


def create_bar_from_dict(schedule, title_):
    data_dict = create_data_dict(schedule)
    fig, ax = plt.subplots()
    # Create the bar graph
    ax.bar(data_dict.keys(), data_dict.values())
    # Set the axis labels and title
    ax.set_xlabel('Employee')
    ax.set_ylabel('Amount of lines')
    ax.set_title('Amount of Lines Per Employee ' + title_)
    # Show the plot
    plt.show()


def get_schedule_by_skill(schedule, employees_height_transfer):
    schedule_height_pick = {}
    schedule_pick = {}
    for id_, tasks in schedule.items():
        if id_ in get_attribute_list(employees_height_transfer, "id_"):
            schedule_height_pick[id_] = tasks
        else:
            schedule_pick[id_] = tasks
    return schedule_pick, schedule_height_pick


def get_orders_with_one_line(orders):
    ans = []
    for order in orders:
        if len(order.lines) == 1:
            ans.append(order)
    return ans


def get_orders_by_street(orders_one_line):
    ans = {}
    for order in orders_one_line:
        for line in order.lines:
            street = line.location.street
            if street not in ans:
                ans[street] = []
            ans[street].append(order)
    return ans


def break_orders_one_line(orders_input, amount_of_one_line_in_street):
    orders_one_line = get_orders_with_one_line(orders_input)
    orders_by_street = get_orders_by_street(orders_one_line)
    sorted_dict = {k: orders_by_street[k] for k in
                   sorted(orders_by_street, key=lambda k: len(orders_by_street[k]), reverse=True)}
    all_goos = []
    for street, orders_ in sorted_dict.items():
        all_goos.append(GroupOfOrders(street, orders_))
    # create_histogram(all_goos,"amount_of_orders")

    ans = []
    for street, orders_ in sorted_dict.items():
        if len(orders_) >= amount_of_one_line_in_street:
            ans.append(GroupOfOrders(street, orders_))
            for order in orders_:
                orders_input.remove(order)

    return ans


def create_current_tasks(tasks_input_):
    tasks = []
    for ind in tasks_input_.index:
        task_id = tasks_input_['מספר_משימת_מחסן'][ind]
        status = tasks_input_['סטטוס'][ind]
        employee = tasks_input_['לטיפול'][ind]
        importance = tasks_input_['עדיפות'][ind]
        is_picked = tasks_input_['נלקח_למסופון_ידני'][ind]
        warehouse_id = tasks_input_['אזור_במחסן'][ind]

        if is_picked != "Y":
            line = TaskPick(order_id=task_id, employee=employee, status=status, importance=importance,
                            warehouse_id=warehouse_id)
            tasks.append(line)
    return tasks


def create_current_task_dict_by_id(current_tasks, amount_to_not_remove):
    ans_remain = {}
    ans_deleted = {}
    for current_task in current_tasks:
        if current_task.employee not in ans_remain:
            ans_remain[current_task.employee] = []
            ans_deleted[current_task.employee] = []
        ans_remain[current_task.employee].append(current_task)
        ans_deleted[current_task.employee].append(current_task)

    for employee, tasks in ans_remain.items():
        ans_remain[employee] = sorted(tasks, key=lambda x: int(x.importance), reverse=True)
        ans_deleted[employee] = sorted(tasks, key=lambda x: int(x.importance), reverse=True)
        if len(ans_remain[employee]) >= amount_to_not_remove:
            ans_remain[employee] = ans_remain[employee][:amount_to_not_remove]
            ans_deleted[employee] = ans_deleted[employee][amount_to_not_remove:]

    return ans_remain, ans_deleted


def get_tasks_dict_by_employee(current_tasks_data, amount_to_not_remove):
    current_tasks_data_2 = choose_records(current_tasks_data, field_name="אזור_במחסן", values=["C1", "W1", "W2"])

    bodek_3 = choose_records(current_tasks_data_2, field_name="לטיפול", values=["בודק3"])
    bodek_3 = create_current_tasks(bodek_3)

    bodek_3_not = choose_records_not(current_tasks_data_2, field_name="לטיפול", values=["בודק3"])
    bodek_3_not = create_current_tasks(bodek_3_not)

    remain, deleted = create_current_task_dict_by_id(bodek_3_not, amount_to_not_remove)

    for task in bodek_3:
        if task.employee not in deleted:
            deleted[task.employee] = []
        deleted[task.employee].append(task)

    return remain, deleted


def get_list_ids_to_delete(deleted):
    ans = []
    for tasks_list in deleted.values():
        for task in tasks_list:
            ans.append(task.id_)
    return ans


def write_csv_list(file_name_, list_, title_):
    with open(file_name_, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([title_])
        for item in list_:
            writer.writerow([item])


def read_csv_list(file_name_):
    data = []

    with open(file_name_, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        for row in reader:
            data.append(row[0])
    return data


def get_orders_to_remove_in_transfer(lines_after_gal_by_order, ids_to_remove):
    orders_to_remove = []
    for order_id, lines in lines_after_gal_by_order.items():
        for line in lines:
            if line.item_id in ids_to_remove:
                orders_to_remove.append(order_id)
                break
    return orders_to_remove


def filter_orders_that_have_lines_with_items_from_list(lines_after_gal_by_order, ids_to_remove):
    orders_to_remove = get_orders_to_remove_in_transfer(lines_after_gal_by_order, ids_to_remove)
    ans = {key: value for key, value in lines_after_gal_by_order.items() if key not in orders_to_remove}
    return ans
