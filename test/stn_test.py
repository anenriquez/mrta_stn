import json
import networkx as nx
from structs.task import Task
from temporal.stn import Node, Edge, STN

def get_stn_dict():
    """Reads an STN from a json file and returns it as a dict"""
    with open('data/stn_two_tasks.py') as json_file:
        stn_dict = json.load(json_file)
    return stn_dict

def create_stn_from_dict(stn_dict):
    stn = STN()
    # Adding the zero timepoint
    zero_timepoint = Node(0)
    stn.add_node(0, data=zero_timepoint)

    for node in stn_dict['nodes']:
        task = Task.from_dict(node['task'])
        new_node_id = node['id']

        new_node = Node(new_node_id, task, start_task=node['is_task_start'], end_task=node['is_task_end'])

        stn.add_node(new_node_id, data=new_node)

        if node['is_task_start']:
            earliest_start_time = Edge(new_node.id, zero_timepoint.id, -task.earliest_start_time)
            latest_start_time = Edge(zero_timepoint.id, new_node.id, task.latest_start_time)
            stn.add_constraint(earliest_start_time)
            stn.add_constraint(latest_start_time)

        elif node['is_task_end']:
            earliest_finish_time = Edge(new_node.id, zero_timepoint.id, -task.earliest_finish_time)
            latest_finish_time = Edge(zero_timepoint.id, new_node.id, task.latest_start_time)

            stn.add_constraint(earliest_finish_time)
            stn.add_constraint(latest_finish_time)

    for edge in stn_dict['edges']:

        # print("Getting some info..")
        # print(stn.node[edge['starting_node']]['data'].task)

        new_constraint = Edge(edge['starting_node'], edge['ending_node'], edge['weight'], edge['distribution'])
        stn.add_constraint(new_constraint)

    return stn


# def get_execution_guide(execution_strat, previous_alpha, previous_guide):
#     """ Retrieve a guide STN (dispatch) based on the execution strategy
#
#         Args:
#             execution_strat (str): String representing the execution strategy.
#             previous_alpha (float): The previously used guide STN's alpha.
#             previous_guide (STN): The previously used guide STN.
#
#         Return:
#             Returns a tuple with format:
#             | [0]: Alpha of the guide.
#             | [1]: dispatch (type STN) which the simulator should follow,
#         """
#     if execution_strat == "early":
#         return 1.0, self.stn
#     elif execution_strat == "srea":
#         return self.srea_algorithm(previous_alpha,
#                                     previous_guide)
#
#
# def srea_algorithm(previous_alpha, previous_guide):
#     result = srea.srea(self.stn)
#         if result is not None:
#             self.num_sent_schedules += 1
#             return result[0], result[1]
#         # Our guide was inconsistent... um. Well.
#         # This is not great.
#         # Follow the previous guide?
#         return previous_alpha, previous_guide

if __name__ == "__main__":

    stn_dict = get_stn_dict()
    stn = create_stn_from_dict(stn_dict)

    print("Nodes:", stn.nodes.data())
    # print("Edges:", stn.edges.data())
    print("Edges: ", stn.edges.data())

    # print("Edge data:", stn[1][0])
    # dict_edges = dict()
    # dict_edges[(1, 0)] = stn[1][0]
    # print("Dict of edges: ", dict_edges)

    # for constraint, attr in stn.contingent_constraints.items():
    #     print("Constant: ", constraint)
    #     constraint_obj = stn[constraint[0]][constraint[1]]['data']
    #     print("Distribution type: ", constraint_obj.dtype())
    #
    # for edge in stn.edges():
    #     print("Edge: ", edge[0], edge[1])

    print("Calculating the minimal STN...")
    minimal_stn = nx.floyd_warshall(stn)
    print(minimal_stn)

    if stn.is_consistent(minimal_stn):
        print("Updating the stn")
        # stn.update_edges(minimal_stn)
        stn.update_time_schedule(minimal_stn)

    print("Completion time: ", stn.get_completion_time())
    print("Makespan: ", stn.get_makespan())
    # nx.draw(stn, with_labels=True, font_weight='bold')
    # plt.show()



    #https://stackoverflow.com/questions/48543460/how-to-use-user-defined-class-object-as-a-networkx-node
