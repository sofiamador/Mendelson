from Enteties import StreetObj, TaskTransfer
from functions import *
from web_services import *
import time

#create_transfer
max_transfer_tasks = 4
center_street = 35

#create_orders
amount_of_one_line_in_street = 3
pick_employee_grade_cut_off = 8
pick_height_employee_grade_cut_off = 8
tail_percantage_to_reallocate = 0.10
max_hour_to_ignore_noon = 13
min_number_of_lines_for_transfer = 2

###input
# get old tasks
old_task_data = get_old_tasks()
lines_per_employee = create_employees_lines_dic(old_task_data)

# read employees
employees_data = read_input("employees.xlsx")
employees = create_employees(employees_data,lines_per_employee , max_hour_to_ignore_noon=max_hour_to_ignore_noon)


employees_height_transfer, employees_pick = get_employees_by_skill(employees)
schedule = init_schedule(employees)

# get stock - create
inventory = get_stock()
inventory_dict = create_inventory_dict_from_json(inventory,center_street)

# get wtasks
lines_input = get_wtasks()
lines, refresh_ids = create_lines_from_json_after_gal(lines_input)

# create transfer tasks
transfer_tasks, item_ids_in_transfer = create_transfer_tasks(lines, inventory_dict, max_transfer_tasks,refresh_ids,min_number_of_lines_for_transfer)
allocate_tasks_to_employees(transfer_tasks, schedule, employees_height_transfer, "transfer")
# ben todo!!!!! to take emp with only רענון


# post - transfer tasks (api)
#post_transfer_tasks(schedule)

# patch -  new location for items in transfers (api)
#patch_upadate_location_for_items(schedule)

# create  allocation
for k in schedule:
    schedule[k]=[]
lines_after_gal_by_order = get_lines_by_order_v2(lines)
lines_after_gal_by_order = filter_orders_that_have_lines_with_items_from_list(lines_after_gal_by_order,item_ids_in_transfer)
# todo remove lines of orders that have those ids
pick_orders,pick_height_orders = get_order_by_ability(lines_after_gal_by_order)
pick_orders_one_line = break_orders_one_line(pick_orders, amount_of_one_line_in_street)
all_pick_orders = pick_orders_one_line+pick_orders

pick_height_orders_one_line = break_orders_one_line(pick_height_orders, amount_of_one_line_in_street)
all_pick_height_orders = pick_height_orders_one_line+pick_height_orders

schedule_pick ,schedule_height_pick = get_schedule_by_skill(schedule,employees_height_transfer)

allocate_pick_orders(all_pick_orders, schedule_pick, employees_pick,pick_employee_grade_cut_off,tail_percantage_to_reallocate)
allocate_pick_height_orders(all_pick_height_orders, schedule_height_pick, employees_height_transfer,pick_height_employee_grade_cut_off,tail_percantage_to_reallocate)


for e,tasks in schedule_pick.items():
    schedule[e] = sorted(tasks,key=lambda x:x.priority)

for e,tasks in schedule_height_pick.items():
    schedule[e] = sorted(tasks,key=lambda x:x.priority)
# patch -  allocate tasks to employees
patch_update_allocation(schedule)
print("end")


