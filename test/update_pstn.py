import os
from stn.pstn.pstn import PSTN
import unittest
from stn.utils.uuid import from_str
from stn.utils.utils import load_yaml, create_task


class UpdatePSTN(unittest.TestCase):

    def setUp(self):
        code_dir = os.path.abspath(os.path.dirname(__file__))
        tasks_dict = load_yaml(code_dir + "/data/tasks.yaml")
        self.tasks = list()
        for task_dict in tasks_dict.values():
            task = create_task(PSTN(), task_dict)
            print(task)
            self.tasks.append(task)

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

        self.assertEqual(n_nodes, pstn.number_of_nodes())
        self.assertEqual(n_edges, pstn.number_of_edges())


if __name__ == '__main__':
    unittest.main()
