import logging
from stn.stn import STN
from stn.pstn.pstn import PSTN
from stn.stnu.stnu import STNU
from stn.methods.srea import srea
from stn.methods.fpc import get_minimal_network
from stn.methods.dsc_lp import DSC_LP

""" Solves a Simple Temporal Problem (STP) 

Computes the dispatchable graph (solution space) of a STP

The dispatchable graph is not the schedule (assigment of values to timepoints), but the space of solutions to the Simple Temporal Problem (STP).

Possible methods:
- fpc:  Full Path Consistency.
        Applies the all-pairs-shortest path algorithm Floyd Warshall to establish minimality and decomposability

- srea: Static Robust Execution Algorithm
        Approximate method for solving the Robust Execution Problem. Computes the space of solutions that maximizes the robustness (likelihood of success) along with a level of risk

- dsc-lp:   Degree of Strong Controllability Linear Program
            Approximate method for finding the DSC along with an offline solution (schedule)

- durability: Returns a durable dispatchable graph that
              withstands unexpected disturbances
"""

logging.getLogger(__name__)


class STP(object):

    def __init__(self, method):
        self.method = method

    def init_graph(self):
        """Returns an empty stn of type STN, STNU or PSTN
        """
        if self.method == 'srea':
            stn = PSTN()
        elif self.method == 'fpc':
            stn = STN()
        elif self.method == 'dsc_lp':
            stn = STNU()
        elif self.method == 'durability':
            stn = STN()

        return stn

    def load_stn(self, json_stn):
        """Converts a json file to a stn (STN, STNU or PSTN)
        """
        if self.method == 'srea':
            stn = PSTN.from_json(json_stn)
        if self.method == 'fpc':
            stn = STN.from_json(json_stn)
        elif self.method == 'dsc_lp':
            stn = STNU.from_json(json_stn)

        return stn

    def get_method(self):
        return self.method

    def get_dispatchable_graph(self, stn) -> tuple:
        if self.method == 'srea':
            result = STP.srea_algorithm(stn)
        elif self.method == 'fpc':
            result = STP.fpc_algorithm(stn)
        elif self.method == 'dsc_lp':
            result = STP.dsc_lp_algorithm(stn)

        return result

    @staticmethod
    def srea_algorithm(stn) -> tuple:
        result = srea(stn)
        if result is None:
            return
        risk_level, dispatchable_graph = result
        logging.debug("Risk level: %s", risk_level)
        logging.debug("Dispatchable graph: %s", dispatchable_graph)
        return risk_level, dispatchable_graph

    @staticmethod
    def fpc_algorithm(stn) -> tuple:
        dispatchable_graph = get_minimal_network(stn)
        if dispatchable_graph is None:
            return
        risk_level = 1
        logging.debug("Risk level %s: ", risk_level)
        return risk_level, dispatchable_graph

    @staticmethod
    def dsc_lp_algorithm(stn) -> tuple:
        dsc_lp = DSC_LP(stn)
        status, bounds, epsilons = dsc_lp.original_lp()

        if epsilons is None:
            return
        original, shrinked = dsc_lp.new_interval(epsilons)
        logging.debug("Original intervals: %s", original)
        logging.debug("Shrinked intervals: %s", shrinked)

        dsc = dsc_lp.compute_dsc(original, shrinked)
        logging.debug("DSC: %s", dsc)

        stnu = dsc_lp.get_stnu(bounds)
        logging.debug("STNU: %s", stnu)

        # Returns a schedule because it is an offline approach
        schedule = dsc_lp.get_schedule(bounds)
        logging.debug("Schedule: %s ", schedule)

        return dsc, schedule

    @staticmethod
    def get_task_navigation_start_time(dispatchable_graph, task_id):
        for i, data in dispatchable_graph.nodes.data():
            if task_id in data['data']['task_id'] and data['data']['type'] == 'navigation':
                navigation_start_time = -dispatchable_graph[i][0]['weight']

        return navigation_start_time
