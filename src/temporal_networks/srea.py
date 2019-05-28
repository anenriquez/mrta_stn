# Based on https://github.com/HEATlab/DREAM/blob/master/libheat/srea.py
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

"""
Contains the core of the SREA algorithm.

This file is mostly unchanged from the original RobotBrunch code.

Authors: Jordan R Abrahams, Kyle Lund, Sam Dietrich
"""

from math import floor, ceil
import pulp
import copy
import networkx as nx

# from src.temporal_networks.stnu import STNU
from src.temporal_networks.stnu import STNU
# import src.temporal_networks.stnu.stnu
from src.temporal_networks.distempirical import invcdf_norm, invcdf_uniform

# \file SREA.py
#
#  \brief Runs the SREA algorithm on an input STN and computes the robustness
#
#  \details To run this file on an STN, use the command:
#  \code{.unparsed}
#  python SREA.py JSONFILE ALPHA
#  \endcode
#
#
#  \note You'll need pulp to be able to run this. On a linux machine run
#  `sudo pip install pulp` or `sudo easy_install -U pulp`.
#  THEN RUN `sudo pulptest`, otherwise it won't work.

# \fn addConstraint(constraint,problem)
#  \brief Adds an LP constraint to the given LP


def addConstraint(constraint, problem):
    problem += constraint
    # print 'adding constraint', constraint

# \fn setUpLP(stn)
#  \brief initializes the LP problem and the LP variables that will not change
#      with alpha
#  \returns A tuple (bounds, deltas, prob) where bounds and deltas are
#      dictionaries of LP variables, and prob is the LP problem instance


def setUpLP(stn, decouple):
    bounds = {}
    deltas = {}

    prob = pulp.LpProblem('PSTN Robust Execution LP', pulp.LpMaximize)

    print("Input STN: ", stn)

    # ##
    # Store Original STN edges and objective variables for easy access.
    # Not part of LP yet
    # ##

    for i in stn.nodes():
        print("SREA verts: ", i)
        bounds[(i, '+')] = pulp.LpVariable('t_%d_hi' % i,
                                           lowBound=-stn.get_edge_weight(i, 0),
                                           upBound=stn.get_edge_weight(0, i))
        print("Lower bound + : ", -stn.get_edge_weight(i, 0))
        print("Upper bound + : ", stn.get_edge_weight(0, i))
        bounds[(i, '-')] = pulp.LpVariable('t_%d_lo' % i,
                                           lowBound=-stn.get_edge_weight(i, 0),
                                           upBound=stn.get_edge_weight(0, i))
        print("Lower bound - : ", -stn.get_edge_weight(i, 0))
        print("Upper bound - : ", stn.get_edge_weight(0, i))

        condition = bounds[(i, '+')] >= bounds[(i, '-')]
        addConstraint(condition, prob)

    for edge in stn.edges():
        i, j = edge
        print("Edge ({}, {})".format(i, j))
        if (i, j) in stn.contingent_constraints:
            print("Contingent constraint: ", stn[i][j])
            print("{}, {}".format(i, j))
            deltas[(i, j)] = pulp.LpVariable('delta_%d_%d' %
                                             (i, j), lowBound=0, upBound=None)
            deltas[(j, i)] = pulp.LpVariable('delta_%d_%d' %
                                             (j, i), lowBound=0, upBound=None)

        else:
            # ignore edges from z. these edges are implicitly handled
            # with the bounds on the LP variables
            # also ignore complementary edges of contingent constraints
            if i != 0 and j != 0 and (j, i) not in stn.contingent_constraints and not decouple:
                print("Adding extra constraints ({}, {})".format(i, j))
                addConstraint(bounds[(j, '+')] - bounds[(i, '-')]
                              <= stn.get_edge_weight(i, j), prob)
                addConstraint(bounds[(i, '+')] - bounds[(j, '-')]
                              <= stn.get_edge_weight(j, i), prob)

            # For now, we dont have interagentEdges
            # elif edge[0] != 0 and (starting_node, ending_node) in stn.interagentEdges:
            #     addConstraint(bounds[(ending_node, '+')] - bounds[(starting_node, '-')]
            #                   <= stn.get_edge_weight(starting_node, ending_node), prob)
            #     addConstraint(bounds[(starting_node, '+')] - bounds[(ending_node, '-')]
            #                   <= stn.get_edge_weight(ending_node, starting_node), prob)
    return (bounds, deltas, prob)


##
# \fn srea(inputstn,debug=False,debugLP=False,lb=0.0,ub=0.999)
# \brief Runs the SREA algorithm on an input STN
#
# @param inputstn The STN that we are running SREA on
# @param invCDF_map A dictionary of dictionaries generated from a
#      distgenlib.invcdf_map call. See documentation there for more info.
# @param debug Print optional status messages about alpha levels
# @param debugLP Print optional status messages about each run of the LP
# @param lb The starting lower bound on alpha for the binary search
# @param ub The starting upper bound on alpha for the binary search
#
# @returns a tuple (alpha, outputstn) if there is a solution, or None if there
#     is no solution
def srea(inputstn,
         debug=False,
         debugLP=False,
         returnAlpha=True,
         decouple=False,
         lb=0.0,
         ub=0.999):
    # inputstn = inputstn.copy()
    inputstn = copy.deepcopy(inputstn)
    # dictionary of alphas for binary search
    alphas = {i: i / 1000.0 for i in range(1001)}

    # bounds for binary search
    lower = ceil(lb * 1000) - 1
    upper = floor(ub * 1000) + 1

    result = None

    # set up LP
    if not decouple:
        # TODO: Change to faster algorithm?
        # inputstn.floyd_warshall()
        minimal_stn = nx.floyd_warshall(inputstn)
        inputstn.update_edges(minimal_stn)
    bounds, deltas, probBase = setUpLP(inputstn, decouple)

    print("Bounds:")
    for bound in bounds:
        print("{}:{}".format(bound, bounds[bound]))
        print("")

    print("Deltas:")
    for delta in deltas:
        print("{}:{}".format(delta, deltas[delta]))
        print("")
    print("probBase: ", probBase)

    # First run binary search on alpha
    while upper - lower > 1:
        alpha = alphas[(upper + lower) // 2]
        if debug:
            print('trying alpha = {}'.format(alpha))

        # run the LP
        probContainer = (bounds, deltas, probBase.copy())
        LPbounds = srea_LP(inputstn,
                           alpha,
                           decouple,
                           debug=debugLP,
                           probContainer=probContainer)

        # LP was feasible, try lower alpha
        if LPbounds is not None:
            upper = (upper + lower) // 2
            result = (alpha, LPbounds)
        # LP was infeasable, try higher alpha
        else:
            lower = (upper + lower) // 2

        # finished our search, load the smallest alpha decoupling
        if upper - lower <= 1:
            if result is not None:
                alpha, LPbounds = result
                if debug:
                    print(
                        'modifying STN with lowest good alpha, {}'.format(alpha))
                for i, sign in LPbounds:
                    if sign == '+':
                        inputstn.update_edge_weight(
                            0, i, ceil(bounds[(i, '+')].varValue))
                    else:
                        inputstn.update_edge_weight(
                            i, 0, ceil(-bounds[(i, '-')].varValue))

                if returnAlpha:
                    return alpha, inputstn
                else:
                    return inputstn
    # skip the rest if there was no decoupling at all
    if result is None:
        if debug:
            print('could not produce feasible LP.')
        return None

    # Fail here
    assert(False)


# \fn srea_LP(inputstn,alpha,debug=False,probContainer=None)
#  \brief Runs the robust execution LP on the input STN at the given alpha
#  level
#
#  @param inputSTN The STN used as an input to the LP
#  @param invCDF_map A dictionary of dictionaries generated from a
#       distgenlib.invcdf_map call. See documentation there for more info.
#  @param alpha The risk level (between 0 and 1) that we are using for the LP
#  @param decouple originally was meant to indicate if we wanted decoupling or not
#   but then we discovered that this already decouples the STN
#  @param debug Print optional status messages
#  @param probContainer Optional tuple of LP variables and the LP problem
#       instance, returned from setUpLP
#
#  \returns A dictionary of the LP_variables for the bounds on timepoints.
def srea_LP(inputstn,
            alpha,
            decouple,
            debug=False,
            probContainer=None
            ):

    # Check some types to make sure everything is the correct type
    if not isinstance(inputstn, STNU):
        raise TypeError("inputstn is not of type STN")

    alpha = round(float(alpha), 3)

    if probContainer is None:
        if debug:
            print('No saved LP variables, generating all LP variables from current STN')
        bounds, deltas, prob = setUpLP(inputstn, decouple)
    else:
        bounds, deltas, prob = probContainer

    for (i, j), constraint in inputstn.contingent_constraints.items():
        # starting_node, ending_node = edge
        # constraint = inputstn[starting_node][ending_node]['data']
        if constraint.dtype() == "gaussian":
            p_ij = invcdf_norm(1.0 - alpha * 0.5, constraint.mu, constraint.sigma)
            p_ji = -invcdf_norm(alpha * 0.5, constraint.mu, constraint.sigma)
            limit_ij = invcdf_norm(0.997, constraint.mu, constraint.sigma)
            limit_ji = -invcdf_norm(0.003, constraint.mu, constraint.sigma)

        elif constraint.dtype() == "uniform":
            p_ij = invcdf_uniform(1.0 - alpha * 0.5, constraint.dist_lb,
                                  constraint.dist_ub)
            p_ji = -invcdf_uniform(alpha * 0.5, constraint.dist_lb, constraint.dist_ub)
            limit_ij = invcdf_uniform(0.0, constraint.dist_lb, constraint.dist_ub)
            limit_ji = -invcdf_uniform(1.0, constraint.dist_lb, constraint.dist_ub)

        deltas[(i, j)].upBound = limit_ij - p_ij
        deltas[(i, j)].upBound = limit_ji - p_ji

        cons1 = bounds[(j, "+")] - bounds[(i, "+")] == p_ij + deltas[(i, j)]
        cons2 = bounds[(j, "-")] - bounds[(i, "-")] == -p_ji - deltas[(j, i)]
        # Lund et al. LP (3)
        addConstraint(cons1, prob)
        # Lund et al. LP (4)
        addConstraint(cons2, prob)
    # ##
    # Generate the objective function.
    #   Our objective function is SUM delta_ij
    # ##
    deltaSum = sum([deltas[(i, j)] for i, j in deltas])
    prob += deltaSum, 'Maximize time added back to \
        constraints while decoupling'

    if debug:
        prob.writeLP('STN.lp')
        pulp.LpSolverDefault.msg = 10

    # for RPi only
    # mySolver = solvers.GLPK()
    # prob.solve(solver=mySolver)
    # This try except exists because there was a weird bug with Pulp where
    # it was throwing an error instead of just saying that the lp was not
    # resolvable.  I don't know much about the inner workings of pulp and
    # stack overflow suggested I put in this fix so I did.
    # https://stackoverflow.com/questions/27406858/pulp-solver-error
    # try:
    prob.solve()
    # except Exception:
    # return None

    status = pulp.LpStatus[prob.status]
    if debug:
        print('Status:', status)
        # Each of the variables is printed with it's resolved optimum value
        for v in prob.variables():
            print(v.name, '=', v.varValue)
    if status != 'Optimal':
        return None
    return bounds

# \fn getRobustness(stn)
# \brief Calls the rust simulator to compute the robustness of the input STN
# NOTE: This is now depracated
#
#
# def getRobustness(stn):
#    tempstn = 'json/temp.json'
#
#    with open(tempstn, 'w+') as f:
#        json.dump(stn.forJSON(), f, indent=2, separators=(',', ':'))
#
#    # Find the robustness of the decoupling
#    simulation = Popen(['../stpsimulator/target/release/simulator_stp',
#                        '--samples', str(10000),
#                        '--threads', '4',
#                        '--sample_directory', '../stpsimulator/samples/',
#                        tempstn],
#                       stdout=PIPE, stderr=PIPE)
#    simulation.wait()
#
#    dataRegex = re.compile(r'result:\n([0-9\.]+)')
#
#    # extract the robustness from simulator output
#    simData = simulation.stdout.read()
#    match = dataRegex.search(simData)
#
#    # simulator failed -- 0 robustness
#    if match is None:
#        return 0
#
#    return float(match.group(1))
#
#
# \fn getDispatch(stn)
# \brief performs srea on the given STN
##
# \returns STN that represents the dispatch strategy
# def getDispatch(stn, invCDF_map):
#
#    output = srea(stn, invCDF_map)
#
#    if output != None:
#        alpha, stn = output
#        # print getRobustness(stn)
#        stn.minimize()
#        for (starting_node, ending_node), edge in list(stn.contingent_edges.items()):
#            edge_i = stn.getEdge(0, starting_node)
#            edge_j = stn.getEdge(0, ending_node)
#            edge.Cij = edge_j.getWeightMax()-edge_i.getWeightMax()
#            edge.Cji = - (edge_j.getWeightMin()-edge_i.getWeightMin())
#            # this loop ensures that the output STN with integer edge weights is still
#            # strongly controllable
#            for connected_edge in stn.getOutgoing(ending_node):
#                edge.Cji = -max(-edge.Cji, edge.Cij -
#                                connected_edge.Cji-connected_edge.Cij)
#        return stn
#
#    print("srea did not result in a feasible LP, please try again with a different STN")
#    return None
