from stn.stn import STN
from stn.pstn.pstn import PSTN
from stn.stnu.stnu import STNU
from stn.methods.srea import srea
from stn.methods.fpc import get_minimal_network
from stn.methods.dsc_lp import DSC_LP


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


class STNFactory(object):

    def __init__(self):
        self._stns = {}

    def register_stn(self, solver_name, stn):
        """ Registers an stn type based and the solver that uses it

        Saves the stn in a dictionary of stns
        key - name of the solver that uses the stn
        value - stn class

        :param solver_name: solver name
        :param stn: stn class
        """
        self._stns[solver_name] = stn

    def get_stn(self, solver_name):
        """ Returns an stn based on a solver name

        :param solver_name: solver name
        :return: stn class
        """
        stn = self._stns.get(solver_name)
        if not stn:
            raise ValueError(solver_name)
        return stn()


class STPSolverFactory(object):

    def __init__(self):
        self._solvers = {}

    def register_solver(self, solver_name, solver):
        """ Registers stp problem solvers

        Saves the solver in a dictionary of solvers
        key - solver name
        value - class that implements the solver

        :param solver_name: solver name
        :param solver: solver class
        """
        self._solvers[solver_name] = solver

    def get_solver(self, solver_name):
        """ Returns the class that implements the solver

        :param solver_name: solver name
        :return: class that implements the solver
        """
        solver = self._solvers.get(solver_name)
        if not solver:
            raise ValueError(solver_name)

        return solver()


class StaticRobustExecution(object):

    def __init__(self):
        self.compute_dispatchable_graph = self.srea_algorithm

    @staticmethod
    def srea_algorithm(stn):
        """ Computes the dispatchable graph of an stn using the
        srea algorithm

        :param stn: stn (object)
        """
        result = srea(stn, debug=True)
        if result is None:
            return
        risk_level, dispatchable_graph = result
        return risk_level, dispatchable_graph


class DegreeStongControllability(object):

    def __init__(self):
        self.compute_dispatchable_graph = self.dsc_lp_algorithm

    @staticmethod
    def dsc_lp_algorithm(stn):
        """ Computes the dispatchable graph of an stn using the
        degree of strong controllability lp solver

        :param stn: stn (object)
        """
        dsc_lp = DSC_LP(stn)
        status, bounds, epsilons = dsc_lp.original_lp()

        if epsilons is None:
            return
        original_intervals, shrinked_intervals = dsc_lp.new_interval(epsilons)

        dsc = dsc_lp.compute_dsc(original_intervals, shrinked_intervals)

        stnu = dsc_lp.get_stnu(bounds)

        # Returns a schedule because it is an offline approach
        schedule = dsc_lp.get_schedule(bounds)

        return dsc, schedule


class FullPathConsistency(object):

    def __init__(self):
        self.compute_dispatchable_graph = self.fpc_algorithm

    @staticmethod
    def fpc_algorithm(stn):
        """ Computes the dispatchable graph of an stn using
        full path consistency

        :param stn: stn (object)
        """
        dispatchable_graph = get_minimal_network(stn)
        if dispatchable_graph is None:
            return
        risk_level = 1
        return risk_level, dispatchable_graph


class STP(object):
    def __init__(self, solver_name):
        # Receive the factories ?
        self.stn_factory = STNFactory()
        self.stn_factory.register_stn('fpc', STN)
        self.stn_factory.register_stn('srea', PSTN)
        self.stn_factory.register_stn('dsc_lp', STNU)

        self.stp_solver_factory = STPSolverFactory()
        self.stp_solver_factory.register_solver('fpc', FullPathConsistency)
        self.stp_solver_factory.register_solver('srea', StaticRobustExecution)
        self.stp_solver_factory.register_solver('dsc_lp', DegreeStongControllability)

        self.solver_name = solver_name
        self.solver = self.stp_solver_factory.get_solver(solver_name)

    def get_solver_name(self):
        """ Returns the name of the solver used to solve the
        stp problem

        :return: solver name
        """
        return self.solver_name

    def get_stn(self, **kwargs):
        """ Returns an stn of the type used by the stp solver

        :param kwargs: stn in json format
        :return: stn (object)
        """
        stn_json = kwargs.pop('stn_json', None)
        stn = self.stn_factory.get_stn(self.solver_name)
        if stn_json:
            stn = stn.from_json(stn_json)

        return stn

    def compute_dispatchable_graph(self, stn):
        """ Computes the dispatchable graph of the stn using the stp method

        :param stn: stn
        :return: (metric, dispatchable_graph)
        """
        result = self.solver.compute_dispatchable_graph(stn)
        return result


