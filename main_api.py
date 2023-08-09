from Enteties import StreetObj, TaskTransfer
from functions import *
from web_services import *
import time


#prioraty
alpha = 0.9 #weight for current amount of line distributed
#create_transfer
max_transfer_tasks = 4
center_street = 35
min_number_of_lines_for_transfer = 5
percentage_of_pallet = 0.5

#create_orders
amount_of_one_line_in_street = 3
pick_employee_grade_cut_off = 8
pick_height_employee_grade_cut_off = 8
jack_employee_grade_cut_off = 8
tail_percantage_to_reallocate = 0.10
max_hour_to_ignore_noon = 13
###input
# get old tasks
old_task_data = get_old_tasks()

# read emloyees input and create employees
employees_data = read_input("employees.xlsx")
employees = create_employees(employees_data,old_task_data , max_hour_to_ignore_noon=max_hour_to_ignore_noon)
employees_pick_height,employees_pick,employees_transfer, employees_jack = get_employees_by_skill(employees)
schedule = init_schedule(employees)

# get stock - create
inventory = get_stock()
inventory_dict = create_inventory_dict_from_json(inventory,center_street)

# get wtasks
lines_input = get_wtasks()
lines, refresh_ids = create_lines_from_json_after_gal(lines_input)

# create transfer tasks
transfer_tasks, item_ids_in_transfer = create_transfer_tasks(lines, inventory_dict, max_transfer_tasks,refresh_ids,min_number_of_lines_for_transfer,percentage_of_pallet)
#TODO what are the options: transfer no pick height? pick height no transfer? employees_pick_height,employees_pick,employees_transfer, employees_jack
allocate_tasks_to_employees(transfer_tasks, schedule, employees_transfer, "transfer")
item_ids_in_transfer = []


# post - transfer tasks (api)
#post_transfer_tasks(schedule)

# patch -  new location for items in transfers (api)
#patch_upadate_location_for_items(schedule)

# create  allocation
for k in schedule:
    schedule[k]=[]
lines_after_gal_by_order = get_lines_by_order_v2(lines)
lines_after_gal_by_order = filter_orders_that_have_lines_with_items_from_list(lines_after_gal_by_order,item_ids_in_transfer)

pick_orders,pick_height_orders,pick_jack_orders = get_order_by_ability(lines_after_gal_by_order)

#################### create unit one line orders #################### create unit one line orders
pick_orders_one_line = break_orders_one_line(pick_orders, amount_of_one_line_in_street)
all_pick_orders = pick_orders_one_line+pick_orders

pick_height_orders_one_line = break_orders_one_line(pick_height_orders, amount_of_one_line_in_street)
all_pick_height_orders = pick_height_orders_one_line+pick_height_orders

pick_jack_one_line = break_orders_one_line(pick_jack_orders, amount_of_one_line_in_street)
all_pick_jack_orders = pick_jack_one_line+pick_jack_orders
#TODO ask Mangasha if to unit jack order to of one lines

#################### create unit one line orders ####################
#employees_pick_height,employees_pick,employees_jack
schedule_pick, schedule_pick_height, schedule_jack = get_schedule_by_skill(schedule,employees_pick_height,employees_pick,employees_jack)

allocate_pick_orders(all_pick_orders, schedule_pick, employees_pick,pick_employee_grade_cut_off,tail_percantage_to_reallocate,alpha)
allocate_pick_height_orders(all_pick_height_orders, schedule_pick_height, employees_pick_height,pick_height_employee_grade_cut_off,tail_percantage_to_reallocate,alpha)
allocate_pick_jack_orders(all_pick_jack_orders, schedule_jack, employees_jack,jack_employee_grade_cut_off,tail_percantage_to_reallocate,alpha)

for e,tasks in schedule_pick.items():
    schedule[e] = sorted(tasks,key=lambda x:x.priority)

for e,tasks in schedule_pick_height.items():
    schedule[e] = sorted(tasks,key=lambda x:x.priority)

for e, tasks in schedule_jack.items():
    schedule[e] = sorted(tasks, key=lambda x: x.priority)
# patch -  allocate tasks to employees
#patch_update_allocation(schedule)
print("end")


