import datetime


# snifim
is_with_store = True
# transfer
is_with_transfer = False

# employees
time_to_ignore_employee = 1
employees_to_ignore= ["hasana", "rami","meirg","chaimh","gavriel"]
number_of_allocation_per_employee = 5
#host = "https://menprime.mendelson.co.il/odata/Priority/tabula.ini/a121204/"  #test
host = "https://priweb.mendelson.co.il/odata/Priority/tabula.ini/a121204/"  #main
date = str(datetime.date.today())

# prioraty
alpha = 0.9  # weight for current amount of line distributed
# create_transfer
max_transfer_tasks = 4
center_street = 35
min_number_of_lines_for_transfer = 3
percentage_of_pallet = 0.2
min_lines_for_no_pallet_constraint = 6

# create_orders
amount_of_one_line_in_street = 3
pick_employee_grade_cut_off = 0
pick_height_employee_grade_cut_off = 0
jack_employee_grade_cut_off = 0
tail_percantage_to_reallocate = 0.10
max_hour_to_ignore_noon = 13
min_amount_of_jack_tasks = 2
