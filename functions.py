import pandas as pd
from Enteties import Line, TaskPick


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


def get_lines_by_item(lines):
    dict_ = {}
    for line in lines:
        item_id = line.item_id
        if item_id not in dict_.keys():
            dict_[item_id] = []
        dict_[item_id].append(line)
    ans = []
    for line_list in dict_.values():
        ans.append(GroupOfItem(item_id=line_list[0].item_id, lines=line_list))
    return ans

def get_dict_by_street(item_groups,werehouse_id):
    ans = {}
    for item_group in item_groups:
        item_aisle = item_group.street
        if item_aisle not in ans.keys():
            ans[item_aisle] = []
        ans[item_aisle].append(item_group)
    return ans

def get_item_groups_by_aisle(item_groups, max_groups_per_task, max_transfer_task, max_weight):
    dict_by_aisle = get_dict_by_aisle(item_groups)
    aisle_couples = get_aisle_couples()
    dict_by_aisle_connection = get_dict_by_aisle_connection(dict_by_aisle, aisle_couples)
    dict_sorted_value_by_volume = get_sorted_value_list_by_volume(dict_by_aisle_connection)
    transfer_groups_per_aisle = get_transfer_groups_per_aisle(dict_sorted_value_by_volume, max_groups_per_task,
                                                              max_volume)
    transfer_groups_list = get_transfer_groups_list(transfer_groups_per_aisle)
    transfer_groups_list_sorted = sorted(transfer_groups_list, key=lambda x: x.total_volume, reverse=True)

    # --------------
    selected_transfer_tasks = select_transfer_tasks(transfer_groups_list_sorted, max_transfer_task)
    selected_transfer_tasks = fix_selected_transfer_tasks(selected_transfer_tasks, dict_sorted_value_by_volume,
                                                          max_groups_per_task, max_volume)
    return selected_transfer_tasks

