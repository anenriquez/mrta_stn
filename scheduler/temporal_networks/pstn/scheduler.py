import numpy as np
import copy
from scheduler.temporal_networks.pstn import PSTN
from scheduler.temporal_networks.stn import Scheduler
from scheduler.temporal_networks.srea import srea

""" Computes a schedule based on the selected dispatch strategy """


class SchedulerPSTN(Scheduler):
    def __init__(self, random_seed):
        super().__init__()
        self.random_seed = random_seed
        self._rand_state = np.random.RandomState(random_seed)

    def resample_pstn(self, pstn):
        """ Samples the contingent edges of the pstn"""
        for constraint in pstn.contingent_constraints.values():
            constraint.resample(self._rand_state)
        return pstn

    def get_schedule(self, pstn, strategy):
        """ Computes a schedule based on the execution strategy and an input pstn

        Args:
        execution_strat (str): String representing the execution strategy.
        stn (STN): a simple scheduler network

        Returns a tuple with format:
        | [0]: Alpha of the guide.
        | [1]: dispatch (type STN) which the simulator should follow
        """
        if strategy == "early":
            return 1.0, pstn
        elif strategy == "srea":
            return self.srea_algorithm(pstn)
        else:
            raise ValueError(("Execution strategy '{}'"
                              " unknown").format(strategy))

    def srea_algorithm(self, pstn):
        """ Implements the SREA algorithm.
        Returns a tuple with format:
        | [0]: Alpha of new guide
        | [1]: new guide which the simulator should follow
        """
        result = srea(pstn, debug=True)
        if result is not None:
            alpha, guide = result
            schedule = self.earliest_schedule(guide)
            return alpha, schedule
