import numpy as np
import copy
from temporal.networks.srea import srea

""" Computes a robust dispatch strategy based on a STNU """


class Dispatch(object):
    def __init__(self, stnu, random_seed, strategy):
        self.stnu = stnu
        self.random_seed = random_seed
        self.strategy = strategy
        self._rand_state = np.random.RandomState(random_seed)

    def resample_stn(self):
        """ Samples the contingent edges of the stn"""
        for constraint in self.stnu.contingent_constraints.values():
            constraint.resample(self._rand_state)

    def get_guide(self):
        """ Computes a guide STN (dispatch) based on the execution strategy and an input stn

        Args:
        execution_strat (str): String representing the execution strategy.
        alpha (float): The previously used guide STN's alpha.
        stn (STNU): The previously used guide STN.

        Returns a tuple with format:
        | [0]: Alpha of the guide.
        | [1]: dispatch (type STN) which the simulator should follow
        """
        if self.strategy == "early":
            return 1.0, self.stnu
        elif self.strategy == "srea":
            return self.srea_algorithm()
        else:
            raise ValueError(("Execution strategy '{}'"
                              " unknown").format(self.strategy))

    def srea_algorithm(self):
        """ Implements the SREA algorithm.
        Returns a tuple with format:
        | [0]: Alpha of new guide
        | [1]: new guide which the simulator should follow
        """
        result = srea(self.stnu, debug=True)
        if result is not None:
            return result[0], result[1]
