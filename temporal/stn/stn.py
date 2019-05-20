""" Based on: https://github.com/HEATlab/DREAM/blob/master/libheat/stntools/stn.py """

import networkx as nx


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
        i = constraint.starting_node_id
        j = constraint.ending_node_id
        # self.add_edge(i, j, weight=constraint.weight, data=constraint.get_attr_dict())
        self.add_edge(i, j, weight=constraint.weight, data=constraint)

        if constraint.is_contingent:
            self.contingent_constraints[(i, j)] = self[i][j]
            self.received_timepoints += [j]
        else:
            self.requirement_constraints[(i, j)] = self[i][j]

    # def get_minimal_stn(self):
    #     return nx.floyd_warshall(stn)

    def is_consistent(self, minimal_stn):
        """The STN is not consistent if it has negative cycles"""
        consistent = True
        for node, nodes in minimal_stn.items():
            if nodes[node] != 0:
                consistent = False
        return consistent

    def update_edges(self, minimal_stn):
        """Update edges in the STN to reflect the distances in the minimal stn"""
        for column, row in minimal_stn.items():
            nodes = dict(row)
            for n in nodes:
                if self.has_edge(column, n):
                    # Updating edge
                    # self[column][n]['weight'] = minimal_stn[column][n]
                    self.update_edge_weight(column, n, minimal_stn[column][n])

    def update_edge_weight(self, starting_node_id, ending_node_id, weight):
        self[starting_node_id][ending_node_id]['weight'] = weight

    def update_time_schedule(self, minimal_stn):
        """Updates the start time, finish time and pickup_start_time of scheduled takes"""
        # Contains latest start and finish times
        first_row = list(minimal_stn[0].values())
        # Contains earliest start and finish times
        first_column = list()

        for node, nodes in minimal_stn.items():
            first_column.append(nodes[0])

        print("First row: ", first_row)
        print("First column: ", first_column)

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

    def __str__(self):
        stn_str = ""
        return stn_str



    # def draw_stn(self):
    #     nx.draw(self, with_labels=True, font_weight='bold')
    #     plt.show()

# if __name__ == "__main__":
#     node0 = Node(0)
#     node1 = Node(1)
#
#     stn = STN()
#
#     constraint1 = Edge(node0, node1, 46)
#     constraint2 = Edge(node1, node0, -41)
#
#     stn.add_constraint(constraint1)
#     stn.add_constraint(constraint2)
#     minimal_stn = stn.get_minimal_stn()
#
#     edges = stn.edges.data()
#     print("Nodes:", stn.nodes.data())
#     print("Edges:", edges)
#
#     print("Minimal STN")
#     print(minimal_stn)
#     print(stn.is_consistent(minimal_stn))
#
#     stn.draw_stn()

    # nx.draw(stn, with_labels=True, font_weight='bold')
    # plt.show()
