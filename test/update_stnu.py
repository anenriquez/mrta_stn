from stn.stnu.stnu import STNU
import unittest
from stn.utils.uuid import from_str


class Task(object):

    def __init__(self):
        self.task_id = ''
        self.earliest_start_time = -1
        self.latest_start_time = -1
        self.start_pose_name = ''
        self.finish_pose_name = ''
        self.hard_constraints = True


class UpdateSTNU(unittest.TestCase):

    def setUp(self):
        task_1 = Task()
        task_1.task_id = from_str("0616af00-ec3b-4ecd-ae62-c94a3703594c")
        task_1.r_earliest_navigation_start_time = 0.0
        task_1.r_earliest_start_time = 96.0
        task_1.r_latest_start_time = 102.0
        task_1.start_pose_name = "AMK_TDU-TGR-1_X_14.03_Y_9.55"
        task_1.finish_pose_name = "AMK_TDU-TGR-1_X_15.09_Y_5.69"

        task_2 = Task()
        task_2.task_id = from_str("207cc8da-2f0e-4538-802b-b8f3954df38d")
        task_2.r_earliest_navigation_start_time = 0.0
        task_2.r_earliest_start_time = 71.0
        task_2.r_latest_start_time = 76.0
        task_2.start_pose_name = "AMK_TDU-TGR-1_X_7.15_Y_10.55"
        task_2.finish_pose_name = "AMK_TDU-TGR-1_X_6.67_Y_14.52"

        task_3 = Task()
        task_3.task_id = from_str("0d06fb90-a76d-48b4-b64f-857b7388ab70")
        task_3.r_earliest_navigation_start_time = 0.0
        task_3.r_earliest_start_time = 41.0
        task_3.r_latest_start_time = 47.0
        task_3.start_pose_name = "AMK_TDU-TGR-1_X_9.7_Y_5.6"
        task_3.finish_pose_name = "AMK_TDU-TGR-1_X_5.82_Y_6.57"

        self.tasks = [task_1, task_2, task_3]

    def test_add_tasks_consecutively(self):
        """ Adds tasks in consecutive positions. Example
        position 1, position 2, ...
        """
        print("--->Adding tasks consecutively...")
        stnu = STNU()

        for i, task in enumerate(self.tasks):
            stnu.add_task(task, i+1)

        n_nodes = 3 * len(self.tasks) + 1
        n_edges = 2 * (5 * len(self.tasks) + len(self.tasks)-1)

        print("N nodes: ", n_nodes)
        print("N edges: ", n_edges)
        print(stnu)

        self.assertEqual(n_nodes, stnu.number_of_nodes())
        self.assertEqual(n_edges, stnu.number_of_edges())

    def test_add_task_beggining(self):
        """Adds task at the beginning. Displaces the other tasks
        """
        print("--->Adding task at the beginning...")
        stnu = STNU()
        # Adds the first task in position 1
        stnu.add_task(self.tasks[0], 1)
        print(stnu)

        # Adds a new task in position 1. Displaces existing task at position 1 to position 2
        stnu.add_task(self.tasks[1], 1)
        print(stnu)

        # We added two tasks
        added_tasks = [self.tasks[0], self.tasks[1]]
        n_nodes = 3 * len(added_tasks) + 1
        n_edges = 2 * (5 * len(added_tasks) + len(added_tasks)-1)

        print("N nodes: ", n_nodes)
        print("N edges: ", n_edges)
        print(stnu)

        self.assertEqual(n_nodes, stnu.number_of_nodes())
        self.assertEqual(n_edges, stnu.number_of_edges())

    def test_add_task_middle(self):
        print("--->Adding task in the middle...")
        stnu = STNU()
        # Add task in position 1
        stnu.add_task(self.tasks[0], 1)

        # Adds task in position 2.
        stnu.add_task(self.tasks[1], 2)
        print(stnu)

        # Add a new task in position 2. Displace existing task at position 2 to position 3
        stnu.add_task(self.tasks[2], 2)
        print(stnu)

        n_nodes = 3 * len(self.tasks) + 1
        n_edges = 2 * (5 * len(self.tasks) + len(self.tasks)-1)

        print("N nodes: ", n_nodes)
        print("N edges: ", n_edges)

        self.assertEqual(n_nodes, stnu.number_of_nodes())
        self.assertEqual(n_edges, stnu.number_of_edges())

    def test_remove_task_beginning(self):
        print("--->Removing task at the beginning...")
        stnu = STNU()

        # Add all tasks
        for i, task in enumerate(self.tasks):
            stnu.add_task(task, i+1)

        # Remove task in position 1
        stnu.remove_task(1)

        added_tasks = self.tasks[:-1]
        n_nodes = 3 * len(added_tasks) + 1
        n_edges = 2 * (5 * len(added_tasks) + len(added_tasks)-1)

        print("N nodes: ", n_nodes)
        print("N edges: ", n_edges)
        print(stnu)

        self.assertEqual(n_nodes, stnu.number_of_nodes())
        self.assertEqual(n_edges, stnu.number_of_edges())

    def test_remove_task_middle(self):
        print("--->Removing task in the middle...")
        stnu = STNU()

        # Add all tasks
        for i, task in enumerate(self.tasks):
            stnu.add_task(task, i+1)
        print(stnu)

        # Remove task in position 2
        stnu.remove_task(2)

        added_tasks = self.tasks[:-1]
        n_nodes = 3 * len(added_tasks) + 1
        n_edges = 2 * (5 * len(added_tasks) + len(added_tasks)-1)

        print("N nodes: ", n_nodes)
        print("N edges: ", n_edges)
        print(stnu)

        self.assertEqual(n_nodes, stnu.number_of_nodes())
        self.assertEqual(n_edges, stnu.number_of_edges())

    def test_remove_task_end(self):
        print("--->Removing task at the end...")
        stnu = STNU()

        # Add all tasks
        for i, task in enumerate(self.tasks):
            stnu.add_task(task, i+1)
            print(stnu)

        print(stnu)
        # Remove task in position 3
        stnu.remove_task(3)

        added_tasks = self.tasks[:-1]
        n_nodes = 3 * len(added_tasks) + 1
        n_edges = 2 * (5 * len(added_tasks) + len(added_tasks)-1)

        print("N nodes: ", n_nodes)
        print("N edges: ", n_edges)
        print(stnu)

        self.assertEqual(n_nodes, stnu.number_of_nodes())
        self.assertEqual(n_edges, stnu.number_of_edges())

    def test_add_two_tasks(self):
        print("----Adding two tasks")
        stnu = STNU()
        # Add task in position 1
        stnu.add_task(self.tasks[1], 1)

        # Adds task in position 2.
        stnu.add_task(self.tasks[0], 2)
        print(stnu)

        stnu_json = stnu.to_json()
        print("JSON format ", stnu_json)


if __name__ == '__main__':
    unittest.main()
