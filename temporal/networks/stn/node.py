from temporal.structs.task import Task


class Node(object):
    """Represents a timepoint in the STN """

    def __init__(self, id='', task=Task(), type=0):
        # The unique ID number of the node in the STN.
        self.id = id
        # Transportation task represented by this node
        self.task = task
        # The node can be a start, pickup or delivery node
        self.type = type

    def __repr__(self):
        """ String representation """
        return "node_{} {}".format(self.id, self.type)

    def __hash__(self):
        return hash((self.id, self.task, self.type))

    def __eq__(self, other):
        if other is None:
            return False
        return (self.id == other.id and
                self.task == other.task and
                self.type == other.type)

    def to_dict(self):
        node_dict = dict()
        node_dict['id'] = self.id
        node_dict['task'] = self.task.to_dict()
        node_dict['type'] = self.type
        return node_dict

    @staticmethod
    def from_dict(node_dict):
        node = Node()
        node.id = node_dict['id']
        node.task = Task.from_dict(node_dict['task'])
        node.type = node_dict['type']
        return node
