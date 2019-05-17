""" Based on: https://github.com/HEATlab/DREAM/blob/master/libheat/stntools/stn.py """

import networkx as nx
import matplotlib.pyplot as plt

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
        return "Node {} executed {}".format(self.id, self.executed)

    def __hash__(self):
        return hash((self.id, self.executed))

    def __eq__(self, other):
        if other is None:
            return False
        return (self.id == other.id and
                self.executed == other.executed)

    def copy(self):
        """ Return a copy of this node """
        new_node = Node(self.id, self.executed)
        return new_node

    def for_json(self):
        """ Returns a dictionary in json format """
        return {"node_id": self.id,
                "executed": self.executed}

    def execute(self):
        self.executed = True

    def is_executed(self):
        return self.executed


class Constraint(object):
    """ Represents a temporal constraint in the STN
    Consists of two edges:
    edge_earliest_time:  starting_node -----> ending_node,    weight = latest time
    edge_latest_time:   ending_node  <------ starting_node,  weight = -earliest time"""

    def __init__(self, stn, starting_node, ending_node, earliest_time, latest_time, distribution=None):
        # STN (networkx object) to which the constraint will be added
        self.stn = stn
        # node where the constraint starts
        self.starting_node = starting_node
        # node where the constraint ends
        self.ending_node = ending_node
        # Minimum time allotted between the starting and ending node
        self.earliest_time = -earliest_time
        # Maximum time allotted between the starting and the ending node
        self.latest_time = latest_time
        # Probability distribution (for contingent edges)
        self.distribution = distribution
        # Duration (used for conringent edges)
        # The duration is sampled from the probability distribution
        self._sampled_duration = 0

        self.add_constraint_to_stn()

    def add_constraint_to_stn(self):
        self.stn.add_weighted_edges_from([(self.starting_node, self.ending_node, self.latest_time),
                                          (self.ending_node, self.starting_node, self.earliest_time)])

    def __hash__(self):
        return hash((self.starting_node, self.ending_node, self.earliest_time, self.latest_time, self.distribution, self._sampled_duration))

    def __eq__(self, other):
        if other is None:
            return False
        return (self.starting_node == other.starting_node
        and self.ending_node == other.ending_node
        and self.earliest_time == other.earliest_time
        and self.latest_time == other.latest_time
        and self.distribution == other.distribution
        and self._sampled_duration == other._sampled_duration)

    def for_json(self):
        """ Returns a dictionary in json format """
        json = {"starting_node": self.starting_node.id,
                "ending_node": self.ending_node.id}

        if self.distribution is not None:
            json["distribution"] = {self.distribution}

        if self.earliest_time == float('inf'):
            json['earliest_time'] = '-inf'
        else:
            json['earliest_time'] = -self.earliest_time

        if self.latest_time == float('inf'):
            json['latest_time'] = 'inf'
        else:
            json["latest_time"] = self.latest_time

        return json


if __name__ == "__main__":
    node1 = Node(1)
    node2 = Node(2)

    stn = nx.DiGraph()
    stn.add_node(node1)
    stn.add_node(node2)

    constraint = Constraint(stn, node1, node2, 41, 46)

    # stn.add_edge(node1, node2, )

    # stn.add_edge(node1, node2, object=Constraint(node1, node2, 0, 0))
    # stn.edges[node1, node2]['weight'] = 7

    print("Nodes:", list(stn.nodes))
    print("Edges:", list(stn.edges))
    print(stn.edges[node1, node2]['weight'])
    print(stn.edges[node2, node1]['weight'])

    nx.draw(stn, with_labels=True, font_weight='bold')
    plt.show()
