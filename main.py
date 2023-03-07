from random import random

from Enteties import StreetObj, TaskTransfer
from functions import *

is_with_transfer_tasks = True
max_transfer_tasks = 4
max_makats_in_transfer_task = 4
min_amount_of_unique_items = 4


# file_name = "input.xlsx"
# lines_input = read_input(file_name)
# lines_input2 = choose_records(lines_input, field_name="אזור_במחסן", values=["C1","W1","W2"])
# print(lines_input2.info)
# create_files_by_date(lines_input2)

####------------AGENTS DATA--------------------
employees_data = read_input("employees.xlsx")
employees = create_employees(employees_data)

####------------TASKS DATA--------------------
date ="2023-01-08"
dir = "input_by_date/"

lines_input = read_input(dir + "input_" + date + ".xlsx")
print(lines_input.info)

#ratio_dict,dict_amount_of_makat_per_street,dict_amount_of_makat_in_orders_per_street = sort_streets_by_ratio_makat_per_street_amount_of_makat_in_orders_per_street(lines_input)

lines = create_lines( lines_input)
lines_by_warehouse_and_order = get_lines_by_warehouse_and_order(lines)
lines_to_remove = []


transfer_tasks = []
pick_tasks = []


id_counter = 0
if is_with_transfer_tasks:
    streets = create_streets_from_lines (lines,min_amount_of_unique_items)
    lines_by_task_transfer,order_ids_to_remove_in_c1 = get_lines_by_task_transfer(max_makats_in_transfer_task,min_amount_of_unique_items,max_transfer_tasks,streets)
    for k,v in lines_by_task_transfer.items():
        id_counter = id_counter +1
        transfer_tasks.append(TaskTransfer(k,v,id_counter))
        create_order_lines_dict_without_transfer(lines_by_warehouse_and_order,order_ids_to_remove_in_c1,"C1")
else:
    order_lines_dict_without_transfer = create_order_lines_dict_without_transfer(lines)

for order_id,warehouse_lines_dict in lines_by_warehouse_and_order.items():
    for warehouse_id, lines_for_task  in warehouse_lines_dict.items():
        id_counter = id_counter + 1
        pick_tasks.append(TaskPick(order_id,lines_for_task,id_counter,warehouse_id))

schedule = get_random_schedule(employees,pick_tasks, transfer_tasks)



first = True
for employee,tasks in schedule.items():
    pd_output = create_pandas_output(tasks)
    write_to_excel(employee,pd_output,first)
    first = False#


# pick_tasks = get_lines_by_order(lines)
# ##pick_tasks = remove_pick_tasks_that_are_finished(pick_tasks)
#
# item_groups = get_lines_by_item(lines)
# if is_with_transfer_tasks:
#     transfer_tasks = get_item_groups_by_aisle(item_groups=item_groups, max_groups_per_task=max_groups_per_task_transfer,
#                                               max_transfer_task=max_transfer_task)
# else:
#     transfer_tasks = []

pd_output2 = create_pandas_output2(schedule)
write_to_excel2(pd_output2)