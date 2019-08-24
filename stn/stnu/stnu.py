from stn.stn import STN
from stn.stn import Node
from json import JSONEncoder
import logging


class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class STNU(STN):
    """ Represents a Simple Temporal Network with Uncertainties (STNU) as a networkx directed graph
    """
    logger = logging.getLogger('stn.stnu')

    def __init__(self):
        super().__init__()

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
                    if self[j][i]['is_contingent'] is True:
                        to_print += "Constraint {} => {}: [{}, {}] (contingent)".format(i, j, -self[j][i]['weight'], self[i][j]['weight'])
                    else:

                        to_print += "Constraint {} => {}: [{}, {}]".format(i, j, -self[j][i]['weight'], self[i][j]['weight'])

                to_print += "\n"

        return to_print

    def add_constraint(self, i, j, wji=0.0, wij=float('inf'), is_contingent=False):
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

        Types of constraints:
        - contingent constraint
        - requirement constraint

        A constraint is contingent if it is uncontrollable, i.e., its value is assigned by Nature at execution time.

        I a constraint is not contingent, then it is of type requirement and its value is assigned by the system.
        """

        super().add_constraint(i, j, wji, wij)

        self.add_edge(i, j, is_contingent=is_contingent)

        self.add_edge(j, i, is_contingent=is_contingent)

    def timepoint_hard_constraints(self, node_id, task, type):
        """ Adds the earliest and latest times to execute a timepoint (node)
        Navigation timepoint [0, inf]
        Start timepoint [earliest_start_time, latest_start_time]
        Finish timepoint [0, inf]
        """

        if type == "navigation":
            self.add_constraint(0, node_id, task.r_earliest_navigation_start_time)

        if type == "start":
            self.add_constraint(0, node_id, task.r_earliest_start_time, task.r_latest_start_time)

        elif type == "finish":
            self.add_constraint(0, node_id)

    def get_contingent_constraints(self):
        """ Returns a dictionary with the contingent constraints in the STNU
         {(starting_node, ending_node): self[i][j] }
        """
        contingent_constraints = dict()

        for (i, j, data) in self.edges.data():
            if self[i][j]['is_contingent'] is True and i < j:
                contingent_constraints[(i, j)] = self[i][j]

        return contingent_constraints

    def get_contingent_timepoints(self):
        """ Returns a list with the contingent (uncontrollable) timepoints in the STNU
        """
        timepoints = list(self.nodes)
        contingent_timepoints = list()

        for (i, j, data) in self.edges.data():
            if self[i][j]['is_contingent'] is True and i < j:
                contingent_timepoints.append(timepoints[j])

        return contingent_timepoints

    def shrink_contingent_constraint(self, i, j, low, high):
        if self.has_edge(i, j):
            self[i][j]['weight'] += high
            self[j][i]['weight'] -= low

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
            self.logger.debug("Adding constraint: %s ", (i, j))
            if self.node[i]['data']['type'] == "navigation":
                lower_bound, upper_bound = self.get_navigation_bounded_duration(i, j)
                self.add_constraint(i, j, lower_bound, upper_bound, is_contingent=True)

            elif self.node[i]['data']['type'] == "start":
                lower_bound, upper_bound = self.get_task_bounded_duration(task)
                self.add_constraint(i, j, lower_bound, upper_bound, is_contingent=True)

            elif self.node[i]['data']['type'] == "finish":
                # wait time between finish of one task and start of the next one. Fixed to [0, inf]
                self.add_constraint(i, j, 0)

    def get_navigation_bounded_duration(self, source, destination):
        """ Reads from the database the probability distribution for navigating from source to destination and converts it to a bounded interval
        [mu - 2*sigma, mu + 2*sigma]
        as in:
        Shyan Akmal, Savana Ammons, Hemeng Li, and James Boerkoel Jr. Quantifying Degrees of Controllability in Temporal Networks with Uncertainty. In
        Proceedings of the 29th International Conference on Automated Planning and Scheduling, ICAPS 2019, 07 2019.
        """
        # TODO: Read estimated distribution from database
        distribution = "N_1_1"
        name_split = distribution.split("_")
        # mean
        mu = float(name_split[1])
        # standard deviation
        sigma = float(name_split[2])

        lower_bound = mu - 2*sigma
        upper_bound = mu + 2*sigma

        return lower_bound, upper_bound

    def get_task_bounded_duration(self, task):
        """ Reads from the database the estimated distribution of the task
        In the case of transportation tasks, the estimated distribution is the navigation time from the pickup to the delivery location
        Converts the estimated distribution to a bounded interval
        [mu - 2*sigma, mu + 2*sigma]
        as in:
        Shyan Akmal, Savana Ammons, Hemeng Li, and James Boerkoel Jr. Quantifying Degrees of Controllability in Temporal Networks with Uncertainty. In
        Proceedings of the 29th International Conference on Automated Planning and Scheduling, ICAPS 2019, 07 2019.
        """
        # TODO: Read estimated distribution from database
        distribution = "N_4_1"
        name_split = distribution.split("_")
        # mean
        mu = float(name_split[1])
        # standard deviation
        sigma = float(name_split[2])

        lower_bound = mu - 2*sigma
        upper_bound = mu + 2*sigma

        return lower_bound, upper_bound
