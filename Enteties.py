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


class Task:
    def __init__(self ):
        self.lines = []
        self.importance = 1

class TaskPick(Task):
    def __init__(self, id_, lines):
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
