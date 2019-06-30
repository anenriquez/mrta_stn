from scheduler.temporal_networks.stnu import STNU
import unittest
import logging
import sys
from datasets.dataset_loader import load_dataset


logger = logging.getLogger()
logger.level = logging.INFO
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class UpdateSTNU(unittest.TestCase):
    logger = logging.getLogger('scheduler.test')

    def setUp(self):
        self.tasks = load_dataset('three_tasks.csv')

    def test_add_tasks_consecutively(self):
        """ Adds tasks in consecutive positions. Example
        position 1, position 2, ...
        """
        self.logger.info("--->Adding tasks consecutively...")
        stnu = STNU()

        for i, task in enumerate(self.tasks):
            stnu.add_task(task, i+1)

        n_nodes = 3 * len(self.tasks) + 1
        n_edges = 2 * (5 * len(self.tasks) + len(self.tasks)-1)

        self.logger.info("N nodes: %s ", n_nodes)
        self.logger.info("N edges: %s ", n_edges)
        self.logger.info(stnu)

        self.assertEqual(n_nodes, stnu.number_of_nodes())
        self.assertEqual(n_edges, stnu.number_of_edges())

    def test_add_task_beggining(self):
        """Adds task at the beginning. Displaces the other tasks
        """
        self.logger.info("--->Adding task at the beginning...")
        stnu = STNU()
        # Adds the first task in position 1
        stnu.add_task(self.tasks[0], 1)
        self.logger.info("%s", stnu)

        # Adds a new task in position 1. Displaces existing task at position 1 to position 2
        stnu.add_task(self.tasks[1], 1)
        self.logger.info("%s", stnu)

        # We added two tasks
        added_tasks = [self.tasks[0], self.tasks[1]]
        n_nodes = 3 * len(added_tasks) + 1
        n_edges = 2 * (5 * len(added_tasks) + len(added_tasks)-1)

        self.logger.info("N nodes: %s ", n_nodes)
        self.logger.info("N edges: %s", n_edges)
        self.logger.info(stnu)

        self.assertEqual(n_nodes, stnu.number_of_nodes())
        self.assertEqual(n_edges, stnu.number_of_edges())

    def test_add_task_middle(self):
        self.logger.info("--->Adding task in the middle...")
        stnu = STNU()
        # Add task in position 1
        stnu.add_task(self.tasks[0], 1)

        # Adds task in position 2.
        stnu.add_task(self.tasks[1], 2)
        self.logger.info("%s", stnu)

        # Add a new task in position 2. Displace existing task at position 2 to position 3
        stnu.add_task(self.tasks[2], 2)
        self.logger.info("%s", stnu)

        n_nodes = 3 * len(self.tasks) + 1
        n_edges = 2 * (5 * len(self.tasks) + len(self.tasks)-1)

        self.logger.info("N nodes: %s", n_nodes)
        self.logger.info("N edges: %s", n_edges)

        self.assertEqual(n_nodes, stnu.number_of_nodes())
        self.assertEqual(n_edges, stnu.number_of_edges())

    def test_remove_task_beginning(self):
        self.logger.info("--->Removing task at the beginning...")
        stnu = STNU()

        # Add all tasks
        for i, task in enumerate(self.tasks):
            stnu.add_task(task, i+1)

        # Remove task in position 1
        stnu.remove_task(1)

        added_tasks = self.tasks[:-1]
        n_nodes = 3 * len(added_tasks) + 1
        n_edges = 2 * (5 * len(added_tasks) + len(added_tasks)-1)

        self.logger.info("N nodes: %s", n_nodes)
        self.logger.info("N edges: %s", n_edges)
        self.logger.info(stnu)

        self.assertEqual(n_nodes, stnu.number_of_nodes())
        self.assertEqual(n_edges, stnu.number_of_edges())

    def test_remove_task_middle(self):
        self.logger.info("--->Removing task in the middle...")
        stnu = STNU()

        # Add all tasks
        for i, task in enumerate(self.tasks):
            stnu.add_task(task, i+1)
        self.logger.info(stnu)

        # Remove task in position 2
        stnu.remove_task(2)

        added_tasks = self.tasks[:-1]
        n_nodes = 3 * len(added_tasks) + 1
        n_edges = 2 * (5 * len(added_tasks) + len(added_tasks)-1)

        self.logger.info("N nodes: %s", n_nodes)
        self.logger.info("N edges: %s", n_edges)
        self.logger.info(stnu)

        self.assertEqual(n_nodes, stnu.number_of_nodes())
        self.assertEqual(n_edges, stnu.number_of_edges())

    def test_remove_task_end(self):
        self.logger.info("--->Removing task at the end...")
        stnu = STNU()

        # Add all tasks
        for i, task in enumerate(self.tasks):
            stnu.add_task(task, i+1)
            self.logger.info("%s", stnu)

        self.logger.info("%s", stnu)
        # Remove task in position 3
        stnu.remove_task(3)

        added_tasks = self.tasks[:-1]
        n_nodes = 3 * len(added_tasks) + 1
        n_edges = 2 * (5 * len(added_tasks) + len(added_tasks)-1)

        self.logger.info("N nodes: %s ", n_nodes)
        self.logger.info("N edges: %s", n_edges)
        self.logger.info("%s", stnu)

        self.assertEqual(n_nodes, stnu.number_of_nodes())
        self.assertEqual(n_edges, stnu.number_of_edges())

    def test_add_two_tasks(self):
        self.logger.info("----Adding two tasks")
        stnu = STNU()
        # Add task in position 1
        stnu.add_task(self.tasks[1], 1)

        # Adds task in position 2.
        stnu.add_task(self.tasks[0], 2)
        self.logger.info("%s", stnu)

        stnu_json = stnu.to_json()
        self.logger.info("JSON format % s", stnu_json)


if __name__ == '__main__':
    unittest.main()
