import unittest
import os
import yaml
import collections
from scheduler.structs.task import Task
from scheduler.temporal_networks.pstn import PSTN

DATASET = "data/two_tasks.yaml"


class TestBuildPSTN():
    def __init__(self):
        self.tasks = self.get_tasks()

    def get_tasks(self):
        my_dir = os.path.dirname(__file__)
        dataset_path = os.path.join(my_dir, DATASET)

        with open(dataset_path, 'r') as file:
            dataset = yaml.safe_load(file)

        tasks = list()
        ordered_tasks = collections.OrderedDict(sorted(dataset['tasks'].items(), reverse=True))

        for task_id, task in ordered_tasks.items():
            tasks.append(Task.from_dict(task))
        return tasks

    def test_add_tasks_consecutively(self):
        """ Adds tasks in consecutive positions. Example
        position 1, position 2, ...
        """
        print("--->Adding tasks consecutively...")
        pstn = PSTN()

        for i, task in enumerate(self.tasks):
            pstn.add_task(task, i+1)

        n_nodes = 3 * len(self.tasks) + 1
        n_edges = 2 * (5 * len(self.tasks) + len(self.tasks)-1)

        print("N nodes: ", n_nodes)
        print("N edges: ", n_edges)
        print(pstn)

        contingent_constraints = pstn.get_contingent_constraints()
        print(contingent_constraints)

        pstn_json = pstn.to_json()
        print("Json format")
        print(pstn_json)

        # self.assertEqual(n_nodes, stn.number_of_nodes())
        # self.assertEqual(n_edges, stn.number_of_edges())

    # def test_build_stn(self):
    #     print("STN: \n", self.scheduler.temporal_network)
    #     # print("Nodes: ", self.pstn.nodes.data())
    #     # print("Edges: ", self.pstn.edges.data())
    #     # print("Contingent constraints: ", self.pstn.contingent_constraints)
    #
    #     # minimal_stnu = self.pstn.floyd_warshall()
    #     # self.pstn.update_edges(minimal_stnu)
    #     # minimal_network = get_minimal_network(self.pstn)
    #
    #     alpha, guide = self.scheduler.get_dispatch_graph()
    #     print("Schedule: \n", guide)
    #
    #     completion_time = guide.get_completion_time()
    #     makespan = guide.get_makespan()
    #
    #     print("Completion time: ", completion_time)
    #     print("Makespan: ", makespan)
    #
    #     self.assertEqual(completion_time, 69)
    #     self.assertEqual(makespan, 107)


if __name__ == '__main__':
    # unittest.main
    test = TestBuildPSTN()
    test.test_add_tasks_consecutively()
