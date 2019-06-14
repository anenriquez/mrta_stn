from scheduler.structs.task import Task


class Node(object):
    """Represents a timepoint in the STN """

    def __init__(self, task_id='', pose='', type='zero_timepoint'):
        # id of the task represented by this node
        self.task_id = task_id
        # Pose in the map where the node has to be executed
        self.pose = pose
        # The node can be of type zero_timepoint, navigation, start or finish
        self.type = type

    def __str__(self):
        to_print = ""
        to_print += "node {} {}".format(self.task_id, self.type)
        return to_print

    def __repr__(self):
        # return "node {} {}".format(self.task_id, self.type)
        return str(self.to_dict())

    def __hash__(self):
        return hash((self.task_id, self.pose, self.type))

    def __eq__(self, other):
        if other is None:
            return False
        return (self.task_id == other.task_id and
                self.pose == other.pose and
                self.type == other.type)

    def to_dict(self):
        node_dict = dict()
        node_dict['task_id'] = self.task_id
        node_dict['pose'] = self.pose
        node_dict['type'] = self.type
        return node_dict

    @staticmethod
    def from_dict(node_dict):
        node = Node()
        node.task_id = node_dict['task_id']
        node.pose = node_dict['pose']
        node.type = node_dict['type']
        return node
