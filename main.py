from enum import Enum
from random import random

from Enteties import StreetObj, TaskTransfer
from functions import *

date_ = "9.5/"

class Scenario(Enum):
    remove_tasks = 1
    create_transfer = 2
    create_orders = 3

scenario = Scenario.create_transfer


def create_excels(schedule):
    if scenario == Scenario.create_transfer:
        file_name_ = "transfer"
    if scenario == Scenario.create_orders:
        file_name_ = "orders"
    first = True

    for employee, tasks in schedule.items():
        pd_output = create_pandas_output(tasks)
        write_to_excel(employee, pd_output, first,file_name_)
        first = False

    pd_output2 = create_pandas_output2(schedule)
    write_to_excel2(pd_output2, file_name_+"_simple.xlsx")



#remove_tasks
amount_to_not_remove = 3
#create_transfer
max_transfer_tasks = 4
center_street = 35


#lb_street_for_transfer = 0
#ub_street_for_transfer = 0

#create_orders
amount_of_one_line_in_street = 3
pick_employee_grade_cut_off = 8
pick_height_employee_grade_cut_off = 8
tail_percantage_to_reallocate = 0.10





if scenario == Scenario.remove_tasks:
    file_name = date_ + "יומן משימות מחסן.xlsx"
    current_tasks_data = read_input(file_name)
    remain, deleted = get_tasks_dict_by_employee(current_tasks_data,amount_to_not_remove)
    list_ids_to_delete = get_list_ids_to_delete(deleted)

    write_csv_list("orders_to_remove.csv",list_ids_to_delete,"orders_to_remove")

    # file_name = date_ + "מסך שאילתה - פירוט משימת מחסן.xlsx"
    # current_lines_data = read_input(file_name)
    # current_lines_data2 = choose_records(current_lines_data, field_name="מספר_משימת_מחסן", values=list_ids_to_delete)
    # write_to_excel2(current_lines_data2, "tasks_to_delete.xlsx")

if scenario == Scenario.create_transfer or scenario == Scenario.create_orders:

    ####------------AGENTS DATA--------------------
    employees_data = read_input("employees.xlsx")
    employees = create_employees(employees_data)
    employees_height_transfer,employees_pick = get_employees_by_skill(employees)
    schedule = init_schedule(employees)


if scenario == Scenario.create_transfer:

    file_name =date_+ "מלאי נוכחי במחסנים.xlsx"
    inventory = read_input(file_name)
    inventory_dict = create_inventory_dict(inventory,center_street)


####------------TASKS DATA--------------------

    file_name =date_+ "סימון שורות הזמנה פתוחות.xlsx"
    lines_input = read_input(file_name)
    lines_before_gal = create_lines_before_gal(lines_input)

    transfer_tasks, item_ids_in_transfer = create_transfer_tasks(lines_before_gal, inventory_dict, max_transfer_tasks)
    allocate_tasks_to_employees(transfer_tasks, schedule, employees_height_transfer, "transfer")
    create_excels(schedule)
    write_csv_list("transfer_id_list.csv",item_ids_in_transfer,"transfer_id_list")
    #if is_with_after_gal:
    #    clear_orders(lines_after_gal_by_order, item_ids_in_transfer)


if scenario == Scenario.create_orders:
    file_name = date_ + "מסך שאילתה - פירוט משימת מחסן.xlsx"
    lines_input2 = read_input(file_name)
    lines_input3 = choose_records(lines_input2, field_name="אזור_במחסן", values=["C1","W1","W2"])
    lines_after_gal = create_lines_from_gal_output(lines_input3)
    lines_after_gal_by_order = get_lines_by_order_v2(lines_after_gal)

    ids_to_remove = read_csv_list("transfer_id_list.csv")


    lines_after_gal_by_order = filter_orders_that_have_lines_with_items_from_list(lines_after_gal_by_order,ids_to_remove)

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
        schedule[e] = sorted(tasks,key=lambda x:x.priority,reverse=True)

    for e,tasks in schedule_height_pick.items():
        schedule[e] = sorted(tasks,key=lambda x:x.priority,reverse=True)


    create_excels(schedule)




