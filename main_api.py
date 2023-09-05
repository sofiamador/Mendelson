from Enteties import StreetObj, TaskTransfer
from functions import *
from web_services import *
import time, datetime

while True:
    # get old tasks
    old_task_data = get_old_tasks()

    # read employees input and create employees
    employees_data = read_input("employees.xlsx")
    employees = create_employees(employees_data, old_task_data)
    employees_pick_height, employees_pick, employees_transfer, employees_jack = get_employees_by_skill(employees)
    schedule = init_schedule(employees)

    # get stock - create
    inventory = get_stock()
    inventory_dict = create_inventory_dict_from_json(inventory)

    # get wtasks
    lines_input = get_wtasks()
    lines, refresh_ids = create_lines_from_json_after_gal(lines_input)

    # Use the filter() function to filter out lines with is_store set to False
    if not is_with_store:
        filtered_lines = list(filter(lambda line: line.is_store, lines))
        lines = [item for item in lines if item not in filtered_lines]

    ## create transfer tasks
    inventory_no_c = clear_c_from_inventory_dict(inventory_dict)
    transfer_tasks, item_ids_in_transfer = create_transfer_tasks(lines, inventory_no_c, refresh_ids)
    if len(transfer_tasks) > 0 and len(employees_pick_height) > 1 :
        print("transfer" + str(len(transfer_tasks)))
        if len(employees_transfer) == 0:
            employees_transfer.append(pick_employee_for_transfer(employees_pick_height,employees_data))
        allocate_tasks_to_employees(transfer_tasks, schedule, employees_transfer, "transfer")



        # post - transfer tasks (api)
        post_transfer_tasks(schedule)

        # patch -  new location for items in transfers (api)
        patch_upadate_location_for_items(schedule)
        for emp in employees_transfer:
            employees.remove(emp)
            del schedule[emp.id_]

    # create  allocation
    item_ids_in_transfer = []
    for k in schedule:
        schedule[k] = []
    lines_after_gal_by_order = get_lines_by_order_v2(lines)
    lines_after_gal_by_order = filter_orders_that_have_lines_with_items_from_list(lines_after_gal_by_order,
                                                                                  item_ids_in_transfer)
    lines_after_gal_by_order = filter_first_allocated_orders(lines_after_gal_by_order,employees,schedule)
    pick_orders, pick_height_orders, pick_jack_orders = get_order_by_ability(lines_after_gal_by_order)

    #################### create unit one line orders #################### create unit one line orders
    pick_orders_one_line = break_orders_one_line(pick_orders)
    all_pick_orders = pick_orders_one_line + pick_orders

    pick_height_orders_one_line = break_orders_one_line(pick_height_orders)
    all_pick_height_orders = pick_height_orders_one_line + pick_height_orders

    pick_jack_one_line = break_orders_one_line(pick_jack_orders)
    all_pick_jack_orders = pick_jack_one_line + pick_jack_orders

    # TODO ask Mangasha if to unit jack order to of one lines

    #################### create unit one line orders ####################
    schedule_pick, schedule_pick_height, schedule_jack = get_schedule_by_skill(schedule, employees_pick_height,
                                                                               employees_pick, employees_jack)
    if len(employees_pick) != 0:
        allocate_pick_orders(all_pick_orders, schedule_pick, employees_pick)
    if len(employees_pick_height) != 0:
        allocate_pick_height_orders(all_pick_height_orders, schedule_pick_height, employees_pick_height)
    if len(employees_jack) != 0:
        allocate_pick_jack_orders(all_pick_jack_orders, schedule_jack, employees_jack)

    for e, tasks in schedule_pick.items():
        schedule[e] = sorted(tasks, key=lambda x: x.priority)

    for e, tasks in schedule_pick_height.items():
        schedule[e] = sorted(tasks, key=lambda x: x.priority)

    for e, tasks in schedule_jack.items():
        schedule[e] = sorted(tasks, key=lambda x: x.priority)

    # patch -  allocate tasks to employees
    print("before: ",datetime.datetime.now())
    patch_update_allocation(schedule)
    print("after: ", datetime.datetime.now())

    time.sleep(480)
