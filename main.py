from functions import *

is_with_transfer_tasks = False
max_groups_per_task_transfer = 4
max_transfer_task = 2


# file_name = "input.xlsx"
# lines_input = read_input(file_name)
# lines_input2 = choose_records(lines_input, field_name="אזור_במחסן", values=["C1","W1","W2"])
# print(lines_input2.info)
# create_files_by_date(lines_input2)

date ="2023-01-08"
dir = "input_by_date/"
lines_input = read_input(dir + "input_" + date + ".xlsx")
print(lines_input.info)
lines = create_lines( lines_input)
pick_tasks = get_lines_by_order(lines)
##pick_tasks = remove_pick_tasks_that_are_finished(pick_tasks)

item_groups = get_lines_by_item(lines)
if is_with_transfer_tasks:
    transfer_tasks = get_item_groups_by_aisle(item_groups=item_groups, max_groups_per_task=max_groups_per_task_transfer,
                                              max_transfer_task=max_transfer_task)
else:
    transfer_tasks = []

