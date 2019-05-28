# Based on: https://github.com/HEATlab/DREAM/blob/master/libheat/stntools/stn.py
#
# MIT License
#
# Copyright (c) 2019 HEATlab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from src.temporal_networks.distempirical import norm_sample, uniform_sample


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

    def __init__(self, i=0, j=0, wji=-1, wij=-1, distribution=None):
        # node where the constraint starts
        self.starting_node_id = i
        # node where the constraint ends
        self.ending_node_id = j
        # Minimum allocated time between i and j
        self.min_time = -wji
        # Maximum allocated time between i and j
        if wij == 'inf':
            wij = float('inf')
        self.max_time = wij
        # Probability distribution (for contingent constraints)
        self.distribution = distribution
        # Duration (for contingent constraints) sampled from the probability distribution
        self.sampled_duration = 0
        # The constraint is contingent if it has a probability distribution
        self.is_contingent = distribution is not None

    def __repr__(self):
        return "Constraint {} => {} [{}, {}]".format(self.starting_node_id, self.ending_node_id, -self.min_time, self.max_time)

    def dtype(self):
        """Returns the distribution edge type as a String. If no there is
            distribution for this edge, return None.
        """
        if self.distribution is None:
            return None
        if self.distribution[0] == "U":
            return "uniform"
        elif self.distribution[0] == "N":
            return "gaussian"
        else:
            return "unknown"

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

    def to_dict(self):
        constraint_dict = dict()
        constraint_dict['starting_node_id'] = self.starting_node_id
        constraint_dict['ending_node_id'] = self.ending_node_id
        constraint_dict['min_time'] = - self.min_time
        if self.max_time == float('inf'):
            self.max_time = 'inf'
        constraint_dict['max_time'] = self.max_time
        constraint_dict['distribution'] = self.distribution
        constraint_dict['sampled_duration'] = self.sampled_duration
        constraint_dict['is_contingent'] = self.is_contingent
        return constraint_dict

    @staticmethod
    def from_dict(constraint_dict):
        constraint = Constraint()
        constraint.starting_node_id = constraint_dict['starting_node_id']
        constraint.ending_node_id = constraint_dict['ending_node_id']
        constraint.min_time = -constraint_dict['min_time']
        if constraint_dict['max_time'] == 'inf':
            constraint_dict['max_time'] = float('inf')
        constraint.max_time = constraint_dict['max_time']
        constraint.distribution = constraint_dict['distribution']
        constraint.sampled_duration = constraint_dict['sampled_duration']
        constraint.is_contingent = constraint_dict['is_contingent']
        return constraint
