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

# from scheduler.temporal_networks.pstn import NodePSTN, ConstraintPSTN
from scheduler.temporal_networks.pstn import Constraint
from scheduler.temporal_networks.stn import STN
from json import JSONEncoder
from networkx.readwrite import json_graph
import json


class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class PSTN(STN):
    """ Represents a Probabilistic Simple Temporal Network (PSTN) as a networkx directed graph
    """
    def __init__(self):
        super().__init__()
        # # List of node ids of received contingent timepoints
        # self.received_timepoints = list()
        # # {(starting_node, ending_node): Constraint object}
        # self.contingent_constraints = dict()
        # # {(starting_node, ending_node): Constraint object}
        # self.requirement_constraints = dict()

    # def __str__(self):
    #     to_print = ""
    #     for (i, j), constraint in sorted(self.constraints.items()):
    #         # if the constraint is connected to the zero_timepoint
    #         if i == 0:
    #             timepoint = self.node[j]['data']
    #             lower_bound = -self[j][i]['weight']
    #             upper_bound = self[i][j]['weight']
    #             to_print += "Timepoint {}: [{}, {}]".format(timepoint, lower_bound, upper_bound)
    #
    #             if constraint.distribution:
    #                 to_print += " ({})".format(constraint.distribution)
    #             if timepoint.is_executed:
    #                 to_print += " Ex"
    #         else:
    #             if constraint.distribution:
    #                 to_print += "Constraint {} => {}: [{}, {}], Sampled value: [{}] ({})".format(
    #                     constraint.starting_node_id, constraint.ending_node_id, -self[j][i]['weight'], self[i][j]['weight'], constraint.sampled_duration, constraint.distribution)
    #             else:
    #                 to_print += "Constraint {} => {}: [{}, {}]".format(
    #                     constraint.starting_node_id, constraint.ending_node_id, -self[j][i]['weight'], self[i][j]['weight'])
    #                 # to_print += " ({})".format(constraint.distribution)
    #         to_print += "\n"
    #     return to_print

    # def add_zero_timepoint(self):
    #     zero_timepoint = NodePSTN(0)
    #     self.add_node(0, data=zero_timepoint)

    def add_constraint(self, i=0, j=0, wji=0, wij=float('inf'), distribution=""):
        """
        Adds constraint between nodes i and j
        i: starting node
        j: ending node

        The constraint
        i --- [-wji, wij] ---> j
        Maps to two edges in a distance graph
        i --- wij ---> j
        i <--- -wji --- j

        -wji is the lower bound (minimum allocated time between i and j)
         wij is the upper bound (maximum allocated time between i and j)

        If there is no upper bound, its value is set to infinity

        distribution is the probability distribution of the constraint between i and j
        """

        # i = constraint.starting_node_id
        # j = constraint.ending_node_id


        # The constraint is contingent if it has a probability distribution
        is_contingent = distribution is not ""

        super().add_constraint(i, j, wji, wij)

        self.add_edge(i, j, distribution=distribution)
        self.add_edge(i, j, is_contingent=is_contingent)

        self.add_edge(j, i, distribution=distribution)
        self.add_edge(j, i, is_contingent=is_contingent)

        # if constraint.is_contingent:
        #     self.contingent_constraints[(i, j)] = constraint
        #     self.received_timepoints += [j]
        # else:
        #     self.requirement_constraints[(i, j)] = constraint

    def get_contingent_constraints(self):
        """ Returns a dictionary with the contingent constraints in the PSTN
         {(starting_node, ending_node): Constraint (object)}
        """
        contingent_constraints = dict()

        for (i, j, data) in self.edges.data():
            if self[i][j]['is_contingent'] is True and i < j:
                contingent_constraints[(i, j)] = Constraint(i, j, self[i][j]['distribution'])

        return contingent_constraints



    # def add_timepoint_constraints(self, node_id, task, type)

    # def add_start_end_constraints(self, node):
    #     """Add the start and finish time scheduler constraints of a timepoint (node) in the STNU"""
    #     if node.type == "start":
    #         start_time = ConstraintPSTN(0, node.id, 0)
    #         self.add_constraint(start_time)
    #
    #     elif node.type == "pickup":
    #         pickup_time = ConstraintPSTN(0, node.id, node.task.earliest_pickup_time, node.task.latest_pickup_time)
    #         self.add_constraint(pickup_time)
    #
    #     elif node.type == "delivery":
    #         delivery_time = ConstraintPSTN(0, node.id, node.task.earliest_delivery_time, node.task.latest_delivery_time)
    #         self.add_constraint(delivery_time)

    # def build_temporal_network(self, scheduled_tasks):
    #     """ Builds an STN with the tasks in the list of scheduled tasks"""
    #     self.clear()
    #     self.add_zero_timepoint()
    #
    #     print("Scheduled tasks: ", [task.id for task in scheduled_tasks])
    #
    #     position = 1
    #     for task in scheduled_tasks:
    #         print("Adding task {} in position{}".format(task.id, position))
    #         # Add two nodes per task
    #         node = NodePSTN(position, task, "start")
    #         self.add_node(node.id, data=node)
    #         self.add_start_end_constraints(node)
    #
    #         node = NodePSTN(position + 1, task, "pickup")
    #         self.add_node(node.id, data=node)
    #         self.add_start_end_constraints(node)
    #
    #         node = NodePSTN(position + 2, task, "delivery")
    #         self.add_node(node.id, data=node)
    #         self.add_start_end_constraints(node)
    #         position += 3
    #
    #     # Add constraints between nodes
    #     nodes = list(self.nodes)
    #     print("Nodes: ", nodes)
    #     constraints = [((i), (i + 1)) for i in range(1, len(nodes)-1)]
    #     print("Constraints: ", constraints)
    #
    #     for (i, j) in constraints:
    #         if self.node[i]['data'].type == "start":
    #             # TODO: Get distribution from i to j
    #             distribution = "N_6_1"
    #             constraint = ConstraintPSTN(i, j, 6, distribution=distribution)
    #             self.add_constraint(constraint)
    #
    #         elif self.node[i]['data'].type == "pickup":
    #             # TODO: Get distribution of duration
    #             distribution = "N_4_1"
    #             constraint = ConstraintPSTN(i, j, self.node[i]['data'].task.estimated_duration, distribution=distribution)
    #             self.add_constraint(constraint)
    #
    #         elif self.node[i]['data'].type == "delivery":
    #             constraint = ConstraintPSTN(i, j, 0)
    #             self.add_constraint(constraint)

    def add_intertimepoints_constraints(self, constraints, task):
        """ Adds constraints between the timepoints of a task
        Constraints between:
        - navigation start and start (contingent)
        - start and finish (contingent)
        - finish and next task (if any) (requirement)
        Args:
            constraints (list) : list of tuples that defines the pair of nodes between which a new constraint should be added
            Example:
            constraints = [(1, 2), (2, 3)]
            New constraints will be added between nodes 1 and 2 and between 2 and 3

            task (Task): task represented by the constraints
        """
        for (i, j) in constraints:
            print("Adding constraint: ", (i, j))
            if self.node[i]['data']['type'] == "navigation":
                distribution = self.get_navigation_distribution(i, j)
                self.add_constraint(i, j, distribution=distribution)

            elif self.node[i]['data']['type'] == "start":
                distribution = self.get_task_distribution(task)
                self.add_constraint(i, j, distribution=distribution)

            elif self.node[i]['data']['type'] == "finish":
                # wait time between finish of one task and start of the next one. Fixed to [0, inf]
                self.add_constraint(i, j, 0)

    def get_navigation_distribution(self, source, destination):
        """ Reads from the database the probability distribution for navigating from source to destination
        """
        # TODO: Read estimated distribution from dataset
        distribution = "N_6_1"
        return distribution

    def get_task_distribution(self, task):
        """ Reads from the database the estimated distribution of the task
        In the case of transportation tasks, the estimated distribution is the navigation time from the pickup to the delivery location
        """
        distribution = "N_4_1"
        return distribution

    def to_dict(self):
        stnu_dict = dict()
        stnu_dict['nodes'] = list()
        for node in self.nodes():
            stnu_dict['nodes'].append(self.node[node]['data'].to_dict())
            print("Printing the nodes")
            print(self.node[node]['data'])
        #     stnu_dict['nodes'].append(node.to_dict())
        stnu_dict['constraints'] = list()
        for (i, j), constraint in self.constraints.items():
            stnu_dict['constraints'].append(constraint.to_dict())
        return stnu_dict

    @staticmethod
    def from_dict(stnu_dict):
        stnu = PSTN()
        zero_timepoint_exists = False

        for node_dict in stnu_dict['nodes']:
            node = NodePSTN.from_dict(node_dict)
            stnu.add_node(node.id, data=node)
            if node.id != 0:
                # Adding starting and ending node scheduler constraint
                if node.type == "start":
                    start_time = ConstraintPSTN(0, node.id, 0)
                    stnu.add_constraint(start_time)

                elif node.type == "pickup":
                    pickup_time = ConstraintPSTN(0, node.id, node.task.earliest_pickup_time, node.task.latest_pickup_time)
                    stnu.add_constraint(pickup_time)

                elif node.type == "delivery":
                    delivery_time = ConstraintPSTN(0, node.id, node.task.earliest_delivery_time, node.task.latest_delivery_time)
                    stnu.add_constraint(delivery_time)

            else:
                zero_timepoint_exists = True

        if zero_timepoint_exists is not True:
            # Adding the zero timepoint
            zero_timepoint = NodePSTN(0)
            stnu.add_node(0, data=zero_timepoint)

        for constraint_dict in stnu_dict['constraints']:
            constraint = ConstraintPSTN.from_dict(constraint_dict)
            stnu.add_constraint(constraint)

        return stnu

    @staticmethod
    def from_json(pstn_json):
        pstn = PSTN()
        dict_json = json.loads(pstn_json)
        graph = json_graph.node_link_graph(dict_json)
        pstn.add_nodes_from(graph.nodes(data=True))
        pstn.add_edges_from(graph.edges(data=True))

        return pstn

    def from_dict(pstn_json):
        pstn = PSTN()
        dict_json = json.load(pstn_json)
        print("Done with loading")
        graph = json_graph.node_link_graph(dict_json)
        pstn.add_nodes_from(graph.nodes(data=True))
        pstn.add_edges_from(graph.edges(data=True))
        return pstn
