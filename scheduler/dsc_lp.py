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

import pulp
import sys
from scheduler.temporal_networks.stnu import STNU
from math import ceil


''' Converts an input STNU to LP form and computes its degree of controllability as presented in:
Shyan Akmal, Savana Ammons, Hemeng Li, and James Boerkoel Jr. Quantifying Degrees of Controllability in Temporal Networks with Uncertainty. In
Proceedings of the 29th International Conference on Automated Planning and Scheduling, ICAPS 2019, 07 2019.
'''

# A global variable that stores the max float that will be used to deal with infinite edges.
MAX_FLOAT = sys.float_info.max


def addConstraint(constraint, problem):
    """ Add adds a constraint to the given LP"""
    print("Adding constraint: ", constraint)
    problem += constraint


def setUp(stnu, proportion=False, maxmin=False):
    """ Initializes the LP problem and the LP variables
    @param stnu            An input STNU
    @param proportion     Flag indicating whether we are
                          setting up LP to proportionally shrink contingent intervals
    @param maxmin         Flag indicating whether we are
                          setting up LP to maximize the min shrinked contingent intervals

    @return   A tuple (bounds, deltas, prob) where bounds and
              deltas are dictionaries of LP variables, and prob is the LP problem instance
    """
    bounds = {}
    epsilons = {}

    # Maximize for super and minimize for Subinterval
    if maxmin:
        prob = pulp.LpProblem('SuperInterval LP', pulp.LpMaximize)
    else:
        prob = pulp.LpProblem('Max Subinterval LP', pulp.LpMinimize)

    # ##
    # NOTE: Our LP requires each event to occur within a finite interval.
    # If the input LP does not have finite interval specified for all events, we want to set the setMakespan to MAX_FLOAT (infinity) so the LP works
    #
    # We do not want to run minimal network first because we are going to modify the contingent edges in LP, while some constraints in  minimal network are obtained through contingent edges
    #
    # There might be better way to deal with this problem.
    # ##
    for (i, j) in stnu.edges():
        weight = stnu.get_edge_weight(i, j)
        if weight == float('inf'):
            stnu.update_edge_weight(i, j, MAX_FLOAT)

    # ##
    # Store Original STN edges and objective variables for easy access.
    # Not part of LP yet
    # ##
    contingent_timepoints = stnu.get_contingent_timepoints()
    print("Contingent timepoints: ", contingent_timepoints)

    for i in stnu.nodes():
        print("Node: ", i)
        bounds[(i, '+')] = pulp.LpVariable('t_%i_hi'%i, lowBound=0,
                                            upBound=stnu.get_edge_weight(0, i))

        lowbound = 0 if stnu.get_edge_weight(i, 0) == float('inf') else\
                            -stnu.get_edge_weight(i, 0)

        bounds[(i,'-')] = pulp.LpVariable('t_%i_lo'%i, lowBound=lowbound, upBound=None)

        addConstraint(bounds[(i, '-')] <= bounds[(i, '+')], prob)

        if i == 0:
            addConstraint(bounds[(i, '-')] == 0, prob)
            addConstraint(bounds[(i, '+')] == 0, prob)

        if i not in contingent_timepoints:
            print("Adding constraint for ", i)
            addConstraint(bounds[(i, '-')] == bounds[(i, '+')], prob)

    if proportion:
        return (bounds, epsilons, prob)

    contingent_constraints = stnu.get_contingent_constraints()

    print("----------")
    constraints = stnu.get_constraints()

    print("Constraints: ", constraints)
    print("Contigent constraints: ", contingent_constraints)

    for (i, j) in constraints:
        if (i, j) in contingent_constraints:
            print("Contingent constraint: ", (i, j))

            epsilons[(j, '+')] = pulp.LpVariable('eps_%i_hi' % j, lowBound=0, upBound=None)

            epsilons[(j, '-')] = pulp.LpVariable('eps_%i_lo' % j, lowBound=0, upBound=None)

            addConstraint(bounds[(j, '+')]-bounds[(i, '+')] ==
                    stnu.get_edge_weight(i, j) - epsilons[(j,'+')], prob)
            addConstraint(bounds[(j, '-')]-bounds[(i, '-')] ==
                    -stnu.get_edge_weight(j, i) + epsilons[(j, '-')], prob)

        else:
            # NOTE: We need to handle the infinite weight edges. Otherwise the LP would be infeasible
            upbound = MAX_FLOAT if stnu.get_edge_weight(i, j) == float('inf') \
                        else stnu.get_edge_weight(i, j)

            lowbound = MAX_FLOAT if stnu.get_edge_weight(j, i) == float('inf') \
                        else stnu.get_edge_weight(j, i)

            addConstraint(bounds[(j, '+')]-bounds[(i, '-')] <= upbound, prob)
            addConstraint(bounds[(i, '+')]-bounds[(j, '-')] <= lowbound, prob)

    return (bounds, epsilons, prob)

##
# \fn originalLP(STN, naiveObj=False, debug=False):
# \brief Runs the LP on the input STN
#
# @param STN            An input STNU
# @param naiveObj       Flag indicating if we are using the naive objective
#                       function
# @param debug          Print optional status messages
#
# @return   LP status, A dictionary of the LP_variables for the bounds on
#           timepoints and a dictionary of LP variables for epsilons


def originalLP(stnu, naiveObj=False, debug=False):

    bounds, epsilons, prob = setUp(stnu)

    print("Bounds:")
    for bound in bounds:
        print("{}:{}".format(bound, bounds[bound]))
        print("")

    print("Epsilons:")
    for epsilon in epsilons:
        print("{}:{}".format(epsilon, epsilons[epsilon]))
        print("")
    print("prob: ", prob)

    # Set up objective function for the LP
    if naiveObj:
        Obj = sum([epsilons[(i, j)] for i, j in epsilons])
    else:
        eps = []
        contingent_constraints = stnu.get_contingent_constraints()

        for i, j in contingent_constraints:
            c = stnu[i][j]['weight'] + stnu[j][i]['weight']
            # c = stnu.edges[(i,j)].Cij + stnu.edges[(i,j)].Cji

            eps.append((epsilons[(j, '+')]+epsilons[j, '-'])/c )
        Obj = sum(eps)

    prob += Obj, "Maximize the Super-Interval/Max-Subinterval for the input STN"

    # write LP into file for debugging (optional)
    if debug:
        prob.writeLP('original.lp')
        pulp.LpSolverDefault.msg = 10

    try:
        prob.solve()
    except Exception:
        print("The model is invalid.")
        return 'Invalid', None, None

    # Report status message
    status = pulp.LpStatus[prob.status]
    if debug:
        print("Status: ", status)

        for v in prob.variables():
            print(v.name, '=', v.varValue)

    if status != 'Optimal':
        print("The solution for LP is not optimal")
        return status, None, None

    # print("Status: ", status)
    # print("Bounds: ", bounds)
    # print("Epsilons: ", epsilons)
    #
    # print("Original STNU")
    # print(stnu)
    #
    # for i, sign in bounds:
    #     if sign == '+':
    #         stnu.update_edge_weight(
    #             0, i, ceil(bounds[(i, '+')].varValue))
    #     else:
    #         stnu.update_edge_weight(
    #             i, 0, ceil(-bounds[(i, '-')].varValue))
    #
    # print("Updated STNU")
    # print(stnu)

    return status, bounds, epsilons


def newInterval(stnu, epsilons):
    """ Computes shrinked contingent intervals
    stnu         an input STNU
    epsilons     a dictionary of epsilon returned by the LP program

    return      list of original contingent intervals
                list of shrinked contingent intervals
    """
    original = list()
    shrinked = list()
    constraints = stnu.get_contingent_constraints()

    for (i, j) in constraints:
        orig = (-stnu[j][i]['weight'], stnu[i][j]['weight'])
        original.append(orig)

        low = epsilons[(j, '-')].varValue
        high = epsilons[(j, '+')].varValue

        stnu.shrink_contingent_constraint(i, j, low, high)
        new = (-stnu[j][i]['weight'], stnu[i][j]['weight'])
        shrinked.append(new)

    return original, shrinked


def calculateMetric(original, shrinked):
    """ Computes degreee of strong controllability (DSC)
    original       A list of original contingent intervals
    shrinked       A list of shrinked contingent intervals

    return the value of degree of strong controllability
    """
    for i in range(len(original)):
        x, y = original[i]
        orig = y-x

        a, b = shrinked[i]
        new = b-a

    dsc = float(new/orig)

    return dsc


def get_schedule(stnu, bounds):
    schedule = {}
    contingent_timepoints = stnu.get_contingent_timepoints()

    for i in stnu.nodes():
        if i not in contingent_timepoints:
            time = (bounds[(i, '-')].varValue + bounds[(i, '+')].varValue)/2
            schedule[i] = time

    return schedule
