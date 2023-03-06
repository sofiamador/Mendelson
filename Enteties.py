class Location():
    def __init__(self, loc_str,warehouse_id):
        self.loc_str =loc_str
        self.loc_lst = loc_str.split(".")
        self.warehouse_id = warehouse_id
        self.street = self.loc_lst[0]
        if len(self.loc_lst) > 1:
            self.column = self.loc_lst[1]
        if len(self.loc_lst) > 2:
            self.row = self.loc_lst[2]
        if len(self.loc_lst) > 3:
            self.cell = self.loc_lst[3]

class Line(object):

    def __init__(self, item_id, order_id , quantity, warehouse_id, location_string, importance=1, weight=0):
        """

        :param order_id: order_id that the line belongs to
        :param item_id:
        :param quantity:
        :param location_string: full location of the product in the warehouse
        :param importance:
        :param weight: the weight of the products in this line
        """
        self.location = Location(loc_str=location_string,warehouse_id=warehouse_id)
        self.item_id = item_id
        self.order_id = order_id
        self.quantity = quantity
        self.importance = importance
        self.weight = weight


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
        self.update_for_sorting_values ()


        self.lines_for_transfer_task = []

        ##---- for within the street





    def create_item_id_and_lines(self,item_id_and_lines):
        for line in self.lines_breathing :
            item_id = line.item_id
            if item_id not in item_id_and_lines:
                item_id_and_lines[item_id] = []
            item_id_and_lines[item_id].append(line)


    def get_lines_for_transfer_task (self, amount_of_items):

        item_id_and_orders = {}
        items_sorted_by_number_orders = self.create_item_id_and_orders(item_id_and_orders)
        item_id_and_lines = {}
        self.create_item_id_and_lines(item_id_and_lines)


        ans = []
        items_to_move = []
        for i in range(amount_of_items):
            if i<len(items_sorted_by_number_orders):
                item_id = items_sorted_by_number_orders[i]
                lines_of_item = item_id_and_lines[item_id]
                ans.extend(lines_of_item)
            else:
                break


        for line in ans:
            self.lines_breathing.remove(line)

        self.update_for_sorting_values ()
        self.lines_for_transfer_task.append(ans)
        return ans



    def create_item_id_and_orders(self,item_id_and_orders):
        for line in self.lines_breathing :
            item_id = line.item_id
            if item_id not in item_id_and_orders:
                item_id_and_orders[item_id] = []
            item_id_and_orders[item_id].append(line.order_id)
        return list(dict(sorted(item_id_and_orders.items(), key=lambda x: len(x[1]), reverse=True)).keys())

    def update_number_of_unique_orders(self):
        dict_ ={}
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
    def __init__(self ):
        self.lines = []
        self.importance = 1

class TaskPick(Task):
    def __init__(self,  id_,lines):
        Task.__init__(self)
        self.lines = lines
        self.id_ = id_
        self.importance = lines[0].importance
        self.total_weight = calc_total_weight(lines)
        self.number_of_lines = len(lines)
        self.is_in_transfer= False
        self.numberOfIds = self.getNumberOfIds();

    def getNumberOfIds(self):
        ids_ = []
        for line in self.lines:
            if line.item_id not in ids_:
                ids_.append(line.item_id)
        return len(ids_)



class TaskTransfer(Task):
    def __init__(self,  street,lines):
        Task.__init__(self)
        self.street = street
        self.lines = lines

    def __str__(self):
        return str(self.street)+ ", "+ str(self.total_volume)




class GroupOfItem():
    def __init__(self, item_id, lines):
        self.lines = lines
        self.item_id = item_id
        self.importance = 1 # data not avaliable
        self.total_quantity = calc_total_quantity(lines)
        self.total_volume = calc_total_weight(lines)
        self.number_of_lines = len(lines)  # number of distinct orders\
        self.location = lines[0].location
        self.street = lines[0].location.street

    def __str__(self):
        return str(self.item_id)+ "  "+ str(self.total_volume)

    def __hash__(self):
        return self.item_id

    def __eq__(self, other):
        return self.item_id == other.item_id


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

