from temporal.structs.task import Task


class Node(object):
    """Represents a timepoint in the STN """

    def __init__(self, id='', task=Task(), is_start_task=True, is_task_end=False):
        # The unique ID number of the node in the STN.
        self.id = id
        # Transportation task represented by this node
        self.task = task
        # The node represents the start of the transportation task
        self.is_task_start = is_start_task
        # The node represents the end of the transportation task
        self.is_task_end = not(is_start_task)

    def __repr__(self):
        """ String representation """
        return "node_{} ".format(self.id)

    def __hash__(self):
        return hash((self.id, self.task, self.is_task_start, self.is_task_end))

    def __eq__(self, other):
        if other is None:
            return False
        return (self.id == other.id and
                self.task == other.task and
                self.is_task_start == other.is_task_start and
                self.is_task_end == other.is_task_end)

    def to_dict(self):
        node_dict = dict()
        node_dict['id'] = self.id
        node_dict['task'] = self.task.to_dict()
        node_dict['is_task_start'] = self.is_task_start
        node_dict['is_task_end'] = self.is_task_end
        return node_dict

    @staticmethod
    def from_dict(node_dict):
        node = Node()
        node.id = node_dict['id']
        node.task = Task.from_dict(node_dict['task'])
        node.is_task_start = node_dict['is_task_start']
        node.is_task_end = node_dict['is_task_end']
        return node
