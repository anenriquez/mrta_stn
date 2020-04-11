# Based on
# https://github.com/HEATlab/Prob-in-Ctrl/blob/master/LP.py
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
import copy

import pulp
import sys
import logging
from math import ceil

"""
Computes the Degree of Strong Controllability (DSC) using an LP program as presented in:

Shyan Akmal, Savana Ammons, Hemeng Li, and James Boerkoel Jr. Quantifying Degrees of Controllability in Temporal Networks with Uncertainty. In
Proceedings of the 29th International Conference on Automated Planning and Scheduling, ICAPS 2019, 07 2019.
"""
# A global variable that stores the max float that will be used to deal with infinite edges.
MAX_FLOAT = sys.float_info.max


class DSC_LP(object):

    logger = logging.getLogger('stn.dsc_lp')

    def __init__(self, stnu):
        self.stnu = copy.deepcopy(stnu)
        self.constraints = stnu.get_constraints()
        self.contingent_constraints = stnu.get_contingent_constraints()
        self.contingent_timepoints = stnu.get_contingent_timepoints()

    def add_constraint(self, constraint, problem):
        """
        Add adds a constraint to the given LP problem
        """
        problem += constraint

    def setup(self, proportion=False, maxmin=False):
        """
        Initializes the LP problem and the LP variables
        proportion     Flag indicating whether we are
                              setting up LP to proportionally shrink contingent intervals
        maxmin         Flag indicating whether we are
                              setting up LP to maximize the min shrinked contingent intervals

        return   A tuple (bounds, deltas, prob) where bounds and
                  deltas are dictionaries of LP variables, and prob is the LP problem instance
        """
        bounds = {}
        epsilons = {}

        # Maximize for super and minimize for Subinterval
        if maxmin:
            prob = pulp.LpProblem('SuperInterval LP', pulp.LpMaximize)
        else:
            prob = pulp.LpProblem('Max Subinterval LP', pulp.LpMinimize)

        # NOTE: Our LP requires each event to occur within a finite interval.
        # If the input LP does not have finite interval specified for all events, we want to set the setMakespan to MAX_FLOAT (infinity) so the LP works
        #
        # We do not want to run minimal network first because we are going to modify the contingent edges in LP, while some constraints in  minimal network are obtained through contingent edges
        #
        # There might be better way to deal with this problem.
        # ##
        for (i, j) in self.stnu.edges():
            weight = self.stnu.get_edge_weight(i, j)
            if weight == float('inf'):
                self.stnu.update_edge_weight(i, j, MAX_FLOAT)

        # Store Original STN edges and objective variables for easy access. Not part of LP yet

        for i in self.stnu.nodes():
            bounds[(i, '+')] = pulp.LpVariable('t_%i_hi'%i, lowBound=0,
                                                upBound=self.stnu.get_edge_weight(0, i))

            lowbound = 0 if self.stnu.get_edge_weight(i, 0) == float('inf') else\
                                -self.stnu.get_edge_weight(i, 0)

            bounds[(i,'-')] = pulp.LpVariable('t_%i_lo'%i, lowBound=lowbound, upBound=None)

            self.add_constraint(bounds[(i, '-')] <= bounds[(i, '+')], prob)

            if i == 0:
                self.add_constraint(bounds[(i, '-')] == 0, prob)
                self.add_constraint(bounds[(i, '+')] == 0, prob)

            if i not in self.contingent_timepoints:
                self.add_constraint(bounds[(i, '-')] == bounds[(i, '+')], prob)

        if proportion:
            return (bounds, epsilons, prob)

        for (i, j) in self.constraints:
            if (i, j) in self.contingent_constraints:

                epsilons[(j, '+')] = pulp.LpVariable('eps_%i_hi' % j, lowBound=0, upBound=None)

                epsilons[(j, '-')] = pulp.LpVariable('eps_%i_lo' % j, lowBound=0, upBound=None)

                self.add_constraint(bounds[(j, '+')]-bounds[(i, '+')] ==
                        self.stnu.get_edge_weight(i, j) - epsilons[(j,'+')], prob)
                self.add_constraint(bounds[(j, '-')]-bounds[(i, '-')] ==
                        -self.stnu.get_edge_weight(j, i) + epsilons[(j, '-')], prob)

            else:
                # NOTE: We need to handle the infinite weight edges. Otherwise the LP would be infeasible
                upbound = MAX_FLOAT if self.stnu.get_edge_weight(i, j) == float('inf') \
                            else self.stnu.get_edge_weight(i, j)

                lowbound = MAX_FLOAT if self.stnu.get_edge_weight(j, i) == float('inf') \
                            else self.stnu.get_edge_weight(j, i)

                self.add_constraint(bounds[(j, '+')]-bounds[(i, '-')] <= upbound, prob)
                self.add_constraint(bounds[(i, '+')]-bounds[(j, '-')] <= lowbound, prob)

        return (bounds, epsilons, prob)

    def original_lp(self, naive_obj=False, debug=False):
        """ Runs the LP on the input STN
        naive_obj       Flag indicating if we are using the naive
                       objective function
        debug          Print optional status messages

        return      LP status
                    dictionary of the LP_variables for the bounds on timepoints
                    dictionary of LP variables for epsilons
        """

        bounds, epsilons, prob = self.setup()

        # Set up objective function for the LP
        if naive_obj:
            obj = sum([epsilons[(i, j)] for i, j in epsilons])
        else:
            eps = list()

            for i, j in self.contingent_constraints:
                c = self.stnu[i][j]['weight'] + self.stnu[j][i]['weight']

                eps.append((epsilons[(j, '+')]+epsilons[j, '-'])/c)
            obj = sum(eps)

        prob += obj, "Maximize the Super-Interval/Max-Subinterval for the input STN"

        # write LP into file for debugging (optional)
        if debug:
            prob.writeLP('original.lp')
            pulp.LpSolverDefault.msg = 10

        try:
            prob.solve()
        except Exception:
            self.logger.error("The model is invalid.")
            return 'Invalid', None, None

        # Report status message
        status = pulp.LpStatus[prob.status]
        if debug:
            self.logger.debug("Status: %s", status)

            for v in prob.variables():
                self.logger.debug("%s = %s ", v.name, v.varValue)

        if status != 'Optimal':
            self.logger.debug("The solution for LP is not optimal")
            return status, None, None
        return status, bounds, epsilons

    def new_interval(self, epsilons):
        """ Computes shrinked contingent intervals
        epsilons     a dictionary of epsilon returned by the LP program

        return      list of original contingent intervals
                    list of shrinked contingent intervals
        """
        original = list()
        shrinked = list()

        for (i, j) in self.contingent_constraints:
            orig = (-self.stnu[j][i]['weight'], self.stnu[i][j]['weight'])
            original.append(orig)

            low = epsilons[(j, '-')].varValue
            high = epsilons[(j, '+')].varValue

            self.stnu.shrink_contingent_constraint(i, j, low, high)
            new = (-self.stnu[j][i]['weight'], self.stnu[i][j]['weight'])
            shrinked.append(new)

        return original, shrinked

    def compute_dsc(self, original, shrinked):
        """ Computes degreee of strong controllability (DSC)
        original       A list of original contingent intervals
        shrinked       A list of shrinked contingent intervals

        return the value of degree of strong controllability
        """
        new = 1
        orig = 1
        for i in range(len(original)):
            x, y = original[i]
            orig = y-x

            a, b = shrinked[i]
            new = b-a

        dsc = float(new/orig)

        return dsc

    def get_stnu(self, bounds):
        for i, sign in bounds:
            if sign == '+':
                self.stnu.update_edge_weight(
                    0, i, ceil(bounds[(i, '+')].varValue))
            else:
                self.stnu.update_edge_weight(
                    i, 0, ceil(-bounds[(i, '-')].varValue))

        return self.stnu

    def get_schedule(self, bounds):
        """ Assigns a dispatching time to each requirement timepoint
        Contingent timepoints are not assgined a value. The value will be assigned at execution time by "Nature"
        """

        for i in self.stnu.nodes():
            if i not in self.contingent_timepoints:
                time = (bounds[(i, '-')].varValue + bounds[(i, '+')].varValue)/2
                self.stnu.update_edge_weight(0, i, time)
                self.stnu.update_edge_weight(i, 0, -time)
            else:
                # time = bounds[(i, '+')].varValue
                self.stnu.update_edge_weight(0, i, bounds[(i, '+')].varValue)
                self.stnu.update_edge_weight(i, 0, -bounds[(i, '-')].varValue)

        return self.stnu
