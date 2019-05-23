""" Based on: https://github.com/HEATlab/DREAM/blob/master/libheat/stntools/stn.py """

from temporal.distempirical import norm_sample, uniform_sample


class Constraint(object):
    """ Represents a temporal constraint between two nodes in the STN
        i: starting node
        j: ending node

        The constraint
        i --- [-wji, wij] ---> j
        Maps to two edges in a distance graph
        i --- wij ---> j
        i <--- -wji --- j

        -wji is the lower bound (minimum allocated time between i and j)
         wij is the upper bound (maximum allocated time between i and j)

        If there is no upper bound, its value is set to infinity and the edge from i to j does not exist
        Eg, i ---[4, inf] ---> j
        is mapped to
        i <--- -4 --- j
    """

    def __init__(self, i, j, min_time, max_time, distribution=None):
        # node where the constraint starts
        self.i = i
        # node where the constraint ends
        self.j = j
        # Minimum allocated time between i and j
        self.wji = -min_time
        # Maximum allocated time between i and j
        if max_time == 'inf':
            max_time = float('inf')
        self.wij = max_time
        # Probability distribution (for contingent constraints)
        self.distribution = distribution
        # Duration (for contingent constraints) sampled from the probability distribution
        self.sampled_duration = 0
        # The constraint is contingent if it has a probability distribution
        self.is_contingent = distribution is not None

    def __repr__(self):
        return "Constraint {} => {} [{}, {}]".format(self.i, self.j, -self.wji,
                                               self.wij)

    def resample(self, random_state):
        """ Retrieves a new sample from a contingent constraint.
        Raises an exception if this is a requirement constraint.

        Returns:
            A float selected from this constraint's contingent distribution.
        """
        sample = None
        if not self.is_contingent:
            raise TypeError("Cannot sample requirement constraint")
        if self.distribution[0] == "N":
            sample = norm_sample(self.mu, self.sigma, random_state)
        elif self.distribution[0] == "U":
            sample = uniform_sample(self.dist_lb, self.dist_ub, random_state)
        # We have to use integers because of rounding errors.
        self.sampled_duration = round(sample)
        return self.sampled_duration

    @property
    def mu(self):
        name_split = self.distribution.split("_")
        if len(name_split) != 3 or name_split[0] != "N":
            raise ValueError("No mu for non-normal dist")
        return float(name_split[1])

    @property
    def sigma(self):
        name_split = self.distribution.split("_")
        if len(name_split) != 3 or name_split[0] != "N":
            raise ValueError("No sigma for non-normal dist")
        return float(name_split[2])

    @property
    def dist_ub(self):
        name_split = self.distribution.split("_")
        if len(name_split) != 3 or name_split[0] != "U":
            raise ValueError("No upper bound for non-uniform dist")
        return float(name_split[2]) * 1000

    @property
    def dist_lb(self):
        name_split = self.distribution.split("_")
        if len(name_split) != 3 or name_split[0] != "U":
            raise ValueError("No lower bound for non-uniform dist")
        return float(name_split[1]) * 1000
