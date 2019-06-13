from scheduler.structs.task import Task
from scheduler.temporal_networks.stn import STN
import os
import yaml
import collections
import unittest

DATASET = "data/three_tasks.yaml"

class UpdateSTN(object):
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
        position 1, position 2, ..."""
        print("Adding tasks consecutively...")
        stn = STN()
        print(stn)

        for i, task in enumerate(self.tasks):
            stn.add_task(task, i+1)

        n_nodes = 3 * len(self.tasks) + 1
        n_edges = 2 * (5 * len(self.tasks) + len(self.tasks)-1)
        # if len(self.tasks) > 1:
        #     n_edges = 2 * (5 * len(self.tasks) + len(self.tasks)-1)
        # else:
        #     n_edges = 2 * (5 * len(self.tasks))

        print("N nodes: ", n_nodes)
        print("N edges: ", n_edges)

        # self.assertEqual(n_nodes, stn.number_of_nodes())
        # self.assertEqual(n_edges, stn.number_of_edges())

    def test_add_task_beggining(self):
        "Adds task at the beginning. Displaces the other tasks"
        print("Adding task at the beginning...")
        stn = STN()
        print(stn)
        # Adds the first task in position 1
        stn.add_task(self.tasks[0], 1)

        # Adds a new task in position 1. Displaces existing task at position 1 to position 2
        stn.add_task(self.tasks[1], 1)

        n_nodes = 3 * len(self.tasks) + 1
        n_edges = 2 * (5 * len(self.tasks) + len(self.tasks)-1)
        # if len(self.tasks) > 1:
        #     n_edges = 2 * (5 * len(self.tasks) + len(self.tasks)-1)
        # else:
        #     n_edges = 2 * (5 * len(self.tasks))

        print("N nodes: ", n_nodes)
        print("N edges: ", n_edges)

        # self.assertEqual(n_nodes, stn.number_of_nodes())
        # self.assertEqual(n_edges, stn.number_of_edges())

    def test_add_task_middle(self):
        print("Adding task in the middle...")
        stn = STN()
        print(stn)
        # Add task in position 1
        stn.add_task(self.tasks[0], 1)

        # Adds task in position 2.
        stn.add_task(self.tasks[1], 2)

        # Add a new task in position 2. Displace existing task at position 2 to position 3
        stn.add_task(self.tasks[2], 2)

        n_nodes = 3 * len(self.tasks) + 1
        n_edges = 2 * (5 * len(self.tasks) + len(self.tasks)-1)
        # if len(self.tasks) > 1:
        #     n_edges = 2 * (5 * len(self.tasks) + len(self.tasks)-1)
        # else:
        #     n_edges = 2 * (5 * len(self.tasks))

        print("N nodes: ", n_nodes)
        print("N edges: ", n_edges)

        # self.assertEqual(n_nodes, stn.number_of_nodes())
        # self.assertEqual(n_edges, stn.number_of_edges())

    def test_remove_task(self):
        print("Adding tasks consecutively...")
        stn = STN()
        print(stn)

        for i, task in enumerate(self.tasks):
            stn.add_task(task, i+1)

        n_nodes = 3 * len(self.tasks) + 1
        n_edges = 2 * (5 * len(self.tasks) + len(self.tasks)-1)

        print("N nodes: ", n_nodes)
        print("N edges: ", n_edges)

        stn.remove_task(1)


if __name__ == '__main__':
    # unittest.main()
    test = UpdateSTN()
    # test.test_add_tasks_consecutively()
    test.test_add_task_beggining()
    # test.test_add_task_middle()
    # test.test_remove_task()

    #add_tasks_consecutively()
    # tasks = get_tasks()
    # stn = STN()
    # print(stn)
    #
    # for i, task in enumerate(tasks):
    #     stn.add_task(task, i+1)

    # for u, outer_d in stn.nodes(data=True):
    #     print("u: ", u)
    #     print("outer_d: ", outer_d)
