""" Based on: https://github.com/HEATlab/DREAM/blob/master/libheat/stntools/stn.py """

import networkx as nx
from src.temporal_networks.stnu import Node, Constraint


class STNU(nx.DiGraph):
    """ Represents a Simple Temporal Network (STN) as a networkx directed graph
    """
    def __init__(self):
        nx.DiGraph.__init__(self)
        # List of node ids of received contingent timepoints
        self.received_timepoints = list()
        # {node_id: Node object}
        # self.timepoints = dict()
        # {(starting_node, ending_node): Constraint object}
        self.constraints = dict()
        # {(starting_node, ending_node): Constraint object}
        self.contingent_constraints = dict()
        # {(starting_node, ending_node): Constraint object}
        self.requirement_constraints = dict()
        # Time difference between the finish time of the last timepoint and the start time of the first timepoint in the STN
        self.completion_time = 0

    def __str__(self):
        to_print = ""
        for (i, j), constraint in sorted(self.constraints.items()):
            # if the constraint is connected to the zero_timepoint
            if i == 0:
                timepoint = self.node[j]['data']
                lower_bound = -self[j][i]['weight']
                upper_bound = self[i][j]['weight']
                to_print += "Timepoint {}: [{}, {}]".format(timepoint, lower_bound, upper_bound)

                if constraint.distribution is not None:
                    to_print += " ({})".format(constraint.distribution)
                if timepoint.is_executed:
                    to_print += " Ex"
            else:
                to_print += "Constraint {} => {}: [{}, {}], Sampled value: [{}]".format(
                    constraint.starting_node_id, constraint.ending_node_id, -self[j][i]['weight'], self[i][j]['weight'], constraint.sampled_duration)
                if constraint.distribution is not None:
                    to_print += " ({})".format(constraint.distribution)
            to_print += "\n"
        return to_print

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

        self.add_edge(i, j, weight=constraint.max_time)
        self.add_edge(j, i, weight=constraint.min_time)

        self.constraints[(i, j)] = constraint

        if constraint.is_contingent:
            self.contingent_constraints[(i, j)] = constraint
            self.received_timepoints += [j]
        else:
            self.requirement_constraints[(i, j)] = constraint

    def is_consistent(self, minimal_stn):
        """The STN is not consistent if it has negative cycles"""
        consistent = True
        for node, nodes in minimal_stn.items():
            if nodes[node] != 0:
                consistent = False
        return consistent

    def update_edges(self, minimal_stn, create=False):
        """Update edges in the STN to reflect the distances in the minimal stn
        """
        for column, row in minimal_stn.items():
            nodes = dict(row)
            for n in nodes:
                self.update_edge_weight(column, n, minimal_stn[column][n])

    def update_edge_weight(self, i, j, weight, create=False):
        """ Updates the weight of the edge between node starting_node and node ending_node
        :param i: starting_node_id
        :parma ending_node: ending_node_id
        """
        if self.has_edge(i, j):
            self[i][j]['weight'] = weight

    def get_edge_weight(self, i, j):
        """ Returns the weight of the edge between node starting_node and node ending_node
        :param i: starting_node_id
        :parma ending_node: ending_node_id
        """
        if self.has_edge(i, j):
            return self[i][j]['weight']
        else:
            if i == j and self.has_node(i):
                return 0
            else:
                return float('inf')

    def update_time_schedule(self, minimal_stn):
        """Updates the start time, finish time and pickup_start_time of scheduled takes"""
        # Contains latest start and finish times
        first_row = list(minimal_stn[0].values())
        # Contains earliest start and finish times
        first_column = list()

        for node, nodes in minimal_stn.items():
            first_column.append(nodes[0])

        # Remove first element of the list
        first_column.pop(0)
        first_row.pop(0)

        e_s_times = [first_column[i] for i in range(0, len(first_column)) if int(i) % 2 == 0]
        e_f_times = [first_column[i] for i in range(0, len(first_column)) if int(i) % 2 != 0]

        l_s_times = [first_row[i] for i in range(0, len(first_row)) if int(i) % 2 == 0]
        l_f_times = [first_row[i] for i in range(0, len(first_row)) if int(i) % 2 != 0]

        # Updating start time, pickup start time and finish time of tasks in the STN
        task_idx = -1
        for i, node in enumerate(self.nodes()):
            task = self.node[node]['data'].task
            # if the node is not the zero_timepoint
            if task is not None:
                # TODO start_time = e_s_t - travel_time
                task.start_time = -e_s_times[task_idx]
                task.pickup_start_time = -e_s_times[task_idx]
                task.finish_time = -e_f_times[task_idx]
            if i % 2 == 0:
                task_idx += 1
            self.node[node]['data'].task = task

    def get_assigned_time(self, node_id):
        """ Returns to assigned time to a timepoint (node) in the STN"""
        if node_id == 0:
            # This is the zero_timepoint
            return 0.0
        if stn.get_edge_data(0, node_id)['weight'] != -stn.get_edge_data(node_id, 0)['weight']:
            return None
        return stn.get_edge_data(0, node_id)['weight']

    def get_completion_time(self):
        nodes = list(self.nodes())
        node_first_task = nodes[1]
        node_last_task = nodes[-1]

        first_task_start_time = self.node[node_first_task]['data'].task.start_time
        last_task_finish_time = self.node[node_last_task]['data'].task.finish_time

        completion_time = round(last_task_finish_time - first_task_start_time)

        return completion_time

    def get_makespan(self):
        nodes = list(self.nodes())
        node_last_task = nodes[-1]
        last_task_finish_time = self.node[node_last_task]['data'].task.finish_time
        return last_task_finish_time

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
            node = Node.from_dict(node_dict)
            stnu.add_node(node.id, data=node)
            if node.id != 0:
                # Adding starting and ending node temporal constraint
                if node.is_task_start:
                    start_time = Constraint(0, node.id, node.task.earliest_start_time, node.task.latest_start_time)
                    stnu.add_constraint(start_time)
                elif node.is_task_end:
                    finish_time = Constraint(0, node.id, node.task.earliest_finish_time, node.task.latest_finish_time)
                    stnu.add_constraint(finish_time)
            else:
                zero_timepoint_exists = True

        if zero_timepoint_exists is not True:
            # Adding the zero timepoint
            zero_timepoint = Node(0)
            stnu.add_node(0, data=zero_timepoint)

        for constraint_dict in stnu_dict['constraints']:
            constraint = Constraint.from_dict(constraint_dict)
            stnu.add_constraint(constraint)
        return stnu
