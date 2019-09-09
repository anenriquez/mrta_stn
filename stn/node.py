from stn.utils.uuid import generate_uuid


class Node(object):
    """Represents a timepoint in the STN """

    def __init__(self, task_id, pose, node_type):
        # id of the task represented by this node
        self.task_id = task_id
        # Pose in the map where the node has to be executed
        self.pose = pose
        # The node can be of node_type zero_timepoint, navigation, start or finish
        self.node_type = node_type

    def __str__(self):
        to_print = ""
        to_print += "node {} {}".format(self.task_id, self.node_type)
        return to_print

    def __repr__(self):
        return str(self.to_dict())

    def __hash__(self):
        return hash((self.task_id, self.pose, self.node_type))

    def __eq__(self, other):
        if other is None:
            return False
        return (self.task_id == other.task_id and
                self.pose == other.pose and
                self.node_type == other.node_type)

    def to_dict(self):
        node_dict = dict()
        node_dict['task_id'] = self.task_id
        node_dict['pose'] = self.pose
        node_dict['node_type'] = self.node_type
        return node_dict

    @staticmethod
    def from_dict(node_dict):
        task_id = node_dict['task_id']
        pose = node_dict['pose']
        node_type = node_dict['node_type']
        node = Node(task_id, pose, node_type)
        return node
