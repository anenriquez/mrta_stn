import numpy as np
import copy
from temporal.networks.stn import STN

""" Computes a schedule based on the selected dispatch strategy """


class Scheduler(object):
    def __init__(self):
        self.stn = None

    def get_schedule(self, stn, strategy):
        """ Computes a schedule based on the execution strategy and an input stn

        Args:
        execution_strat (str): String representing the execution strategy.
        stn (STN): a simple temporal network

        Returns a tuple with format:
        | [0]: Alpha of the guide.
        | [1]: dispatch (type STN) which the simulator should follow
        """
        alpha = 1.0
        if strategy == "earliest":
            return alpha, self.earliest_schedule(stn)
        elif strategy == "latest":
            return alpha, self.latest_schedule(stn)
        else:
            raise ValueError(("Execution strategy '{}'"
                              " unknown").format(self.strategy))

    def earliest_schedule(self, stn):
        """ Computes a schedule that assigns the earliest time to each start timepoint
        """
        for (i, j), constraint in sorted(stn.constraints.items()):
            # if the constraint is connected to the zero_timepoint
            if i == 0:
                node = stn.node[j]['data']
                task = node.task
                if node.type == "start":
                    start_time_lower_bound = -stn[j][i]['weight']
                    task.start_time = start_time_lower_bound
                elif node.type == 'delivery':
                    delivery_time_lower_bound = -stn[j][i]['weight']
                    task.finish_time = delivery_time_lower_bound

                stn.node[j]['data'].task = task
        return stn

    def latest_schedule(self, stn):
        """ Computes a schedule that assigns the latest time to each start timepoint
        """
        for (i, j), constraint in sorted(stn.constraints.items()):
            # if the constraint is connected to the zero_timepoint
            if i == 0:
                node = stn.node[j]['data']
                task = node.task
                if node.type == "start":
                    start_time_upper_bound = stn[i][j]['weight']
                    task.start_time = start_time_upper_bound
                # elif node.type == 'pickup':
                #     pickup_time_upper_bound = self[i][j]['weight']
                elif node.type == 'delivery':
                    delivery_time_upper_bound = stn[i][j]['weight']
                    task.finish_time = delivery_time_upper_bound

                stn.node[j]['data'].task = task
        return stn

    def travel_time_to_pickup(self):
        """ Computes a schedule that assigns to the start timepoint the difference of the earliest_pickup_time and the travel time (TT) from the previous task (or init position) to the pickup of next task
        """
        pass

    def get_completion_time(self, stn):
        nodes = list(stn.nodes())
        node_first_task = nodes[1]
        node_last_task = nodes[-1]

        first_task_start_time = stn.node[node_first_task]['data'].task.start_time
        # print("First task start time: ", first_task_start_time)
        last_task_finish_time = stn.node[node_last_task]['data'].task.finish_time
        # print("Last task finish time: ", last_task_finish_time)

        completion_time = round(last_task_finish_time - first_task_start_time)

        return completion_time

    def get_makespan(self, stn):
        nodes = list(stn.nodes())
        node_last_task = nodes[-1]
        last_task_finish_time = stn.node[node_last_task]['data'].task.finish_time
        return last_task_finish_time
