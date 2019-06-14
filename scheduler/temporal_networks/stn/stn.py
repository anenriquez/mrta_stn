import networkx as nx
from scheduler.temporal_networks.stn import Node, Constraint


class STN(nx.DiGraph):
    """ Represents a Simple Temporal Network (STN) as a networkx directed graph
    """
    def __init__(self):
        super().__init__()
        # {(starting_node, ending_node): Constraint object}
        self.constraints = dict()
        self.add_zero_timepoint()

    def __str__(self):
        to_print = ""

        #  TODO
        for (i, j), constraint in sorted(self.constraints.items()):
            # if the constraint is connected to the zero_timepoint
            if i == 0:
                timepoint = self.node[j]['data']
                lower_bound = -self[j][i]['weight']
                upper_bound = self[i][j]['weight']
                to_print += "Timepoint {}: [{}, {}]".format(timepoint, lower_bound, upper_bound)

            else:
                to_print += "Constraint {} => {}: [{}, {}]".format(
                    constraint.starting_node_id, constraint.ending_node_id, -self[j][i]['weight'], self[i][j]['weight'])
            to_print += "\n"
        return to_print

    def add_zero_timepoint(self):
        zero_timepoint = Node(0)
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

        self.add_edge(i, j, weight=constraint.max_time)
        self.add_edge(j, i, weight=constraint.min_time)

        self.constraints[(i, j)] = constraint

    def remove_constraint(self, constraint):
        i = constraint.starting_node_id
        j = constraint.ending_node_id
        # print("Starting node: ", i)
        # print("Ending node: ", j)
        #
        # print("Edges: ", self.edges())

        # print("Edge: ", self.edges([i, j]))
        # print("Edge: ", self.edges([j, i]))


        self.remove_edge(i, j)
        self.remove_edge(j, i)

        print("Edges: ", self.edges())

        # Remove key from constraints dict
        self.constraints.pop((i, j), None)

    def add_task(self, task, position):
        """ A task is added as 3 nodes and 5 constraints in the STN"
        Nodes:
        - navigation start
        - start time
        - finish time
        Constraints:
        - earliest and latest navigation times
        - navigation duration
        - earliest and latest start times
        - task duration
        - earliest and latest finish times
        If the task is not the first in the STN, add wait time constraint
        """
        print("Adding task {} in position {}".format(task.id, position))
        # if position > 1:
        #     navigation_node_id = position + 3
        # else:
        #     navigation_node_id = position
        start_node_id = 2 * position + (position-2)
        pickup_node_id = start_node_id + 1
        delivery_node_id = pickup_node_id + 1

        print("Initial Nodes: ", self.nodes())
        print("Initial Edges: ", self.edges.data())

        # Remove constraint linking start_node_id and previous task (if any)
        if (start_node_id-1, start_node_id) in self.constraints and start_node_id-1 != 0:
            print("Deleting constraint: ", self.constraints[(start_node_id-1, start_node_id)])
            self.remove_constraint(self.constraints[(start_node_id-1, start_node_id)])

        # Displace by 3 all nodes and constraints after position
        mapping = {}
        for node_id, data in self.nodes(data=True):
            if node_id >= start_node_id:
                mapping[node_id] = node_id + 3
        print("mapping: ", mapping)
        nx.relabel_nodes(self, mapping, copy=False)

        print("Edges after remapping: ", self.edges.data())

        # Add new nodes
        node = Node(start_node_id, task, "start")
        self.add_node(node.id, data=node)
        self.add_start_end_constraints(node)

        node = Node(pickup_node_id, task, "pickup")
        self.add_node(node.id, data=node)
        self.add_start_end_constraints(node)

        node = Node(delivery_node_id, task, "delivery")
        self.add_node(node.id, data=node)
        self.add_start_end_constraints(node)


        # Add constraints between new Nodes
        new_constraints_between = [start_node_id, pickup_node_id, delivery_node_id]

        # Check if there is a node after the new delivery node
        if self.has_node(delivery_node_id+1):
            # new_constraints_between = [start_node_id, pickup_node_id, delivery_node_id, delivery_node_id+1]
            new_constraints_between.append(delivery_node_id+1)
        # else:
            # new_constraints_between =  [start_node_id, pickup_node_id, delivery_node_id]

        # Check if there is a node before the new start node
        if self.has_node(start_node_id-1):
            new_constraints_between.insert(0, start_node_id-1)
            # new_constraints_between = [start_node_id-1, start_node_id, pickup_node_id, delivery_node_id]
        # else:
        #     new_constraints_between =  [start_node_id, pickup_node_id, delivery_node_id]

        print("New constraints between nodes: ", new_constraints_between)

        constraints = [((i), (i + 1)) for i in new_constraints_between[:-1]]
        print("Constraints: ", constraints)

        for (i, j) in constraints:
            print("Adding constraint: ", (i, j))
            if self.node[i]['data'].type == "start":
                # TODO: Get travel time from i to j
                constraint = Constraint(i, j, 6)
                self.add_constraint(constraint)

            elif self.node[i]['data'].type == "pickup":
                constraint = Constraint(i, j, self.node[i]['data'].task.estimated_duration)
                self.add_constraint(constraint)

            elif self.node[i]['data'].type == "delivery":
                constraint = Constraint(i, j, 0)
                self.add_constraint(constraint)

        print("Nodes: ", self.nodes.data())
        print("Edges: ", self.edges.data())

        print("N nodes in stn: ", self.number_of_nodes())
        print("N edges in stn: ", self.number_of_edges())

    def remove_task(self, position):
        """ Removes the task from the given position"""
        print("Removing task at position: ", position)
        start_node_id = 2 * position + (position-2)
        pickup_node_id = start_node_id + 1
        delivery_node_id = pickup_node_id + 1
        new_constraints_between = list()

        if self.has_node(start_node_id-1) and self.has_node(delivery_node_id+1):
            new_constraints_between = [start_node_id-1, start_node_id]

        # Get adjacent edges
        edges_to_remove = list(self.in_edges(start_node_id)) + list(self.out_edges(start_node_id)) + list(self.in_edges(pickup_node_id)) + list(self.out_edges(pickup_node_id)) + list(self.in_edges(delivery_node_id)) + list(self.out_edges(delivery_node_id))

        print("Edges to remove: ", edges_to_remove)

        for (i, j) in edges_to_remove:
            if (i, j) in self.constraints:
                self.remove_constraint(self.constraints[(i, j)])

        print("Updated constraints: ", self.constraints)

        # print("In edges: ", self.in_edges(start_node_id))
        # print("Out edges: ", self.out_edges(start_node_id))
        # self.remove_edges_from(edges_to_remove)

        # Remove node and all adjacent edges
        self.remove_node(start_node_id)
        self.remove_node(pickup_node_id)
        self.remove_node(delivery_node_id)



        # Displace by -3 all nodes and constraints after position
        mapping = {}
        for node_id, data in self.nodes(data=True):
            if node_id >= start_node_id:
                mapping[node_id] = node_id - 3
        print("mapping: ", mapping)
        nx.relabel_nodes(self, mapping, copy=False)

        # If there is a task before the new position, add constraints
        # if self.has_node(start_node_id-1) and self.has_node(delivery_node_id+1):
        #     new_constraints_between = [start_node_id-1, start_node_id]
        if new_constraints_between:

            constraints = [((i), (i + 1)) for i in new_constraints_between[:-1]]
            print("Constraints: ", constraints)

            for (i, j) in constraints:
                print("Adding constraint: ", (i, j))
                if self.node[i]['data'].type == "delivery":
                    constraint = Constraint(i, j, 0)
                    self.add_constraint(constraint)



        print("Nodes: ", self.nodes.data())
        print("Edges: ", self.edges.data())

        print("N nodes in stn: ", self.number_of_nodes())
        print("N edges in stn: ", self.number_of_edges())


    def is_consistent(self, shortest_path_array):
        """The STN is not consistent if it has negative cycles"""
        consistent = True
        for node, nodes in shortest_path_array.items():
            if nodes[node] != 0:
                consistent = False
        return consistent

    def update_edges(self, shortest_path_array, create=False):
        """Update edges in the STN to reflect the distances in the minimal stn
        """
        print("Updating edges")
        for column, row in shortest_path_array.items():
            nodes = dict(row)
            for n in nodes:
                self.update_edge_weight(column, n, shortest_path_array[column][n])

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

    # def get_assigned_time(self, node_id):
    #     """ Returns to assigned time to a timepoint (node) in the STN"""
    #     if node_id == 0:
    #         # This is the zero_timepoint
    #         return 0.0
    #     if self.get_edge_data(0, node_id)['weight'] != -self.get_edge_data(node_id, 0)['weight']:
    #         return None
    #     return self.get_edge_data(0, node_id)['weight']

    # def floyd_warshall(self):
    #     minimal_stn = nx.floyd_warshall(self)
    #     return minimal_stn

    def get_completion_time(self):
        nodes = list(self.nodes())
        node_first_task = nodes[1]
        node_last_task = nodes[-1]

        start_time_lower_bound = -self[node_first_task][0]['weight']

        finish_time_upper_bound = self[0][node_last_task]['weight']

        completion_time = round(finish_time_upper_bound - start_time_lower_bound)

        return completion_time

    def get_makespan(self):
        nodes = list(self.nodes())
        node_last_task = nodes[-1]
        last_task_finish_time = self[0][node_last_task]['weight']

        return last_task_finish_time

    # def add_task(self, task, position):
    #     """ A transportation task consists of two nodes:
    #         start_node: is_task_start
    #         finish_node: is task_end
    #     """
    #     print("Adding task: ", task.id)

    def add_start_end_constraints(self, node):
        """Add the start and finish time scheduler constraints of a timepoint (node) in the STN
        EStn = EPtn - TTt(n-1)tn
        LStn = LPtn - TTt(n-1)tn
        """
        if node.type == "start":
            # TODO: Get travel time (TT) from previous task (or init position) to the pickup of next task
            earliest_start_time = 0
            # latest_start_time = 100
            start_time = Constraint(0, node.id, earliest_start_time)
            self.add_constraint(start_time)

        if node.type == "pickup":
            pickup_time = Constraint(0, node.id, node.task.earliest_pickup_time, node.task.latest_pickup_time)
            self.add_constraint(pickup_time)

        elif node.type == "delivery":
            delivery_time = Constraint(0, node.id, node.task.earliest_delivery_time, node.task.latest_delivery_time)
            self.add_constraint(delivery_time)

    def build_temporal_network(self, scheduled_tasks):
        """ Builds an STN with the tasks in the list of scheduled tasks"""
        self.clear()
        self.add_zero_timepoint()

        print("Tasks: ", [task.id for task in scheduled_tasks])

        position = 1
        for task in scheduled_tasks:
            print("Adding task {} in position {}".format(task.id, position))
            # Add three nodes per task
            node = Node(position, task, "start")
            self.add_node(node.id, data=node)
            self.add_start_end_constraints(node)

            node = Node(position+1, task, "pickup")
            self.add_node(node.id, data=node)
            self.add_start_end_constraints(node)

            node = Node(position+2, task, "delivery")
            self.add_node(node.id, data=node)
            self.add_start_end_constraints(node)
            position += 3

        # Add constraints between nodes
        nodes = list(self.nodes) #[1:]
        print("Nodes: ", nodes)
        constraints = [((i), (i + 1)) for i in range(1, len(nodes)-1)]
        print("Constraints: ", constraints)

        # Task constraints
        # constraints_tasks = [item for index, item in enumerate(constraints) if (index + 1) % 3 != 0]

        # Constraints between tasks
        # constraints_bw_tasks = set(constraints) - set(constraints_tasks)

        # Add tasks constraints
        for (i, j) in constraints:
            if self.node[i]['data'].type == "start":
                # TODO: Get travel time from i to j
                constraint = Constraint(i, j, 6)
                self.add_constraint(constraint)

            elif self.node[i]['data'].type == "pickup":
                constraint = Constraint(i, j, self.node[i]['data'].task.estimated_duration)
                self.add_constraint(constraint)

            elif self.node[i]['data'].type == "delivery":
                constraint = Constraint(i, j, 0)
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
    def from_dict(stn_dict):
        stn = STN()
        zero_timepoint_exists = False

        for node_dict in stn_dict['nodes']:
            node = Node.from_dict(node_dict)
            stn.add_node(node.id, data=node)
            if node.id != 0:
                # Adding starting and ending node scheduler constraint
                if node.type == "start":
                    # TODO: Get travel time (TT) from previous task (or init position) to the pickup of next task
                    earliest_start_time = 0
                    # latest_start_time = 100
                    start_time = Constraint(0, node.id, earliest_start_time)
                    stn.add_constraint(start_time)

                elif node.type == "pickup":
                    pickup_time = Constraint(0, node.id, node.task.earliest_pickup_time, node.task.latest_pickup_time)
                    stn.add_constraint(pickup_time)

                elif node.type == "delivery":
                    delivery_time = Constraint(0, node.id, node.task.earliest_delivery_time, node.task.latest_delivery_time)
                    stn.add_constraint(delivery_time)

            else:
                zero_timepoint_exists = True

        if zero_timepoint_exists is not True:
            # Adding the zero timepoint
            zero_timepoint = Node(0)
            stn.add_node(0, data=zero_timepoint)

        for constraint_dict in stn_dict['constraints']:
            constraint = Constraint.from_dict(constraint_dict)
            stn.add_constraint(constraint)

        return stn
