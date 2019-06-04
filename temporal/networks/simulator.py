# Based on https://github.com/HEATlab/DREAM/blob/master/libheat/montsim.py
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

import numpy as np
import copy
from temporal.networks.srea import srea

Z_NODE_ID = 0


class Simulator(object):
    def __init__(self, random_seed=None):
        # Nothing here for now.
        self.stn = None
        self.assignment_stn = None
        self._current_time = 0.0

        self._rand_seed = random_seed
        self._rand_state = np.random.RandomState(random_seed)
        self.num_reschedules = 0
        self.num_sent_schedules = 0

    def simulate(self, starting_stn, execution_strat):
        """Run one simulation.

        Args:
            starting_stn (STN): The STN used to run in the simulation.
            execution_strat (str): The strategy to use for timepoint execution.
                Acceptable execution strategies include--
                "early",
                "srea"

            sim_options (dict, optional): A dictionary of possible options to
                pass into the simulator.

        Returns:
            Boolean indicating whether the simulation was successful or not.
        """
        # Initial setup
        self.stn = starting_stn
        self.assignment_stn = copy.deepcopy(starting_stn)
        self._current_time = 0.0
        self.num_reschedules = 0
        self.num_sent_schedules = 0

        print("Original STN: {}".format(self.stn))

        print("Contingent constraints: ", self.stn.contingent_constraints)

        for edge in self.stn.edges():
            i, j = edge
            if (i, j) in self.stn.contingent_constraints:
                print("Contingent constraint: ", self.stn.contingent_constraints[(i, j)])

        # Resample the contingent edges.
        # Super important!
        # print("Resampling contingent edges of stored STN")
        self.resample_stored_stn()

        # print("Resampled STN:\n {}".format(self.stn))

        for edge in self.stn.edges():
            i, j = edge
            if (i, j) in self.stn.contingent_constraints:
                print("Contingent edge: ", self.stn.contingent_constraints[(i, j)])

        # Setup options
        first_run = True
        options = {"first_run": True}

        # Setup default guide settings
        guide_stn = self.stn
        current_alpha = 0.0

        # For testing
        options["first_run"] = first_run
        if first_run:
            first_run = False

        # Calculate the guide STN.
        print("Getting Guide...")
        current_alpha, guide_stn = self.get_guide(execution_strat,
                                                  current_alpha,
                                                  guide_stn,
                                                  options=options)
        print("GUIDE")
        print(guide_stn)
        print("Alpha: ", current_alpha)

        # Loop until all timepoints (nodes) have been executed
        # while not self.all_executed():
        #     options["first_run"] = first_run
        #     if first_run:
        #         first_run = False
        #
        #     # Calculate the guide STN.
        #     print("Getting Guide...")
        #     current_alpha, guide_stn = self.get_guide(execution_strat,
        #                                               current_alpha,
        #                                               guide_stn,
        #                                               options=options)
        #     print("GUIDE")
        #     print(guide_stn)
        #
        #     # Select the next timepoint.
        #     print("Selecting timepoint...")
        #     selection = self.select_next_timepoint(guide_stn,
        #                                            self._current_time)
        #
        #     print("Selected timepoint, node_id of {} executed time {}"
        #                 .format(selection[0], selection[1]))
        #
        #     next_vert_id = selection[0]
        #     next_time = selection[1]
        #     executed_contingent = selection[2]
        #
        #     options["executed_contingent"] = executed_contingent
        #     options["executed_time"] = next_time
        #     options["guide_max"] = guide_stn.get_edge_data(0, next_vert_id)['weight']
        #     options["guide_min"] = -guide_stn.get_edge_data(next_vert_id, 0)['weight']
        #
        #     # Propagate constraints (minimise) and check consistency.
        #     self._assign_timepoint(guide_stn, next_vert_id, next_time)
        #     self._assign_timepoint(self.stn, next_vert_id, next_time)
        #     self._assign_timepoint(
        #         self.assignment_stn, next_vert_id, next_time)
        #
        #     stn_copy = copy.deepcopy(self.stn)
        #     consistent = self.propagate_constraints(stn_copy)
        #     print("Updated STN: ", stn_copy)
        #     if not consistent:
        #         print("Assignments: " + str(self.get_assigned_times()))
        #         print("Failed to place point {}, at {}"
        #                    .format(next_vert_id, next_time))
        #         return False
        #     self.stn = stn_copy
        #     pr.verbose("Done propagating our STN")
        #
        #     # Clean up the STN
        #     self.remove_old_timepoints(self.stn)
        #
        #     self._current_time = next_time
        # pr.verbose("Assignments: " + str(self.get_assigned_times()))
        # pr.verbose("Successful!")
        # assert (self.propagate_constraints(self.assignment_stn))
        # return True

    def select_next_timepoint(self, dispatch, current_time):
        """Retrieves the earliest possible vert.

        Ties are broken arbitrarily.

        Args:
            dispatch: STN which is used for getting the right dispatch.
            current_time: Current time of the simulation.

        Returns:
            Returns a tuple of (vert, time) where 'vert' is the vert ID
            of the vert which has the earliest assignment time, and 'time'
            If no timepoint can be selected, returns (None, inf)
        """
        earliest_so_far = None
        earliest_so_far_time = float("inf")
        has_incoming_contingent = False

        # This could be sped up. We only want unexecuted verts without parents.
        for i, vert in dispatch.verts.items():
            # Don't recheck already executed verts
            if vert.is_executed():
                continue
            # Check if all predecessors are executed -> enabled.
            predecessor_ids = [e.i for e in dispatch.get_incoming(i)]
            predecessors = [dispatch.get_vertex(q) for q in predecessor_ids]
            is_enabled = all([p.is_executed() for p in predecessors])
            # Exit early if not enabled.
            if not is_enabled:
                continue
            incoming_contingent = dispatch.get_incoming_contingent(i)
            if incoming_contingent is None:
                # Get the
                # Make sure that we can't go back in time though.
                incoming_reqs = dispatch.get_incoming(i)
                if incoming_reqs == []:
                    # No incoming edges at all, this will be our start.
                    earliest_time = 0.0
                else:
                    earliest_time = max([edge.get_weight_min()
                                         + self.stn.get_assigned_time(edge.i)
                                         for edge in incoming_reqs])
            else:
                sample_time = incoming_contingent.sampled_time()
                # Get the contingent edge's predecessor
                cont_pred = incoming_contingent.i
                assigned_time = dispatch.get_assigned_time(cont_pred)
                if assigned_time is None:
                    # This is an incredibly bizarre edge case that SREA
                    # sometimes produces: It alters the assigned points to
                    # an invalid time. One work around is to manually find the
                    # UPPER bound (not the lower bound), because that appears
                    # untouched by SREA.
                    pr.warning("Executed event was not assigned.")
                    pr.warning("Event was: {}".format(cont_pred))
                    vert = dispatch.get_vertex(cont_pred)
                    new_time = dispatch.get_edge_weight(Z_NODE_ID,
                                                        cont_pred)
                    msg = "Re-assigned to: {}".format(new_time)
                    pr.warning(msg)
                    earliest_time = new_time
                else:
                    edges = dispatch.edges
                    edge = edges[(0, vert.nodeID)]
                    print("We are on vertex: {} we are interested in edge {}".format(vert, edge))
                    earliest_start_time = -edge.Cji
                    # Earliest start time is in edge with node 0
                    print("Est: ", earliest_start_time)
                    earliest_time = dispatch.get_assigned_time(cont_pred) \
                        + sample_time
                        # Maybe the tasks is not supposed to start until an earliest start time, so wait (no need to hurry)

                    if earliest_time < earliest_start_time:
                        earliest_time = earliest_start_time

            # Update the earliest time  now.
            if earliest_so_far_time > earliest_time:
                earliest_so_far = i
                earliest_so_far_time = earliest_time
                has_incoming_contingent = (incoming_contingent is not None)
        return (earliest_so_far, earliest_so_far_time,
                has_incoming_contingent)

    def _assign_timepoint(self, stn, vert_id, time):
        """Assigns a timepoint to specified time

        Args:
            stn (STN): STN to assign on.
            vert_id (int): Node to assign.
            time (float): Time to assign to this vert.

        Post:
            stn is modified in-place to have an assigned vertex.
        """
        if vert_id != Z_NODE_ID:
            stn.update_edge_weight(Z_NODE_ID,
                            vert_id,
                            time,
                            create=True)
            stn.update_edge_weight(vert_id,
                            Z_NODE_ID,
                            -time,
                            create=True)
        # stn.get_vertex(vert_id).execute()
        self.stn.node[vert_id]['data'].execute()

    def propagate_constraints(self, stn_to_prop):
        """ Updates current constraints and minimises
        """
        minimal_stn = nx.floyd_warshall(stn_to_prop)
        stn_to_prop.update_edges(minimal_stn)
        return stn_to_prop.is_consistent(minimal_stn)

    def all_executed(self) -> bool:
        """ Check if all vertices of the STN have been executed.

        Returns:
            Boolean indicated whether all vertices in the assignment STN have
            been executed.
        """
        for node in self.stn.nodes():
            if not self.stn.node[node]['data'].is_executed():
                return False
        return True

    def remove_old_timepoints(self, stn) -> None:
        """ Remove timepoints which add no new information, as they exist
        entirely in the past, and have no lingering constraints that are not
        already captured.
        """
        stored_keys = list(stn.verts.keys())
        for v_id in stored_keys:
            if v_id == 0:
                continue
            if (stn.outgoing_executed(v_id) and
                    stn.get_vertex(v_id).is_executed()):
                stn.remove_vertex(v_id)

    def resample_stored_stn(self) -> None:
        """Resample the stored STN contingent edges (self.stn)"""
        #for edge, attr in self.stn.contingent_constraints.items():
        # print("Edge: ", edge)
        # print(self.stn[edge[0]][edge[1]])
        # constraint = self.stn[edge[0]][edge[1]]['data']
        # constraint.resample(self._rand_state)
        for constraint in self.stn.contingent_constraints.values():
            constraint.resample(self._rand_state)

    def get_assigned_times(self) -> dict:
        """Return the assigned time to each timepoint in the simulation"""
        times = {}
        for node_id in self.assignment_stn.nodes():
            if self.assignment_stn.node[node_id]['data'].is_executed():
                times[node_id] = (self.assignment_stn.get_assigned_time(node_id))
            else:
                times[node_id] = (None)

        return times

    def get_guide(self, execution_strat, previous_alpha,
                  previous_guide, options={}) -> tuple:
        """ Retrieve a guide STN (dispatch) based on the execution strategy

        Args:
            execution_strat (str): String representing the execution strategy.
            previous_alpha (float): The previously used guide STN's alpha.
            previous_guide (STN): The previously used guide STN.
            options (dict, optional): Dictionary of possible options to use for
                the algorithms.

        Return:
            Returns a tuple with format:
            | [0]: Alpha of the guide.
            | [1]: dispatch (type STN) which the simulator should follow,
        """
        if execution_strat == "early":
            return 1.0, self.stn
        elif execution_strat == "srea":
            return self._srea_algorithm(previous_alpha,
                                        previous_guide,
                                        options["first_run"])
        else:
            raise ValueError(("Execution strategy '{}'"
                              " unknown").format(execution_strat))

    def _srea_wrapper(self, previous_alpha, previous_guide):
        """ Small wrapper to run SREA or keep the same guide if it's not
            consistent.
        """
        self.num_reschedules += 1
        result = srea(self.stn, debug=True)
        if result is not None:
            self.num_sent_schedules += 1
            return result[0], result[1]
        # Our guide was inconsistent... um. Well.
        # This is not great.
        # Follow the previous guide?
        return previous_alpha, previous_guide

    def _srea_algorithm(self, previous_alpha, previous_guide, first_run):
        """ Implements the SREA algorithm. """
        if first_run:
            return self._srea_wrapper(previous_alpha, previous_guide)
        # Not our first run, use the previous guide.
        return previous_alpha, previous_guide
