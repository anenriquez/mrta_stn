""" Based on: https://github.com/HEATlab/DREAM/blob/master/libheat/stntools/stn.py """

import networkx as nx


class STNU(nx.DiGraph):
    """ Represents a Simple Temporal Network (STN) as a networkx directed graph
    """
    def __init__(self):
        nx.DiGraph.__init__(self)
        # List of node ids of received contingent timepoints
        self.received_timepoints = []
        # {(starting_node, ending_node): Constraint object}
        self.constraints = {}
        # {(starting_node, ending_node): Constraint object}
        self.contingent_constraints = {}
        # {(starting_node, ending_node): Constraint object}
        self.requirement_constraints = {}
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
                if timepoint.is_executed():
                    to_print += " Ex"
            else:
                to_print += "Constraint {} => {}: [{}, {}], Sampled value: [{}]".format(
                    constraint.i, constraint.j, -self[j][i]['weight'], self[i][j]['weight'], constraint.sampled_duration)
                if constraint.distribution is not None:
                    to_print += " ({})".format(constraint.distribution)
            to_print += "\n"
        return to_print

    def add_constraint(self, constraint):
        """Add the edges of a constraint to the STN
        i: starting node
        j: ending node

        A constraint
        i --- [-wji, wij] ---> j
        Is mapped to two edges in the STN
        i --- wij ---> j
        i <--- -wji --- j
        """

        i = constraint.i  # starting node
        j = constraint.j  # ending_node

        self.add_edge(i, j, weight=constraint.wij)
        self.add_edge(j, i, weight=constraint.wji)

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
        print("Minimal stn: ", minimal_stn)
        for column, row in minimal_stn.items():
            nodes = dict(row)
            for n in nodes:
                self.update_edge_weight(column, n, minimal_stn[column][n])

    def update_edge_weight(self, i, j, weight, create=False):
        """ Updates the weight of the edge between node i and node j
        :param i: starting_node_id
        :parma j: ending_node_id
        """
        if self.has_edge(i, j):
            self[i][j]['weight'] = weight

    def get_edge_weight(self, i, j):
        """ Returns the weight of the edge between node i and node j
        :param i: starting_node_id
        :parma j: ending_node_id
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
