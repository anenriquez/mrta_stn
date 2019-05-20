""" Based on: https://github.com/HEATlab/DREAM/blob/master/libheat/stntools/stn.py """

from temporal.distempirical import norm_sample, uniform_sample


class Edge(object):
    """ Represents a temporal constraint in the STN """

    def __init__(self, starting_node, ending_node, weight, distribution=None):
        # node where the constraint starts
        self.starting_node_id = starting_node
        # node where the constraint ends
        self.ending_node_id = ending_node
        # Time allotted between the starting and ending node
        self.weight = weight
        # Probability distribution (for contingent edges)
        self.distribution = distribution
        # Duration (for contingent edges)
        # The duration is sampled from the probability distribution
        self.sampled_duration = 0
        # The edge is a contingent edge if it has a probability distribution
        self.is_contingent = distribution is not None
        # The edge is a requirement edge if it does not have a probability distribution
        self.is_requirement = distribution is None

    def __repr__(self):
        return "Edge {} => {} [{}]".format(self.starting_node_id, self.ending_node_id, str(self.weight))

    def __hash__(self):
        return hash((self.starting_node_id, self.ending_node_id, self.weight, self.distribution, self.sampled_duration, self.is_contingent, self.is_requirement))

    def __eq__(self, other):
        if other is None:
            return False
        return (self.starting_node_id == other.starting_node_id
        and self.ending_node_id == other.ending_node_id
        and self.weight == other.weight
        and self.distribution == other.distribution
        and self.sampled_duration == other.sampled_duration
        and self.is_contingent == other.is_contingent
        and self.is_requirement == other.is_requirement)

    def get_attr_dict(self):
        """Returns the edge attributes as a dictionary"""
        attr_dict = {'distribution': self.distribution,
                    'sampled_duration': self.sampled_duration,
                    'is_contingent': self.is_contingent,
                    'is_requirement': self.is_requirement}
        return attr_dict

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
