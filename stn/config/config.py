from stn.stn import STN
from stn.pstn.pstn import PSTN
from stn.stnu.stnu import STNU
from stn.methods.srea import srea
from stn.methods.fpc import get_minimal_network
from stn.methods.dsc_lp import DSC_LP


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
        risk_metric, dispatchable_graph = result

        dispatchable_graph.risk_metric = risk_metric

        return dispatchable_graph


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

        # The dispatchable graph is a schedule because it is an offline approach
        schedule = dsc_lp.get_schedule(bounds)

        # A strongly controllable STNU has a DSC of 1, i.e., a DSC value of 1 is better. We take
        # 1 − DC to be the risk metric, so that small values are preferable
        risk_metric = 1 - dsc

        schedule.risk_metric = risk_metric

        return schedule


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
        risk_metric = 1

        dispatchable_graph.risk_metric = risk_metric

        return dispatchable_graph


stn_factory = STNFactory()
stn_factory.register_stn('fpc', STN)
stn_factory.register_stn('srea', PSTN)
stn_factory.register_stn('dsc', STNU)

stp_solver_factory = STPSolverFactory()
stp_solver_factory.register_solver('fpc', FullPathConsistency)
stp_solver_factory.register_solver('srea', StaticRobustExecution)
stp_solver_factory.register_solver('drea', StaticRobustExecution)
stp_solver_factory.register_solver('dsc', DegreeStongControllability)