""" Based on: https://github.com/HEATlab/DREAM/blob/master/libheat/stntools/stn.py """

from structs.task import Task


class Node(object):
    """Represents a timepoint in the STN """

    def __init__(self, id, task=None, executed=False, transportation_task=True, **kwargs):
        # The unique ID number of the node in the STN.
        self.id = id
        # Flag that indicates if the timepoint has been
        # executed.
        self.executed = False
        # Task represented by this node
        self.task = task

        if transportation_task:
            # The node represents the start of the transportation task
            self.is_task_start = kwargs.pop('start_task', None)
            # The node represents the end of the transportation task
            self.is_task_end = kwargs.pop('end_task', None)

    def __repr__(self):
        """ String representation """
        if self.executed:
            return "node_{} executed ".format(self.id)
        else:
            return "node_{} ".format(self.id)

    def __hash__(self):
        return hash((self.id, self.executed))

    def __eq__(self, other):
        if other is None:
            return False
        return (self.id == other.id and
                self.executed == other.executed)

    def execute(self):
        self.executed = True

    def is_executed(self):
        return self.executed
