import networkx as nx
from stp.temporal_networks.stn import Node
from json import JSONEncoder
from networkx.readwrite import json_graph
import json
import logging.config


class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class STN(nx.DiGraph):
    """ Represents a Simple Temporal Network (STN) as a networkx directed graph
    """

    logger = logging.getLogger('stn')

    def __init__(self):
        super().__init__()
        self.add_zero_timepoint()
        self.max_makespan = 150

    def __str__(self):
        to_print = ""
        for (i, j, data) in self.edges.data():
            if self.has_edge(j, i) and i < j:
                # Constraints with the zero timepoint
                if i == 0:
                    timepoint = Node.from_dict(self.node[j]['data'])
                    lower_bound = -self[j][i]['weight']
                    upper_bound = self[i][j]['weight']
                    to_print += "Timepoint {}: [{}, {}]".format(timepoint, lower_bound, upper_bound)
                # Constraints between the other timepoints
                else:
                    to_print += "Constraint {} => {}: [{}, {}]".format(i, j, -self[j][i]['weight'], self[i][j]['weight'])

                to_print += "\n"

        return to_print

    def add_zero_timepoint(self):
        node = Node()
        self.add_node(0, data=node.to_dict())

    def add_constraint(self, i, j, wji=0.0, wij=float('inf')):
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

        The default upper and lower bounds are 0 and infinity
        """
        # Minimum allocated time between i and j
        min_time = -wji
        # Maximum allocated time between i and j
        max_time = wij

        self.add_edge(j, i, weight=min_time)
        self.add_edge(i, j, weight=max_time)

    def remove_constraint(self, i, j):
        """ i : starting node id
            j : ending node id
        """
        self.remove_edge(i, j)
        self.remove_edge(j, i)

    def get_constraints(self):
        """
        Two edges correspond to a constraint.
        returns     dict with constraints
                    {(starting_node, ending_node): self[i][j] }
        """
        constraints = dict()

        for (i, j) in self.edges():
            if i < j:
                constraints[(i, j)] = self[i][j]

        return constraints

    def get_node_pose(self, task, type):
        """ Returns the pose in the map where the task has to be executed
        """
        if type == 'navigation':
            # TODO: initialize the pose with the robot current position (read it from mongo)
            # this value will be overwritten once the task is allocated
            pose = ''
        elif type == 'start':
            pose = task.pickup_pose_name
        elif type == 'finish':
            pose = task.delivery_pose_name

        return pose

    def add_timepoint(self, id, task, type):
        """ A timepoint is represented by a node in the STN
        The node can be of type:
        - zero_timepoint: references the schedule to the origin
        - navigation: time at which the robot starts navigating towards the task
        - start: time at which the robot starts executing the task
        - finish: time at which the robot finishes executing the task
        """
        pose = self.get_node_pose(task, type)
        node = Node(task.id, pose, type)
        self.add_node(id, data=node.to_dict())

    def add_task(self, task, position):
        """ A task is added as 3 timepoints and 5 constraints in the STN"
        Timepoints:
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

        Note: Position 0 is reserved for the zero_timepoint
        Add tasks from postion 1 onwards
        """
        self.logger.info("Adding task %s in position %s", task.id, position)

        navigation_node_id = 2 * position + (position-2)
        start_node_id = navigation_node_id + 1
        finish_node_id = start_node_id + 1

        # Remove constraint linking navigation_node_id and previous node (if any)
        if self.has_edge(navigation_node_id-1, navigation_node_id) and navigation_node_id-1 != 0:
            self.logger.debug("Deleting constraint: %s  => %s", navigation_node_id-1, navigation_node_id)

            self.remove_constraint(navigation_node_id-1, navigation_node_id)

        # Displace by 3 all nodes and constraints after position
        mapping = {}
        for node_id, data in self.nodes(data=True):
            if node_id >= navigation_node_id:
                mapping[node_id] = node_id + 3
        self.logger.debug("mapping: %s ", mapping)
        nx.relabel_nodes(self, mapping, copy=False)

        # Add new timepoints
        self.add_timepoint(navigation_node_id, task, "navigation")
        self.add_timepoint_constraints(navigation_node_id, task, "navigation")

        self.add_timepoint(start_node_id, task, "start")
        self.add_timepoint_constraints(start_node_id, task, "start")

        self.add_timepoint(finish_node_id, task, "finish")
        self.add_timepoint_constraints(finish_node_id, task, "finish")

        # Add constraints between new nodes
        new_constraints_between = [navigation_node_id, start_node_id, finish_node_id]

        # Check if there is a node after the new delivery node
        if self.has_node(finish_node_id+1):
            new_constraints_between.append(finish_node_id+1)

        # Check if there is a node before the new start node
        if self.has_node(navigation_node_id-1):
            new_constraints_between.insert(0, navigation_node_id-1)

        self.logger.debug("New constraints between nodes: %s", new_constraints_between)

        constraints = [((i), (i + 1)) for i in new_constraints_between[:-1]]
        self.logger.debug("Constraints: %s", constraints)

        self.add_intertimepoints_constraints(constraints, task)

    def add_intertimepoints_constraints(self, constraints, task):
        """ Adds constraints between the timepoints of a task
        Constraints between:
        - navigation start and start
        - start and finish
        - finish and next task (if any)
        Args:
            constraints (list) : list of tuples that defines the pair of nodes between which a new constraint should be added
            Example:
            constraints = [(1, 2), (2, 3)]
            New constraints will be added between nodes 1 and 2 and between 2 and 3

            task (Task): task represented by the constraints
        """
        for (i, j) in constraints:
            self.logger.debug("Adding constraint: %s ", (i, j))
            if self.node[i]['data']['type'] == "navigation":
                duration = self.get_navigation_duration(i, j)
                self.add_constraint(i, j, duration)

            elif self.node[i]['data']['type'] == "start":
                duration = self.get_task_duration(task)
                self.add_constraint(i, j, duration)

            elif self.node[i]['data']['type'] == "finish":
                # wait time between finish of one task and start of the next one. Fixed to [0, inf]
                self.add_constraint(i, j)

    def get_navigation_duration(self, source, destination):
        """ Reads from the database the estimated duration for navigating from source to destination and takes the mean
        """
        # TODO: Read estimated duration from dataset
        duration = 6.0
        return duration

    def get_task_duration(self, task):
        """ Reads from the database the estimated duration of the task
        In the case of transportation tasks, the estimated duration is the navigation time from the pickup to the delivery location
        """
        # TODO: Read estimated duration from dataset
        duration = 4.0
        return duration

    def get_navigation_start_time(self, task):
        """ Returns the earliest_start_time and latest start navigation time
        """
        navigation_duration = self.get_navigation_duration(task.pickup_pose_name, task.delivery_pose_name)

        earliest_navigation_start_time = task.earliest_start_time - navigation_duration
        latest_navigation_start_time = task.latest_start_time - navigation_duration

        return earliest_navigation_start_time, latest_navigation_start_time

    def get_finish_time(self, task):
        """ Returns the earliest and latest finish time
        """
        task_duration = self.get_task_duration(task)

        earliest_finish_time = task.earliest_start_time + task_duration
        latest_finish_time = task.latest_start_time + task_duration

        return earliest_finish_time, latest_finish_time

    def show_n_nodes_edges(self):
        """ Prints the number of nodes and edges in the stn
        """
        self.logger.info("Nodes: %s ", self.number_of_nodes())
        self.logger.info("Edges: %s ", self.number_of_edges())

    def remove_task(self, position):
        """ Removes the task from the given position"""

        self.logger.info("Removing task at position: %s", position)
        navigation_node_id = 2 * position + (position-2)
        start_node_id = navigation_node_id + 1
        finish_node_id = start_node_id + 1

        new_constraints_between = list()

        if self.has_node(navigation_node_id-1) and self.has_node(finish_node_id+1):
            new_constraints_between = [navigation_node_id-1, navigation_node_id]

        # Remove node and all adjacent edges
        self.remove_node(navigation_node_id)
        self.remove_node(start_node_id)
        self.remove_node(finish_node_id)

        # Displace by -3 all nodes and constraints after position
        mapping = {}
        for node_id, data in self.nodes(data=True):
            if node_id >= navigation_node_id:
                mapping[node_id] = node_id - 3
        self.logger.debug("mapping: %s", mapping)
        nx.relabel_nodes(self, mapping, copy=False)

        if new_constraints_between:
            constraints = [((i), (i + 1)) for i in new_constraints_between[:-1]]
            self.logger.debug("Constraints: %s", constraints)

            for (i, j) in constraints:
                if self.node[i]['data']['type'] == "finish":
                    # wait time between finish of one task and start of the next one
                    self.add_constraint(i, j)

    def get_tasks(self):
        """
        Gets the tasks (in order)
        Each timepoint in the STN is associated with a task.
        return  list of task ids
        """
        scheduled_tasks = list()
        for i in self.nodes():
            timepoint = Node.from_dict(self.node[i]['data'])
            if timepoint.type == "navigation":
                scheduled_tasks.append(timepoint.task_id)

        return scheduled_tasks

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
            return float(self[i][j]['weight'])
        else:
            if i == j and self.has_node(i):
                return 0
            else:
                return float('inf')

    def get_completion_time(self):
        nodes = list(self.nodes())
        node_first_task = nodes[1]
        node_last_task = nodes[-1]

        start_time_lower_bound = -self[node_first_task][0]['weight']

        finish_time_lower_bound = -self[node_last_task][0]['weight']

        self.logger.debug("Start time: %s", start_time_lower_bound)
        self.logger.debug("Finish time: %s", finish_time_lower_bound)

        completion_time = finish_time_lower_bound - start_time_lower_bound

        return completion_time

    def get_makespan(self):
        nodes = list(self.nodes())
        node_last_task = nodes[-1]
        last_task_finish_time = - self[node_last_task][0]['weight']

        return last_task_finish_time

    def add_timepoint_constraints(self, node_id, task, type):
        """ Adds the earliest and latest times to execute a timepoint (node)
        Navigation timepoint [earliest_navigation_start_time, latest_navigation_start_time]
        Start timepoint [earliest_start_time, latest_start_time]
        Finish timepoint [earliest_finish_time, lastest_finish_time]
        """

        if task.hard_constraints:
            self.timepoint_hard_constraints(node_id, task, type)
        else:
            self.timepoint_soft_constraints(node_id, task, type)

    def timepoint_hard_constraints(self, node_id, task, type):
        if type == "navigation":
            earliest_navigation_start_time, latest_navigation_start_time = self.get_navigation_start_time(task)

            self.add_constraint(0, node_id, earliest_navigation_start_time, latest_navigation_start_time)

        if type == "start":
            self.add_constraint(0, node_id, task.earliest_start_time, task.latest_start_time)

        elif type == "finish":
            earliest_finish_time, latest_finish_time = self.get_finish_time(task)

            self.add_constraint(0, node_id, earliest_finish_time, latest_finish_time)

    def timepoint_soft_constraints(self, node_id, task, type):
        if type == "navigation":
            self.add_constraint(0, node_id)

        if type == "start":
            self.add_constraint(0, node_id)

        elif type == "finish":

            self.add_constraint(0, node_id, 0, self.max_makespan)

    def to_json(self):
        dict_json = json_graph.node_link_data(self)
        MyEncoder().encode(dict_json)
        stn_json = json.dumps(dict_json, cls=MyEncoder)

        return stn_json

    @classmethod
    def from_json(cls, stn_json):
        stn = cls()
        dict_json = json.loads(stn_json)
        graph = json_graph.node_link_graph(dict_json)
        stn.add_nodes_from(graph.nodes(data=True))
        stn.add_edges_from(graph.edges(data=True))

        return stn

    @classmethod
    def from_dict(cls, stn_json):
        stn = cls()
        dict_json = json.load(stn_json)
        graph = json_graph.node_link_graph(dict_json)
        cls.add_nodes_from(graph.nodes(data=True))
        cls.add_edges_from(graph.edges(data=True))
        return cls
