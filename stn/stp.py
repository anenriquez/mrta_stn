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

Possible methods:
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
        self._methods = {}

    def register_stn(self, method_name, stn):
        """ Registers an stn type

        Saves the stn type in a dictionary of methods
        key - name of the method that uses the stn
        value - stn class

        :param method_name: method name
        :param stn: stn class
        """
        self._methods[method_name] = stn

    def get_stn(self, method_name):
        """ Returns an stn based on a method name

        :param method_name: method name
        :return: stn class
        """
        stn = self._methods.get(method_name)
        if not stn:
            raise ValueError(method_name)
        return stn()


class STPFactory(object):

    def __init__(self):
        self._methods = {}

    def register_method(self, method_name, method):
        """ Registers a method to solve an stp problem

        Saves the method in a dictionary of methods
        key - method name
        value - class that implements the method

        :param method_name: method name
        :param method: method class
        """
        self._methods[method_name] = method

    def get_method(self, method_name):
        """ Returns the class that implements the method

        :param method_name: method name
        :return: class that implements the method
        """
        method = self._methods.get(method_name)
        if not method:
            raise ValueError(method_name)

        return method()


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
    def __init__(self, method_name):
        # Receive the factories ?
        self.stn_factory = STNFactory()
        self.stn_factory.register_stn('fpc', STN)
        self.stn_factory.register_stn('srea', PSTN)
        self.stn_factory.register_stn('dsc_lp', STNU)

        self.stp_factory = STPFactory()
        self.stp_factory.register_method('fpc', FullPathConsistency)
        self.stp_factory.register_method('srea', StaticRobustExecution)
        self.stp_factory.register_method('dsc_lp', DegreeStongControllability)

        self.method_name = method_name
        self.method = self.stp_factory.get_method(method_name)

    def get_method_name(self):
        """ Returns the name of the method used to solve the
        stp problem

        :return: method name
        """
        return self.method_name

    def get_stn(self, **kwargs):
        """ Returns an stn of the type used by the stp method

        :param kwargs: stn in json format
        :return: stn (object)
        """
        stn_json = kwargs.pop('stn_json', None)
        stn = self.stn_factory.get_stn(self.method_name)
        if stn_json:
            stn = stn.from_json(stn_json)

        return stn

    def compute_dispatchable_graph(self, stn):
        """ Computes the dispatchable graph of the stn using the stp method

        :param stn: stn
        :return: (metric, dispatchable_graph)
        """
        result = self.method.compute_dispatchable_graph(stn)
        return result


