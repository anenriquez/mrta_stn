from scheduler.temporal_networks.stn import STN
import unittest
import logging
import sys
from datasets.dataset_loader import load_dataset

logger = logging.getLogger()
logger.level = logging.INFO
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class UpdateSTN(unittest.TestCase):
    logger = logging.getLogger('scheduler.test')

    def setUp(self):
        self.tasks = load_dataset('three_tasks.csv')

    def test_add_tasks_consecutively(self):
        """ Adds tasks in consecutive positions. Example
        position 1, position 2, ...
        """
        self.logger.info("--->Adding tasks consecutively...")
        stn = STN()

        for i, task in enumerate(self.tasks):
            stn.add_task(task, i+1)

        n_nodes = 3 * len(self.tasks) + 1
        n_edges = 2 * (5 * len(self.tasks) + len(self.tasks)-1)

        self.logger.info("N nodes: %s ", n_nodes)
        self.logger.info("N edges: %s ", n_edges)
        self.logger.info(stn)

        self.assertEqual(n_nodes, stn.number_of_nodes())
        self.assertEqual(n_edges, stn.number_of_edges())

    def test_add_task_beggining(self):
        """Adds task at the beginning. Displaces the other tasks
        """
        self.logger.info("--->Adding task at the beginning...")
        stn = STN()
        # Adds the first task in position 1
        stn.add_task(self.tasks[0], 1)
        self.logger.info("%s", stn)

        # Adds a new task in position 1. Displaces existing task at position 1 to position 2
        stn.add_task(self.tasks[1], 1)
        self.logger.info("%s", stn)

        # We added two tasks
        added_tasks = [self.tasks[0], self.tasks[1]]
        n_nodes = 3 * len(added_tasks) + 1
        n_edges = 2 * (5 * len(added_tasks) + len(added_tasks)-1)

        self.logger.info("N nodes: %s", n_nodes)
        self.logger.info("N edges: %s", n_edges)
        self.logger.info("%s", stn)

        self.assertEqual(n_nodes, stn.number_of_nodes())
        self.assertEqual(n_edges, stn.number_of_edges())

    def test_add_task_middle(self):
        self.logger.info("--->Adding task in the middle...")
        stn = STN()
        # Add task in position 1
        stn.add_task(self.tasks[0], 1)

        # Adds task in position 2.
        stn.add_task(self.tasks[1], 2)
        self.logger.info("%s", stn)

        # Add a new task in position 2. Displace existing task at position 2 to position 3
        stn.add_task(self.tasks[2], 2)
        self.logger.info("%s", stn)

        n_nodes = 3 * len(self.tasks) + 1
        n_edges = 2 * (5 * len(self.tasks) + len(self.tasks)-1)

        self.logger.info("N nodes: %s ", n_nodes)
        self.logger.info("N edges: %s", n_edges)

        self.assertEqual(n_nodes, stn.number_of_nodes())
        self.assertEqual(n_edges, stn.number_of_edges())

    def test_remove_task_beginning(self):
        self.logger.info("--->Removing task at the beginning...")
        stn = STN()

        # Add all tasks
        for i, task in enumerate(self.tasks):
            stn.add_task(task, i+1)

        # Remove task in position 1
        stn.remove_task(1)

        added_tasks = self.tasks[:-1]
        n_nodes = 3 * len(added_tasks) + 1
        n_edges = 2 * (5 * len(added_tasks) + len(added_tasks)-1)

        self.logger.info("N nodes: %s ", n_nodes)
        self.logger.info("N edges: %s ", n_edges)
        self.logger.info(stn)

        self.assertEqual(n_nodes, stn.number_of_nodes())
        self.assertEqual(n_edges, stn.number_of_edges())

    def test_remove_task_middle(self):
        self.logger.info("--->Removing task in the middle...")
        stn = STN()

        # Add all tasks
        for i, task in enumerate(self.tasks):
            stn.add_task(task, i+1)
        self.logger.info(stn)

        # Remove task in position 2
        stn.remove_task(2)

        added_tasks = self.tasks[:-1]
        n_nodes = 3 * len(added_tasks) + 1
        n_edges = 2 * (5 * len(added_tasks) + len(added_tasks)-1)

        self.logger.info("N nodes: %s ", n_nodes)
        self.logger.info("N edges: %s", n_edges)
        self.logger.info(stn)

        self.assertEqual(n_nodes, stn.number_of_nodes())
        self.assertEqual(n_edges, stn.number_of_edges())

    def test_remove_task_end(self):
        self.logger.info("--->Removing task at the end...")
        stn = STN()

        # Add all tasks
        for i, task in enumerate(self.tasks):
            stn.add_task(task, i+1)
            self.logger.info(stn)

        self.logger.info("%s", stn)
        # Remove task in position 3
        stn.remove_task(3)

        added_tasks = self.tasks[:-1]
        n_nodes = 3 * len(added_tasks) + 1
        n_edges = 2 * (5 * len(added_tasks) + len(added_tasks)-1)

        self.logger.info("N nodes: %s ", n_nodes)
        self.logger.info("N edges: %s", n_edges)
        self.logger.info(stn)

        self.assertEqual(n_nodes, stn.number_of_nodes())
        self.assertEqual(n_edges, stn.number_of_edges())

    def test_add_two_tasks(self):
        self.logger.info("----Adding two tasks")
        stn = STN()
        # Add task in position 1
        stn.add_task(self.tasks[1], 1)

        # Adds task in position 2.
        stn.add_task(self.tasks[0], 2)
        self.logger.info("%s", stn)

        stn_json = stn.to_json()
        self.logger.info("JSON format", stn_json)


if __name__ == '__main__':
    unittest.main()
