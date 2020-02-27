from stn.stn import STN
from json import JSONEncoder
import logging
from stn.task import TimepointConstraint


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
                    timepoint = self.nodes[j]['data']
                    lower_bound = -self[j][i]['weight']
                    upper_bound = self[i][j]['weight']
                    to_print += "Timepoint {}: [{}, {}]".format(timepoint, lower_bound, upper_bound)
                    if timepoint.is_executed:
                        to_print += " Ex"
                # Constraints between the other timepoints
                else:
                    if self[j][i]['is_contingent'] is True:
                        to_print += "Constraint {} => {}: [{}, {}] (contingent)".format(i, j, -self[j][i]['weight'], self[i][j]['weight'])
                        if self[i][j]['is_executed']:
                            to_print += " Ex"
                    else:

                        to_print += "Constraint {} => {}: [{}, {}]".format(i, j, -self[j][i]['weight'], self[i][j]['weight'])
                        if self[i][j]['is_executed']:
                            to_print += " Ex"

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

        I a constraint is not contingent, then it is of node_type requirement and its value is assigned by the system.
        """

        super().add_constraint(i, j, wji, wij)

        self.add_edge(i, j, is_contingent=is_contingent)
        self.add_edge(j, i, is_contingent=is_contingent)

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
        contingent_timepoints = list()

        for (i, j, data) in self.edges.data():
            if self[i][j]['is_contingent'] is True and i < j:
                contingent_timepoints.append(j)

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
            if self.nodes[i]['data'].node_type == "start":
                lower_bound, upper_bound = self.get_travel_time_bounded_duration(task)
                if lower_bound == upper_bound:
                    self.add_constraint(i, j, 0, 0)
                else:
                    self.add_constraint(i, j, lower_bound, upper_bound, is_contingent=True)

            elif self.nodes[i]['data'].node_type == "pickup":
                lower_bound, upper_bound = self.get_work_time_bounded_duration(task)
                self.add_constraint(i, j, lower_bound, upper_bound, is_contingent=True)

            elif self.nodes[i]['data'].node_type == "delivery":
                # wait time between finish of one task and start of the next one. Fixed to [0, inf]
                self.add_constraint(i, j, 0)

    @staticmethod
    def get_travel_time_bounded_duration(task):
        """ Returns the estimated travel time as a bounded interval
        [mu - 2*sigma, mu + 2*sigma]
        as in:
        Shyan Akmal, Savana Ammons, Hemeng Li, and James Boerkoel Jr. Quantifying Degrees of Controllability in Temporal Networks with Uncertainty. In
        Proceedings of the 29th International Conference on Automated Planning and Scheduling, ICAPS 2019, 07 2019.
        """
        travel_time = task.get_inter_timepoint_constraint("travel_time")
        lower_bound = travel_time.mean - 2*travel_time.standard_dev
        upper_bound = travel_time.mean + 2*travel_time.standard_dev

        return lower_bound, upper_bound

    @staticmethod
    def get_work_time_bounded_duration(task):
        """ Returns the estimated work time as a bounded interval
        [mu - 2*sigma, mu + 2*sigma]
        as in:
        Shyan Akmal, Savana Ammons, Hemeng Li, and James Boerkoel Jr. Quantifying Degrees of Controllability in Temporal Networks with Uncertainty. In
        Proceedings of the 29th International Conference on Automated Planning and Scheduling, ICAPS 2019, 07 2019.
        """
        work_time = task.get_inter_timepoint_constraint("work_time")
        lower_bound = work_time.mean - 2*work_time.standard_dev
        upper_bound = work_time.mean + 2*work_time.standard_dev

        return lower_bound, upper_bound

    @staticmethod
    def get_prev_timepoint_constraint(constraint_name, next_timepoint_constraint, inter_timepoint_constraint):
        r_earliest_time = next_timepoint_constraint.r_earliest_time - \
                          (inter_timepoint_constraint.mean + 2*inter_timepoint_constraint.standard_dev)
        r_latest_time = next_timepoint_constraint.r_latest_time - \
                          (inter_timepoint_constraint.mean - 2*inter_timepoint_constraint.standard_dev)

        return TimepointConstraint(constraint_name, r_earliest_time, r_latest_time)

    @staticmethod
    def get_next_timepoint_constraint(constraint_name, prev_timepoint_constraint, inter_timepoint_constraint):
        r_earliest_time = prev_timepoint_constraint.r_earliest_time + \
                          (inter_timepoint_constraint.mean - 2*inter_timepoint_constraint.standard_dev)
        r_latest_time = prev_timepoint_constraint.r_latest_time + \
                        (inter_timepoint_constraint.mean + 2*inter_timepoint_constraint.standard_dev)

        return TimepointConstraint(constraint_name, r_earliest_time, r_latest_time)

    @staticmethod
    def create_timepoint_constraints(r_earliest_pickup, r_latest_pickup, travel_time, work_time):
        start_constraint = TimepointConstraint(name="start",
                                               r_earliest_time=r_earliest_pickup - (travel_time.mean - 2*work_time.standard_dev),
                                               r_latest_time=r_latest_pickup - (travel_time.mean + 2*work_time.standard_dev))
        pickup_constraint = TimepointConstraint(name="pickup",
                                                r_earliest_time=r_earliest_pickup,
                                                r_latest_time=r_latest_pickup)
        delivery_constraint = TimepointConstraint(name="delivery",
                                                  r_earliest_time=r_earliest_pickup + work_time.mean - 2*work_time.standard_dev,
                                                  r_latest_time=r_latest_pickup + work_time.mean - 2*work_time.standard_dev)
        return [start_constraint, pickup_constraint, delivery_constraint]

