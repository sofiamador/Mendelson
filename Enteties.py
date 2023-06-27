class Location():
    def __init__(self, loc_str, warehouse_id, quantity, pallet=0, x=35, y=0):
        self.loc_str = loc_str
        self.loc_lst = loc_str.split(".")
        self.warehouse_id = warehouse_id
        self.street = self.loc_lst[0]
        self.pallet = pallet


        if len(self.loc_lst) > 1:
            self.column = self.loc_lst[1]

        if len(self.loc_lst) > 2:
            self.row = self.loc_lst[2]

        if len(self.loc_lst) > 3:
            self.cell = self.loc_lst[3]

        if quantity is not None:
            self.quantity = float(quantity)
        try:
            x_diff = abs(x - int(self.street))
            y_diff = abs(y - int(self.column))
            self.manhattan = x_diff + y_diff
        except:
            self.manhattan = 0
        self.measure_for_group_of_items = None

    def update_measure_for_group_of_items(self, distance_max, quantity_max):
        norm_distance = self.manhattan / distance_max
        norm_quantity = int(self.quantity) / int(quantity_max)
        self.measure_for_group_of_items = norm_quantity / norm_distance

    # def update_normalized_manhattan(self,max_manhattan):
    #     self.normalized_manhattan = self.manhattan/max_manhattan
    #
    # def update_measure(self,normalized_number_of_lines):
    #     self.the_measure = normalized_number_of_lines * self.normalized_manhattan


class LineNoLocation(object):

    def __init__(self, item_id, order_id, quantity, importance=1, weight=0):
        """

        :param order_id: order_id that the line belongs to
        :param item_id:
        :param quantity:
        :param location_string: full location of the product in the warehouse
        :param importance:
        :param weight: the weight of the products in this line
        """
        self.item_id = item_id
        self.order_id = order_id
        self.quantity = quantity
        self.importance = importance
        self.weight = weight


class Line(object):

    def __init__(self, item_id, order_id, quantity, warehouse_id, location_string, line_number=1, priority=0,
                 importance=1, weight=0, ):
        """

        :param order_id: order_id that the line belongs to
        :param item_id:
        :param quantity:
        :param location_string: full location of the product in the warehouse
        :param importance:
        :param weight: the weight of the products in this line
        """
        self.location = location_string
        if location_string != "":
            self.location = Location(loc_str=location_string, warehouse_id=warehouse_id, quantity=None)
        self.item_id = item_id
        self.order_id = order_id
        self.quantity = quantity
        self.importance = importance
        self.weight = weight
        self.priority = int(priority)
        self.line_number = line_number


class StreetObj:
    def __init__(self, isle_id, lines):
        self.isle_id = isle_id
        self.lines = lines
        self.lines_breathing = lines

        self.number_of_lines = len(self.lines_breathing)

        ##---- for sorting between streets
        self.number_of_unique_items = 999999
        self.number_of_unique_orders = 0
        self.ratio_for_fav_street = 999999
        self.update_for_sorting_values()

        self.lines_for_transfer_task = []

        ##---- for within the street

    def create_item_id_and_lines(self, item_id_and_lines):
        for line in self.lines_breathing:
            item_id = line.item_id
            if item_id not in item_id_and_lines:
                item_id_and_lines[item_id] = []
            item_id_and_lines[item_id].append(line)

    def get_lines_for_transfer_task(self, amount_of_items):

        item_id_and_orders = {}
        items_sorted_by_number_orders = self.create_item_id_and_orders(item_id_and_orders)
        item_id_and_lines = {}
        self.create_item_id_and_lines(item_id_and_lines)

        ans = []
        items_to_move = []
        for i in range(amount_of_items):
            if i < len(items_sorted_by_number_orders):
                item_id = items_sorted_by_number_orders[i]
                lines_of_item = item_id_and_lines[item_id]
                ans.extend(lines_of_item)
            else:
                break

        for line in ans:
            self.lines_breathing.remove(line)

        self.update_for_sorting_values()
        self.lines_for_transfer_task.append(ans)
        return ans

    def create_item_id_and_orders(self, item_id_and_orders):
        for line in self.lines_breathing:
            item_id = line.item_id
            if item_id not in item_id_and_orders:
                item_id_and_orders[item_id] = []
            item_id_and_orders[item_id].append(line.order_id)
        return list(dict(sorted(item_id_and_orders.items(), key=lambda x: len(x[1]), reverse=True)).keys())

    def update_number_of_unique_orders(self):
        dict_ = {}
        for line in self.lines_breathing:
            order_id = line.order_id
            if order_id not in dict_:
                dict_[order_id] = []
            dict_[order_id].append(line)
        self.number_of_unique_orders = len(dict_)

    def update_number_of_unique_items(self):
        dict_ = {}
        for line in self.lines_breathing:
            item_id = line.item_id
            if item_id not in dict_:
                dict_[item_id] = []
            dict_[item_id].append(line)
        self.number_of_unique_items = len(dict_)

    def update_for_sorting_values(self):
        self.update_number_of_unique_items()
        self.update_number_of_unique_orders()
        self.ratio_for_fav_street = self.number_of_unique_items / self.number_of_unique_orders

    def __str__(self):
        return self.isle_id


class Task:
    def __init__(self, id_, importance=0):
        self.id_ = id_
        self.lines = []
        self.importance = importance
        self.amount_of_lines = 0


class TaskPick(Task):
    def __init__(self, order_id, status, employee, importance, warehouse_id="", lines_for_order=[]):
        Task.__init__(self, order_id, importance)
        self.lines = lines_for_order
        self.warehouse_id = warehouse_id
        self.amount_of_lines = len(lines_for_order)
        self.status = status
        self.employee = employee


class TaskTransfer(Task):
    def __init__(self, item_id, selected_locations,lines, counter):
        Task.__init__(self, item_id)
        self.item_id = item_id
        self.selected_locations = selected_locations
        self.quantity = 0
        self.lines = lines
        # self.grouped_items =[]
        # self.create_grouped_items()

    def __str__(self):
        return str(self.item_id, self.location)

    def create_grouped_items(self):
        lines_by_items = {}
        for line in self.lines:
            item_id = line.item_id
            if item_id not in lines_by_items:
                lines_by_items[item_id] = []
            lines_by_items[item_id].append(line)

        for item_id, lines in lines_by_items.items():
            self.grouped_items.append(GroupOfItem(item_id, lines));


class GroupOfItem():
    def __init__(self, item_id, lines, locations_lines_dict):
        self.lines = lines
        self.item_id = item_id
        self.total_quantity_required = calc_total_quantity(lines)

        self.weight_on_orders_reps = 0.5

        # self.calc_total_quantity_c1()
        # self.total_quantity_not_c1 = self.total_quantity - self.total_quantity_c1

        self.number_of_lines = len(lines)  # number of distinct orders\
        self.locations = locations_lines_dict.keys()
        self.locations_no_c1 = []
        self.is_in_c1 = False
        #counter = 0
        locations_c1 = []
        for location in self.locations:
            warehouse_id = location.warehouse_id
            if warehouse_id == "C1":
                self.is_in_c1 = True
                locations_c1.append(location)

        #        counter = counter + 1
        #    else:
        #        self.locations_no_c1.append(location)
        #if counter > 1:
        #    pass
            # raise Exception("we have something in invetory with more them 1 c1 location, what to do?")
        #total_quantity_c1 = 0
        for location_c1 in locations_c1:
            #total_quantity_c1 = total_quantity_c1 + location_c1.quantity
            self.location_c1 = min(locations_c1, key=lambda x: x.manhattan)

        #try:
        #    self.total_quantity_required_from_w = self.total_quantity_required - total_quantity_c1
        #except:
        #    self.total_quantity_required_from_w = self.total_quantity_required

        self.normalized_location_c1 = None
        self.normalized_number_of_lines = None

        self.the_measure = None

        self.location_lines_dict = locations_lines_dict

    def get_lines_per_location(self,location):
        print(self.location_lines_dict)
        return self.location_lines_dict[location]
    def update_the_measure(self):
        self.the_measure = (
                                   1 - self.weight_on_orders_reps) * self.normalized_location_c1 + self.weight_on_orders_reps * self.normalized_number_of_lines

    def update_normalized_location_c1(self, location_c1_manhattan_max):
        self.normalized_location_c1 = self.location_c1.manhattan / location_c1_manhattan_max

    def update_normalized_number_of_lines(self, number_of_lines_max):
        self.normalized_number_of_lines = self.number_of_lines / number_of_lines_max

    def __str__(self):
        return str(self.item_id) + "  " + str(self.number_of_lines)

    def __hash__(self):
        return self.item_id

    def __eq__(self, other):
        return self.item_id == other.item_id

    def is_c1_location_within_range(self, lb, ub):
        c1_location = None
        for location in self.locations:
            if location.warehouse_id == "C1":
                c1_location = location
        if c1_location is None:
            raise Exception("there is no C1 location for", self.item_id, "group of items")

        street = int(c1_location.street)
        if lb < street < ub:
            return False
        return True

    def get_location_lines_dict(self):
        for location in self.locations:
            for line in self.lines:
                break


class Order(Task):
    def __init__(self, order_id, ability, lines=[]):
        self.order_id = order_id
        self.ability = ability
        self.lines = lines
        self.priority = min(self.lines, key=lambda x: x.priority).priority
        self.amount_of_lines = len(self.lines)
        self.cumulative_value = None

    def update_cumulative_distribution(self, sum_of_lines, sum_of_all_lines):
        self.cumulative_value = sum_of_lines / sum_of_all_lines


class GroupOfOrders(Order):
    def __init__(self, street, orders):
        self.street = street
        self.orders = orders
        self.lines = []

        for order in orders:
            self.lines = order.lines + self.lines
        Order.__init__(self, order_id=orders[0].order_id, ability=orders[0].ability, lines=self.lines)
        self.amount_of_orders = len(self.orders)


# class GroupOfItem():
#     def __init__(self, item_id, lines):
#         self.lines = lines
#         self.item_id = item_id
#         self.importance = 1 # data not avaliable
#         self.total_quantity = calc_total_quantity(lines)
#         self.total_volume = calc_total_weight(lines)
#         self.number_of_lines = len(lines)  # number of distinct orders\
#         self.location = lines[0].location
#         self.street = lines[0].location.street
#
#     def __str__(self):
#         return str(self.item_id)+ "  "+ str(self.total_volume)
#
#     def __hash__(self):
#         return self.item_id
#
#     def __eq__(self, other):
#         return self.item_id == other.item_id


def calc_total_weight(lines):
    sum_weight = 0
    for line in lines:
        sum_weight = sum_weight + line.weight
    return sum_weight


def calc_total_quantity(lines):
    sum_quantity = 0
    for line in lines:
        sum_quantity = sum_quantity + line.quantity
    return sum_quantity


class Employee():

    def __init__(self, id_, role, abilities):
        self.abilities = abilities
        # self.location = location
        # self.name = name
        self.id_ = id_
        self.role = role

    def __str__(self):
        return str(self.id_) + "  " + str(self.abilities)
