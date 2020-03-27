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

import logging
from json import JSONEncoder

from stn.pstn.constraint import Constraint
from stn.stn import STN
from stn.task import TimepointConstraint


class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class PSTN(STN):
    """ Represents a Probabilistic Simple Temporal Network (PSTN) as a networkx directed graph
    """
    logger = logging.getLogger('stn.pstn')

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
                    if 'is_contingent' in self[j][i]:
                        to_print += "Constraint {} => {}: [{}, {}] ({})".format(i, j, -self[j][i]['weight'], self[i][j]['weight'], self[i][j]['distribution'])
                        if self[i][j]['is_executed']:
                            to_print += " Ex"
                    else:

                        to_print += "Constraint {} => {}: [{}, {}]".format(i, j, -self[j][i]['weight'], self[i][j]['weight'])
                        if self[i][j]['is_executed']:
                            to_print += " Ex"

                to_print += "\n"

        return to_print

    def add_constraint(self, i, j, wji=0.0, wij=float('inf'), distribution=""):
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

        # The constraint is contingent if it has a probability distribution
        is_contingent = distribution is not ""

        super().add_constraint(i, j, wji, wij)

        self.add_edge(i, j, distribution=distribution, is_contingent=is_contingent)
        self.add_edge(j, i, distribution=distribution, is_contingent=is_contingent)

    def get_contingent_constraints(self):
        """ Returns a dictionary with the contingent constraints in the PSTN
         {(starting_node, ending_node): Constraint (object)}
        """
        contingent_constraints = dict()

        for (i, j, data) in self.edges.data():
            if self[i][j]['is_contingent'] is True and i < j:
                contingent_constraints[(i, j)] = Constraint(i, j, self[i][j]['distribution'])

        return contingent_constraints

    def add_intertimepoints_constraints(self, constraints, task):
        """ Adds constraints between the timepoints of a task
        Constraints between:
        - start and pickup (contingent)
        - pickup and delivery (contingent)
        - delivery and next task (if any) (requirement)
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
                distribution = self.get_travel_time_distribution(task)
                if distribution.endswith("_0.0"):  # the distribution has no variation (stdev is 0)
                    # Make the constraint a requirement constraint
                    mean = float(distribution.split("_")[1])
                    self.add_constraint(i, j, mean, mean)
                else:
                    self.add_constraint(i, j, distribution=distribution)

            elif self.nodes[i]['data'].node_type == "pickup":
                distribution = self.get_work_time_distribution(task)
                self.add_constraint(i, j, distribution=distribution)

            elif self.nodes[i]['data'].node_type == "delivery":
                # wait time between finish of one task and start of the next one. Fixed to [0, inf]
                self.add_constraint(i, j)

    @staticmethod
    def get_travel_time_distribution(task):
        travel_time = task.get_inter_timepoint_constraint("travel_time")
        travel_time_distribution = "N_" + str(travel_time.mean) + "_" + str(travel_time.standard_dev)
        return travel_time_distribution

    @staticmethod
    def get_work_time_distribution(task):
        work_time = task.get_inter_timepoint_constraint("work_time")
        work_time_distribution = "N_" + str(work_time.mean) + "_" + str(work_time.standard_dev)
        return work_time_distribution

    @staticmethod
    def get_prev_timepoint_constraint(constraint_name, next_timepoint_constraint, inter_timepoint_constraint):
        r_earliest_time = 0
        r_latest_time = float('inf')
        return TimepointConstraint(constraint_name, r_earliest_time, r_latest_time)

    @staticmethod
    def get_next_timepoint_constraint(constraint_name, prev_timepoint_constraint, inter_timepoint_constraint):
        r_earliest_time = 0
        r_latest_time = float('inf')
        return TimepointConstraint(constraint_name, r_earliest_time, r_latest_time)

    @staticmethod
    def create_timepoint_constraints(r_earliest_pickup, r_latest_pickup, travel_time, work_time):
        start_constraint = TimepointConstraint(name="start",
                                               r_earliest_time=r_earliest_pickup - (travel_time.mean - 2*work_time.standard_dev),
                                               r_latest_time=float('inf'))
        pickup_constraint = TimepointConstraint(name="pickup",
                                                r_earliest_time=r_earliest_pickup,
                                                r_latest_time=r_latest_pickup)
        delivery_constraint = TimepointConstraint(name="delivery",
                                                  r_earliest_time= 0,
                                                  r_latest_time=float('inf'))
        return [start_constraint, pickup_constraint, delivery_constraint]
