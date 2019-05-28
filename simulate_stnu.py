import json
import networkx as nx
import numpy as np
from src.structs.task import Task
from src.temporal_networks.stnu import Node, Constraint, STNU
from src.temporal_networks.simulator import Simulator

MAX_SEED = 2 ** 31 - 1
"""The maximum number a random seed can be."""


def get_stnu_dict():
    """Reads an STNU from a json file and returns it as a dict"""
    with open('data/stnu_two_tasks.json') as json_file:
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

    stnu_dict = get_stnu_dict()
    stnu = STNU.from_dict(stnu_dict)

    print("STNU: ", stnu)
    print("Nodes: {}\n".format(stnu.nodes.data()))
    print("Edges: {}\n".format(stnu.edges.data()))

    # stnu2_dict = stnu.to_dict()
    #
    # stnu2 = STNU.from_dict(stnu2_dict)
    #
    # print("STNU2: ", stnu)
    # print("Nodes: {}\n".format(stnu2.nodes.data()))
    # print("Edges: {}\n".format(stnu2.edges.data()))

    # print("Calculating the minimal STNU...")
    # minimal_stnu = nx.floyd_warshall(stnu)
    # print(minimal_stnu)
    # print('')
    #
    # if stnu.is_consistent(minimal_stnu):
    #     print("The STNU is consistent")
    #     stnu.update_edges(minimal_stnu)
    #     stnu.update_time_schedule(minimal_stnu)
    #
    # print("Completion time: ", stnu.get_completion_time())
    # print("Makespan: ", stnu.get_makespan())
    # nx.draw(stnu, with_labels=True, font_weight='bold')
    # plt.show()

    # print('')
    print("Simulating execution of STNU")
    simulate(stnu, 'srea')
