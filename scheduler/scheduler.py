import logging
import logging.config
import yaml
from scheduler.temporal_networks.stn import STN
from scheduler.temporal_networks.pstn import PSTN
from scheduler.temporal_networks.stnu import STNU
from scheduler.srea import srea
from scheduler.fpc import get_minimal_network
from scheduler.dsc_lp import DSC_LP
from scheduler.utils.config_logger import config_logger

""" Computes the dispatchable graph (solution space) of a temporal network

The dispatch graph is not the schedule (assigment of values to timepoints), but the space of solutions to the Simple Temporal Problem (STP).

Possible scheduling methods:
- fpc:  Full Path Consistency.
        Applies the all-pairs-shortest path algorithm Floyd Warshall to establish minimality and decomposability

- srea: Static Robust Execution Algorithm
        Approximate method for solving the Robust Execution Problem. Computes the space of solutions that maximizes the robustness (likelihood of success) along with a level of risk

- dsc-lp:   Degree of Strong Controllability Linear Program
            Approximate method for finding the DSC along with an offline solution (schedule)

- durability: Returns a durable dispatchable graph that
              withstands unexpected disturbances
"""


class Scheduler(object):

    def __init__(self, scheduling_method, **kwargs):
        self.scheduling_method = scheduling_method
        config_logger('../config/logging.yaml')
        self.logger = logging.getLogger('scheduler')

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
        elif self.scheduling_method == 'dsc_lp':
            temporal_network = STNU()
        elif self.scheduling_method == 'durability':
            temporal_network = STN()

        return temporal_network

    def load_temporal_network(self, json_temporal_network):
        if self.scheduling_method == 'srea':
            temporal_network = PSTN.from_json(json_temporal_network)
        if self.scheduling_method == 'fpc':
            temporal_network = STN.from_json(json_temporal_network)
        elif self.scheduling_method == 'dsc_lp':
            temporal_network = STNU.from_json(json_temporal_network)

        return temporal_network

    def get_temporal_network(self):
        return self.temporal_network

    def get_scheduling_method(self):
        return self.scheduling_method

    def get_scheduled_tasks(self):
        return self.temporal_network.get_scheduled_tasks()

    def add_task(self, task, position):
        self.temporal_network.add_task(task, position)

    def remove_task(self, position):
        self.temporal_network.remove_task(position)

    def get_dispatch_graph(self) -> tuple:
        if self.scheduling_method == 'srea':
            result = self.srea_algorithm()
        elif self.scheduling_method == 'fpc':
            result = self.fpc_algorithm()
        elif self.scheduling_method == 'dsc_lp':
            result = self.dsc_lp_algorithm()

        return result

    def srea_algorithm(self) -> tuple:
        result = srea(self.temporal_network)
        if result is None:
            return
        risk_level, dispatch_graph = result
        self.logger.debug("Risk level: %s", risk_level)
        self.logger.debug("Dispatch graph: %s", dispatch_graph)
        return risk_level, dispatch_graph

    def fpc_algorithm(self) -> tuple:
        dispatch_graph = get_minimal_network(self.temporal_network)
        if dispatch_graph is None:
            return
        risk_level = 1
        self.logger.debug("Risk level %s: ", risk_level)
        return risk_level, dispatch_graph

    def dsc_lp_algorithm(self) -> tuple:
        dsc_lp = DSC_LP(self.temporal_network)
        status, bounds, epsilons = dsc_lp.original_lp()

        if epsilons is None:
            return
        original, shrinked = dsc_lp.new_interval(epsilons)
        self.logger.debug("Original intervals: %s", original)
        self.logger.debug("Shrinked intervals: %s", shrinked)

        dsc = dsc_lp.compute_dsc(original, shrinked)
        self.logger.debug("DSC: %s", dsc)

        stnu = dsc_lp.get_stnu(bounds)
        self.logger.debug("STNU: %s", stnu)

        dispatch_graph = dsc_lp.get_schedule(bounds)

        # Returns a schedule because it is an offline approach
        schedule = dsc_lp.get_schedule(bounds)
        self.logger.debug("Schedule: %s ", schedule)

        return dsc, schedule
