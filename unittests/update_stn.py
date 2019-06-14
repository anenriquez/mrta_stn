from scheduler.structs.task import Task
from scheduler.temporal_networks.stn import STN
import os
import yaml
import collections
import unittest

DATASET = "data/three_tasks.yaml"


class UpdateSTN(unittest.TestCase):
    def setUp(self):
        self.tasks = self.get_tasks()

    def get_tasks(self):
        my_dir = os.path.dirname(__file__)
        dataset_path = os.path.join(my_dir, DATASET)

        with open(dataset_path, 'r') as file:
            dataset = yaml.safe_load(file)

        tasks = list()
        ordered_tasks = collections.OrderedDict(sorted(dataset['tasks'].items()))

        for task_id, task in ordered_tasks.items():
            tasks.append(Task.from_dict(task))
        return tasks

    def test_add_tasks_consecutively(self):
        """ Adds tasks in consecutive positions. Example
        position 1, position 2, ...
        """
        print("--->Adding tasks consecutively...")
        stn = STN()

        for i, task in enumerate(self.tasks):
            stn.add_task(task, i+1)

        n_nodes = 3 * len(self.tasks) + 1
        n_edges = 2 * (5 * len(self.tasks) + len(self.tasks)-1)

        print("N nodes: ", n_nodes)
        print("N edges: ", n_edges)
        print(stn)

        self.assertEqual(n_nodes, stn.number_of_nodes())
        self.assertEqual(n_edges, stn.number_of_edges())

    def test_add_task_beggining(self):
        """Adds task at the beginning. Displaces the other tasks
        """
        print("--->Adding task at the beginning...")
        stn = STN()
        # Adds the first task in position 1
        stn.add_task(self.tasks[0], 1)
        print(stn)

        # Adds a new task in position 1. Displaces existing task at position 1 to position 2
        stn.add_task(self.tasks[1], 1)
        print(stn)

        # We added two tasks
        added_tasks = [self.tasks[0], self.tasks[1]]
        n_nodes = 3 * len(added_tasks) + 1
        n_edges = 2 * (5 * len(added_tasks) + len(added_tasks)-1)

        print("N nodes: ", n_nodes)
        print("N edges: ", n_edges)
        print(stn)

        self.assertEqual(n_nodes, stn.number_of_nodes())
        self.assertEqual(n_edges, stn.number_of_edges())

    def test_add_task_middle(self):
        print("--->Adding task in the middle...")
        stn = STN()
        # Add task in position 1
        stn.add_task(self.tasks[0], 1)

        # Adds task in position 2.
        stn.add_task(self.tasks[1], 2)
        print(stn)

        # Add a new task in position 2. Displace existing task at position 2 to position 3
        stn.add_task(self.tasks[2], 2)
        print(stn)

        n_nodes = 3 * len(self.tasks) + 1
        n_edges = 2 * (5 * len(self.tasks) + len(self.tasks)-1)

        print("N nodes: ", n_nodes)
        print("N edges: ", n_edges)

        self.assertEqual(n_nodes, stn.number_of_nodes())
        self.assertEqual(n_edges, stn.number_of_edges())

    def test_remove_task_beginning(self):
        print("--->Removing task at the beginning...")
        stn = STN()

        # Add all tasks
        for i, task in enumerate(self.tasks):
            stn.add_task(task, i+1)

        # Remove task in position 1
        stn.remove_task(1)

        added_tasks = self.tasks[:-1]
        n_nodes = 3 * len(added_tasks) + 1
        n_edges = 2 * (5 * len(added_tasks) + len(added_tasks)-1)

        print("N nodes: ", n_nodes)
        print("N edges: ", n_edges)
        print(stn)

        self.assertEqual(n_nodes, stn.number_of_nodes())
        self.assertEqual(n_edges, stn.number_of_edges())

    def test_remove_task_middle(self):
        print("--->Removing task in the middle...")
        stn = STN()

        # Add all tasks
        for i, task in enumerate(self.tasks):
            stn.add_task(task, i+1)
        print(stn)

        # Remove task in position 2
        stn.remove_task(2)

        added_tasks = self.tasks[:-1]
        n_nodes = 3 * len(added_tasks) + 1
        n_edges = 2 * (5 * len(added_tasks) + len(added_tasks)-1)

        print("N nodes: ", n_nodes)
        print("N edges: ", n_edges)
        print(stn)

        self.assertEqual(n_nodes, stn.number_of_nodes())
        self.assertEqual(n_edges, stn.number_of_edges())

    def test_remove_task_end(self):
        print("--->Removing task at the end...")
        stn = STN()

        # Add all tasks
        for i, task in enumerate(self.tasks):
            stn.add_task(task, i+1)
            print(stn)

        print(stn)
        # Remove task in position 3
        stn.remove_task(3)

        added_tasks = self.tasks[:-1]
        n_nodes = 3 * len(added_tasks) + 1
        n_edges = 2 * (5 * len(added_tasks) + len(added_tasks)-1)

        print("N nodes: ", n_nodes)
        print("N edges: ", n_edges)
        print(stn)

        # data1 = json_graph.node_link_data(stn)
        # MyEncoder().encode(data1)
        # print(data1)
        # print("------------")
        # s1 = json.dumps(data1, cls=MyEncoder)
        # print(s1)
        # stn1 = json.loads(data1)
        # print(s1)
        # print(json_graph.node_link_graph(data1, directed=True))
        # print("----", H)

        self.assertEqual(n_nodes, stn.number_of_nodes())
        self.assertEqual(n_edges, stn.number_of_edges())

    def test_add_two_tasks(self):
        print("----Adding two tasks")
        stn = STN()
        # Add task in position 1
        stn.add_task(self.tasks[1], 1)

        # Adds task in position 2.
        stn.add_task(self.tasks[0], 2)
        print(stn)

        stn_json = stn.to_json()
        print("JSON format")
        print(stn_json)


if __name__ == '__main__':
    unittest.main()
