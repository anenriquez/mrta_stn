# Based on https://github.com/HEATlab/DREAM/
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

import json
import networkx as nx
import numpy as np
from scheduler.structs.task import Task
from scheduler.temporal_networks.pstn import NodePSTN, ConstraintPSTN, PSTN
from scheduler.temporal_networks.simulator import Simulator

MAX_SEED = 2 ** 31 - 1
"""The maximum number a random seed can be."""


def get_pstn_dict():
    """Reads an STNU from a json file and returns it as a dict"""
    with open('unittests/data/pstn_two_tasks.json') as json_file:
        stnu_dict = json.load(json_file)
    return stnu_dict


def simulate(starting_stn, execution_strategy, random_seed=None):
    if random_seed is None:
        random_seed = np.random.randint(MAX_SEED)
    else:
        random_seed = int(random_seed)

    seed_gen = np.random.RandomState(random_seed)
    seed = seed_gen.randint(MAX_SEED)
    simulator = Simulator(seed)

    simulator.simulate(starting_stn, execution_strategy)
    reschedule_count = simulator.num_reschedules
    sent_count = simulator.num_sent_schedules

    # print("Assigned Times: {}".format(simulator.get_assigned_times()))
    # print("Successful?: {}".format(ans))

    # response_dict = {"sample_results": [ans], "reschedules":
    #                  [reschedule_count], "sent_schedules": [sent_count]}
    # return response_dict



if __name__ == "__main__":

    pstn_dict = get_pstn_dict()
    pstn = PSTN.from_dict(pstn_dict)

    print("PSTN: ", pstn)
    print("Nodes: {}\n".format(pstn.nodes.data()))
    print("Edges: {}\n".format(pstn.edges.data()))

    # stnu2_dict = pstn.to_dict()
    #
    # stnu2 = STNU.from_dict(stnu2_dict)
    #
    # print("STNU2: ", pstn)
    # print("Nodes: {}\n".format(stnu2.nodes.data()))
    # print("Edges: {}\n".format(stnu2.edges.data()))

    # print("Calculating the minimal STNU...")
    # minimal_stnu = nx.floyd_warshall(pstn)
    # print(minimal_stnu)
    # print('')
    #
    # if pstn.is_consistent(minimal_stnu):
    #     print("The STNU is consistent")
    #     pstn.update_edges(minimal_stnu)
    #     pstn.update_time_schedule(minimal_stnu)
    #
    # print("Completion time: ", pstn.get_completion_time())
    # print("Makespan: ", pstn.get_makespan())
    # nx.draw(pstn, with_labels=True, font_weight='bold')
    # plt.show()

    # print('')
    print("Simulating execution of STNU")
    simulate(pstn, 'srea')
