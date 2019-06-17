from scheduler.temporal_networks.stn import STN
from scheduler.temporal_networks.pstn import PSTN
from scheduler.srea import srea
from scheduler.fpc import get_minimal_network

""" Computes the dispatchable graph (solution space) of an temporal network based on the scheduling method defined in the config file

The dispatch graph is not the schedule (assigment of values to timepoints) but the space of solutions to the Simple Temporal Problem (STP).

Possible scheduling methods:
- fpc:  Full Path Consistency.
        Applies the all-pairs-shortest path algorithm Floyd Warshall to establish minimality and decomposability

- srea: Static Robust Execution Algorithm
        Approximate method for solving the Robust Execution Problem. Computes the space of solutions that maximizes the robustness (likelihood of success) along with a level of risk

- dsc-lp:   Degree of Strong Controllability Linear Program
            Approximate method for finding the DSC along with a solution (schedule)

- durability: Returns a durable dispatchable graph that
              withstands unexpected disturbances
"""


class Scheduler(object):

    def __init__(self, scheduling_method, **kwargs):
        self.scheduling_method = scheduling_method

        json_temporal_network = kwargs.pop('json_temporal_network', None)

        if json_temporal_network is not None:
            self.temporal_network = self.load_temporal_network(json_temporal_network)
        else:
            self.temporal_network = self.init_temporal_network()

    def init_temporal_network(self):
        if self.scheduling_method == 'srea':
            temporal_network = PSTN()
        elif self.scheduling_method == 'fpc':
            temporal_network = STN()
        elif self.scheduling_method == 'dsc-lp':
            # temporal_network = STNU()
            pass
        elif self.scheduling_method == 'durability':
            temporal_network = STN()

        return temporal_network

    def load_temporal_network(self, json_temporal_network):
        if self.scheduling_method == 'fpc':
            temporal_network = STN.from_json(json_temporal_network)

        elif self.scheduling_method == 'srea':
            temporal_network = PSTN.from_json(json_temporal_network)

        return temporal_network

    def get_temporal_network(self):
        return self.temporal_network

    def get_scheduling_method(self):
        return self.scheduling_method

    def add_task(self, task, position):
        self.temporal_network.add_task(task, position)

    def remove_task(self, position):
        self.temporal_network.remove_task(position)

    def get_dispatch_graph(self) -> tuple:
        if self.scheduling_method == 'srea':
            result = self.srea_algorithm()
        elif self.scheduling_method == 'fpc':
            result = self.fpc_algorithm()

        return result

    def srea_algorithm(self) -> tuple:
        result = srea(self.temporal_network, debug=True)
        if result is not None:
            risk_level, dispatch_graph = result
            return risk_level, dispatch_graph
            # self.temporal_network.update_edges(dispatch_graph)
        # else:
        #     print("Result of SREA was None")

    def fpc_algorithm(self) -> tuple:
        dispatch_graph = get_minimal_network(self.temporal_network)
        risk_level = 1
        return risk_level, dispatch_graph


        # minimal_network = self.temporal_network.floyd_warshall()
        # if self.temporal_network.is_consistent(minimal_network):
        #     return minimal_network
        # else:
        #     print("Temporal network was inconsistent")
            # self.temporal_network.update_edges(minimal_network)

    # def get_graph_metrics(self):
    #     completion_time = self.temporal_network.get_completion_time()
    #     makespan = self.temporal_network.get_makespan()
