from temporal.structs.task import Task
from temporal.networks.stn import Node


class NodeSTNU(Node):
    """Represents a timepoint in the STN """

    def __init__(self, id='', task=Task(), type=0, is_executed=False):

        super().__init__(id, task, type)

        # Flag that indicates if the timepoint has been
        # executed.
        self.is_executed = is_executed

    def __repr__(self):
        """ String representation """
        if self.is_executed:
            return "node_{} executed ".format(self.id)
        else:
            return super().__repr__()

    def execute(self):
        self.is_executed = True

    def to_dict(self):
        node_dict = super().to_dict()
        # node_dict = dict()
        # node_dict['id'] = self.id
        # node_dict['task'] = self.task.to_dict()
        # node_dict['is_task_start'] = self.is_task_start
        # node_dict['is_task_end'] = self.is_task_end
        node_dict['is_executed'] = self.is_executed
        return node_dict

    @staticmethod
    def from_dict(node_dict):
        node = Node.from_dict(node_dict)
        id = node.id
        task = node.task
        type = node.type
        # node = Node()
        # node.id = node_dict['id']
        # node.task = Task.from_dict(node_dict['task'])
        # node.is_task_start = node_dict['is_task_start']
        # node.is_task_end = node_dict['is_task_end']
        is_executed = node_dict['is_executed']
        node_stnu = NodeSTNU(id, task, type, is_executed)
        return node_stnu
