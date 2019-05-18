import json
import networkx as nx
import matplotlib.pyplot as plt
from structs.task import Task
from stntools.stn import Node, Edge, STN

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

        new_node = Node(new_node_id, task, is_task_start=node['is_task_start'], is_task_end=node['is_task_end'])

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


if __name__ == "__main__":

    stn_dict = get_stn_dict()
    stn = create_stn_from_dict(stn_dict)

    print("Nodes:", stn.nodes.data())
    print("Edges:", stn.edges.data())

    print("Minimal STN")
    minimal_stn = nx.floyd_warshall(stn)
    print(minimal_stn)
    print(stn.is_consistent(minimal_stn))

    nx.draw(stn, with_labels=True, font_weight='bold')
    plt.show()



    #https://stackoverflow.com/questions/48543460/how-to-use-user-defined-class-object-as-a-networkx-node
