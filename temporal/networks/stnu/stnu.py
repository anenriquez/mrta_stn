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

import networkx as nx
from temporal.networks.stnu import NodeSTNU, ConstraintSTNU
from temporal.networks.stn import STN
from temporal.structs.task import Task


class STNU(STN):
    """ Represents a Simple Temporal Network (STN) as a networkx directed graph
    """
    def __init__(self):
        super().__init__()
        # List of node ids of received contingent timepoints
        self.received_timepoints = list()
        # {(starting_node, ending_node): Constraint object}
        self.contingent_constraints = dict()
        # {(starting_node, ending_node): Constraint object}
        self.requirement_constraints = dict()

    def __str__(self):
        to_print = ""
        for (i, j), constraint in sorted(self.constraints.items()):
            # if the constraint is connected to the zero_timepoint
            if i == 0:
                timepoint = self.node[j]['data']
                lower_bound = -self[j][i]['weight']
                upper_bound = self[i][j]['weight']
                to_print += "Timepoint {}: [{}, {}]".format(timepoint, lower_bound, upper_bound)

                if constraint.distribution:
                    to_print += " ({})".format(constraint.distribution)
                if timepoint.is_executed:
                    to_print += " Ex"
            else:
                if constraint.distribution:
                    to_print += "Constraint {} => {}: [{}, {}], Sampled value: [{}] ({})".format(
                        constraint.starting_node_id, constraint.ending_node_id, -self[j][i]['weight'], self[i][j]['weight'], constraint.sampled_duration, constraint.distribution)
                else:
                    to_print += "Constraint {} => {}: [{}, {}]".format(
                        constraint.starting_node_id, constraint.ending_node_id, -self[j][i]['weight'], self[i][j]['weight'])
                    # to_print += " ({})".format(constraint.distribution)
            to_print += "\n"
        return to_print

    def add_zero_timepoint(self):
        zero_timepoint = NodeSTNU(0)
        self.add_node(0, data=zero_timepoint)

    def add_constraint(self, constraint):
        """Add the edges of a constraint to the STN
        starting_node: starting node
        ending_node: ending node

        A constraint
        starting_node --- [-min_time, max_time] ---> ending_node
        Is mapped to two edges in the STN
        starting_node --- max_time ---> ending_node
        starting_node <--- -min_time --- ending_node
        """

        i = constraint.starting_node_id
        j = constraint.ending_node_id

        super().add_constraint(constraint)

        if constraint.is_contingent:
            self.contingent_constraints[(i, j)] = constraint
            self.received_timepoints += [j]
        else:
            self.requirement_constraints[(i, j)] = constraint

    def add_start_end_constraints(self, node):
        """Add the start and finish time temporal constraints of a timepoint (node) in the STNU"""
        if node.is_task_start:
            start_time = ConstraintSTNU(0, node.id, node.task.earliest_start_time, node.task.latest_start_time)
            self.add_constraint(start_time)
        elif node.is_task_end:
            finish_time = ConstraintSTNU(0, node.id, node.task.earliest_finish_time, node.task.latest_finish_time)
            self.add_constraint(finish_time)

    def build_stn(self, scheduled_tasks):
        """ Builds an STN with the tasks in the list of scheduled tasks"""
        self.clear()
        self.add_zero_timepoint()

        print("Scheduled tasks: ", [task.id for task in scheduled_tasks])

        position = 1
        for task in scheduled_tasks:
            print("Adding task {} in position{}".format(task.id, position))
            # Add two nodes per task
            node = NodeSTNU(position, task, is_start_task=True)
            self.add_node(node.id, data=node)
            self.add_start_end_constraints(node)

            node = NodeSTNU(position+1, task, is_start_task=False)
            self.add_node(node.id, data=node)
            # Adding starting and ending node temporal constraint
            self.add_start_end_constraints(node)
            position += 2

        # Add constraints between nodes
        nodes = list(self.nodes)[1:]
        i = iter(nodes)
        pairs = list(zip(i, i))
        for (i, j) in pairs:
            constraint = ConstraintSTNU(i, j, self.node[i]['data'].task.estimated_duration)
            self.add_constraint(constraint)

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
        stnu = STNU()
        zero_timepoint_exists = False

        for node_dict in stnu_dict['nodes']:
            node = NodeSTNU.from_dict(node_dict)
            stnu.add_node(node.id, data=node)
            if node.id != 0:
                # Adding starting and ending node temporal constraint
                if node.type == "start":
                    start_time = ConstraintSTNU(0, node.id, 0)
                    stnu.add_constraint(start_time)

                elif node.type == "pickup":
                    pickup_start_time = ConstraintSTNU(0, node.id, node.task.earliest_start_time, node.task.latest_start_time)
                    stnu.add_constraint(pickup_start_time)

                elif node.type == "delivery":
                    delivery_finish_time = ConstraintSTNU(0, node.id, node.task.earliest_finish_time, node.task.latest_finish_time)
                    stnu.add_constraint(delivery_finish_time)

            else:
                zero_timepoint_exists = True

        if zero_timepoint_exists is not True:
            # Adding the zero timepoint
            zero_timepoint = NodeSTNU(0)
            stnu.add_node(0, data=zero_timepoint)

        for constraint_dict in stnu_dict['constraints']:
            constraint = ConstraintSTNU.from_dict(constraint_dict)
            stnu.add_constraint(constraint)

        return stnu
