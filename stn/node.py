from stn.utils.uuid import from_str


class Node(object):
    """Represents a timepoint in the STN """

    def __init__(self, task_id, node_type, is_executed=False):
        # id of the task represented by this node
        if isinstance(task_id, str):
            task_id = from_str(task_id)
        self.task_id = task_id
        # The node can be of node_type zero_timepoint, start, pickup or delivery
        self.node_type = node_type
        self.is_executed = is_executed

    def __str__(self):
        to_print = ""
        to_print += "{} {}".format(self.task_id, self.node_type)
        return to_print

    def __repr__(self):
        return str(self.to_dict())

    def __hash__(self):
        return hash((self.task_id, self.node_type, self.is_executed))

    def __eq__(self, other):
        if other is None:
            return False
        return (self.task_id == other.task_id and
                self.node_type == other.node_type and
                self.is_executed == other.is_executed)

    def __ne__(self, other):
        return not self.__eq__(other)

    def execute(self):
        self.is_executed = True

    def to_dict(self):
        node_dict = dict()
        node_dict['task_id'] = str(self.task_id)
        node_dict['node_type'] = self.node_type
        node_dict['is_executed'] = self.is_executed
        return node_dict

    @staticmethod
    def from_dict(node_dict):
        task_id = node_dict['task_id']
        if isinstance(task_id, str):
            task_id = from_str(task_id)
        node_type = node_dict['node_type']
        is_executed = node_dict.get('is_executed', False)
        node = Node(task_id, node_type, is_executed)
        return node
