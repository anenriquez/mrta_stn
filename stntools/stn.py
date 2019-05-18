""" Based on: https://github.com/HEATlab/DREAM/blob/master/libheat/stntools/stn.py """

import networkx as nx
import matplotlib.pyplot as plt
from stntools.distempirical import norm_sample, uniform_sample


class Node(object):
    """Represents a timepoint in the STN """

    def __init__(self, id, executed=False):
            # The unique ID number of the node in the STN.
            self.id = id
            # Flag that indicates if the timepoint has been
            # executed.
            self.executed = False

    def __repr__(self):
        """ String represenation """
        if self.executed:
            return "node_{} executed ".format(self.id)
        else:
            return "node_{} ".format(self.id)

    def __hash__(self):
        return hash((self.id, self.executed))

    def __eq__(self, other):
        if other is None:
            return False
        return (self.id == other.id and
                self.executed == other.executed)

    def execute(self):
        self.executed = True

    def is_executed(self):
        return self.executed


class Edge(object):
    """ Represents a temporal constraint in the STN """

    def __init__(self, starting_node, ending_node, weight, distribution=None):
        # node where the constraint starts
        self.starting_node = starting_node
        # node where the constraint ends
        self.ending_node = ending_node
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
        return "Edge {} => {} []".format(self.starting_node.id, self.ending_node.id, self.weight)

    def __hash__(self):
        return hash((self.starting_node, self.ending_node, self.weight, self.distribution, self.sampled_duration, self.is_contingent, self.is_requirement))

    def __eq__(self, other):
        if other is None:
            return False
        return (self.starting_node == other.starting_node
        and self.ending_node == other.ending_node
        and self.weight == other.weight
        and self.distribution == other.distribution
        and self.sampled_duration == other.sampled_duration
        and self.is_contingent == other.is_contingent
        and self.is_requirement == other.is_requirement)

    def get_attr_dict(self):
        """Returns the edge attributes as a dictionary"""
        attr_dict = {'weight': self.weight,
                    'distribution': self.distribution,
                    'sampled_duration': self.sampled_duration,
                    'is_contingent': self.is_contingent,
                    'is_requirement': self.is_requirement}
        return attr_dict

    def resample(self, random_state):
        """ Retrieves a new sample from a contingent constraint.
        Raises an exception if this is a requirement constraint.

        Returns:
            A float selected from this constraint's contingent distribution.
        """
        sample = None
        if not self.is_contingent():
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


class STN(nx.DiGraph):
    """ A Simple Temporal Network (STN) is represented using networkx """
    def __init__(self):
        nx.DiGraph.__init__(self)
        # List of node ids of received contingent timepoints
        self.received_timepoints = []
        # {(starting_node, ending_node): Constraint object}
        self.contingent_constraints = {}
        # {(starting_node, ending_node): Constraint object}
        self.requirement_constraints = {}
        # Time difference between the finish time of the last timepoint and the start time of the first timepoint in the STN
        self.completion_time = 0

    def add_constraint(self, constraint):
        """Adds a temporal constraint to the STN"""
        self.add_edge(constraint.starting_node, constraint.ending_node, attr_dict=constraint.get_attr_dict())

    def get_minimal_stn(self):
        return nx.floyd_warshall(stn)

    def is_consistent(self, minimal_stn):
        """The STN is not consistent if it has negative cycles"""
        consistent = True
        for node, nodes in minimal_stn.items():
            if nodes[node] != 0:
                consistent = False
        return consistent

    def get_completion_time(self, minimal_stn):
        pass

    def __str__(self):
        stn_str = ""
        return stn_str

if __name__ == "__main__":
    node0 = Node(0)
    node1 = Node(1)

    stn = STN()

    constraint1 = Edge(node0, node1, 46)
    constraint2 = Edge(node1, node0, -41)

    stn.add_constraint(constraint1)
    stn.add_constraint(constraint2)
    minimal_stn = stn.get_minimal_stn()

    edges = stn.edges.data()
    print("Nodes:", stn.nodes.data())
    print("Edges:", edges)

    print("Minimal STN")
    print(minimal_stn)
    print(stn.is_consistent(minimal_stn))


    nx.draw(stn, with_labels=True, font_weight='bold')
    plt.show()
