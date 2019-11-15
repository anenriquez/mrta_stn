import networkx as nx

from stn.config.config import stn_factory, stp_solver_factory
from stn.exceptions.stp import NoSTPSolution

""" Solves a Simple Temporal Problem (STP)

Computes the dispatchable graph (solution space) of a STP

The dispatchable graph is not the schedule (assignment of values to timepoints),
but the space of solutions to the Simple Temporal Problem (STP).

Possible solvers:
- fpc:  Full Path Consistency.
        Applies the all-pairs-shortest path algorithm Floyd Warshall to establish
        minimality and decomposability

- srea: Static Robust Execution Algorithm
        Approximate method for solving the Robust Execution Problem.
        Computes the space of solutions that maximizes the robustness
        (likelihood of success) along with a level of risk

- dsc-lp:   Degree of Strong Controllability Linear Program
            Approximate method for finding the DSC along with an offline solution
            (schedule)

- durability: Returns a durable dispatchable graph that
              withstands unexpected disturbances
"""


class STP(object):
    def __init__(self, solver_name):
        self.solver_name = solver_name
        self.solver = stp_solver_factory.get_solver(solver_name)

    def get_stn(self, **kwargs):
        """ Returns an stn of the type used by the stp solver

        :param kwargs: stn in json format
        :return: stn (object)
        """
        stn_json = kwargs.pop('stn_json', None)
        stn = stn_factory.get_stn(self.solver_name)
        if stn_json:
            stn = stn.from_json(stn_json)

        return stn

    def solve(self, stn):
        """ Computes the dispatchable graph and risk metric of the given stn
        """
        dispatchable_graph = self.solver.compute_dispatchable_graph(stn)

        if dispatchable_graph is None:
            raise NoSTPSolution()

        return dispatchable_graph

    @staticmethod
    def is_consistent(stn):
        shortest_path_array = nx.floyd_warshall(stn)
        if stn.is_consistent(shortest_path_array):
            return True
        return False


