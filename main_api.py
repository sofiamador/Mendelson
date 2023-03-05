from enum import Enum
from Enteties import StreetObj, TaskTransfer
from functions import *

date_ = "9.5/"

class Scenario(Enum):
    remove_tasks = 1
    create_transfer = 2
    create_orders = 3

scenario = Scenario.create_transfer




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





###input
# get stock - create

# get wtasks

# create transfer tasks
# post - transfer tasks (api)
# patch -  new location for items in transfers (api)
# create  allocation
# patch -  allocate tasks to employees

