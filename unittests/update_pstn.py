import unittest
import os
import yaml
import collections
from scheduler.structs.task import Task
from scheduler.temporal_networks.pstn import PSTN

DATASET = "data/three_tasks.yaml"


class TestBuildPSTN(unittest.TestCase):
    def setUp(self):
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

        # contingent_constraints = ppstn.get_contingent_constraints()
        # print(contingent_constraints)
        #
        # ppstn_json = ppstn.to_json()
        # print("Json format")
        # print(ppstn_json)

        self.assertEqual(n_nodes, pstn.number_of_nodes())
        self.assertEqual(n_edges, pstn.number_of_edges())

    def test_add_task_beggining(self):
        """Adds task at the beginning. Displaces the other tasks
        """
        print("--->Adding task at the beginning...")
        pstn = PSTN()
        # Adds the first task in position 1
        pstn.add_task(self.tasks[0], 1)
        print(pstn)

        # Adds a new task in position 1. Displaces existing task at position 1 to position 2
        pstn.add_task(self.tasks[1], 1)
        print(pstn)

        # We added two tasks
        added_tasks = [self.tasks[0], self.tasks[1]]
        n_nodes = 3 * len(added_tasks) + 1
        n_edges = 2 * (5 * len(added_tasks) + len(added_tasks)-1)

        print("N nodes: ", n_nodes)
        print("N edges: ", n_edges)
        print(pstn)

        self.assertEqual(n_nodes, pstn.number_of_nodes())
        self.assertEqual(n_edges, pstn.number_of_edges())

    def test_add_task_middle(self):
        print("--->Adding task in the middle...")
        pstn = PSTN()
        # Add task in position 1
        pstn.add_task(self.tasks[0], 1)

        # Adds task in position 2.
        pstn.add_task(self.tasks[1], 2)
        print(pstn)

        # Add a new task in position 2. Displace existing task at position 2 to position 3
        pstn.add_task(self.tasks[2], 2)
        print(pstn)

        n_nodes = 3 * len(self.tasks) + 1
        n_edges = 2 * (5 * len(self.tasks) + len(self.tasks)-1)

        print("N nodes: ", n_nodes)
        print("N edges: ", n_edges)

        self.assertEqual(n_nodes, pstn.number_of_nodes())
        self.assertEqual(n_edges, pstn.number_of_edges())

    def test_remove_task_beginning(self):
        print("--->Removing task at the beginning...")
        pstn = PSTN()

        # Add all tasks
        for i, task in enumerate(self.tasks):
            pstn.add_task(task, i+1)

        # Remove task in position 1
        pstn.remove_task(1)

        added_tasks = self.tasks[:-1]
        n_nodes = 3 * len(added_tasks) + 1
        n_edges = 2 * (5 * len(added_tasks) + len(added_tasks)-1)

        print("N nodes: ", n_nodes)
        print("N edges: ", n_edges)
        print(pstn)

        self.assertEqual(n_nodes, pstn.number_of_nodes())
        self.assertEqual(n_edges, pstn.number_of_edges())

    def test_remove_task_middle(self):
        print("--->Removing task in the middle...")
        pstn = PSTN()

        # Add all tasks
        for i, task in enumerate(self.tasks):
            pstn.add_task(task, i+1)
        print(pstn)

        # Remove task in position 2
        pstn.remove_task(2)

        added_tasks = self.tasks[:-1]
        n_nodes = 3 * len(added_tasks) + 1
        n_edges = 2 * (5 * len(added_tasks) + len(added_tasks)-1)

        print("N nodes: ", n_nodes)
        print("N edges: ", n_edges)
        print(pstn)

        self.assertEqual(n_nodes, pstn.number_of_nodes())
        self.assertEqual(n_edges, pstn.number_of_edges())

    def test_remove_task_end(self):
        print("--->Removing task at the end...")
        pstn = PSTN()

        # Add all tasks
        for i, task in enumerate(self.tasks):
            pstn.add_task(task, i+1)
            print(pstn)

        print(pstn)
        # Remove task in position 3
        pstn.remove_task(3)

        added_tasks = self.tasks[:-1]
        n_nodes = 3 * len(added_tasks) + 1
        n_edges = 2 * (5 * len(added_tasks) + len(added_tasks)-1)

        print("N nodes: ", n_nodes)
        print("N edges: ", n_edges)
        print(pstn)

        # data1 = json_graph.node_link_data(pstn)
        # MyEncoder().encode(data1)
        # print(data1)
        # print("------------")
        # s1 = json.dumps(data1, cls=MyEncoder)
        # print(s1)
        # pstn1 = json.loads(data1)
        # print(s1)
        # print(json_graph.node_link_graph(data1, directed=True))
        # print("----", H)

        self.assertEqual(n_nodes, pstn.number_of_nodes())
        self.assertEqual(n_edges, pstn.number_of_edges())

    # def test_add_two_tasks(self):
    #     print("----Adding two tasks")
    #     pstn = PSTN()
    #     # Add task in position 1
    #     pstn.add_task(self.tasks[1], 1)
    #
    #     # Adds task in position 2.
    #     pstn.add_task(self.tasks[0], 2)
    #     print(pstn)
    #
    #     # pstn_json = pstn.to_json()
    #     # print("JSON format")
    #     # print(pstn_json)


if __name__ == '__main__':
    unittest.main()
    # test = TestBuildPpstn()
    # test.test_add_tasks_consecutively()
    # test.test_add_task_beggining()
    # test.test_add_task_middle()
    # test.test_remove_task_beginning()
    # test.test_remove_task_middle()
    # test.test_remove_task_end()
