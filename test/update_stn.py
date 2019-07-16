from stn.stn import STN
import unittest
import os
import json
from allocation.task import Task

code_dir = os.path.abspath(os.path.dirname(__file__))
TASKS = code_dir + "/data/three_tasks.json"


class UpdateSTN(unittest.TestCase):

    def setUp(self):
        with open(TASKS) as json_file:
            tasks_dict = json.load(json_file)

        self.tasks = list()
        for task_dict in tasks_dict['tasks']:
            task = Task.from_dict(task_dict)
            self.tasks.append(task)

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

        list_tasks = list()
        for task in self.tasks:
            list_tasks.append(task.to_dict())

        print("list of tasks")
        print(list_tasks)

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
        print("JSON format", stn_json)


if __name__ == '__main__':
    unittest.main()

