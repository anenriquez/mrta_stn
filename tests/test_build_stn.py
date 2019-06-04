import unittest
import os
import yaml
import collections
from temporal.networks.stn import STN
from temporal.structs.task import Task
from temporal.networks.stn import Scheduler


DATASET = "data/two_tasks.yaml"


class TestBuildSTN(unittest.TestCase):
    def setUp(self):
        self.tasks = list()
        self.scheduled_tasks = list()
        self.stn = STN()
        self.scheduler = Scheduler()

        my_dir = os.path.dirname(__file__)
        dataset_path = os.path.join(my_dir, DATASET)

        with open(dataset_path, 'r') as file:
            dataset = yaml.safe_load(file)

        ordered_tasks = collections.OrderedDict(sorted(dataset['tasks'].items(), reverse=True))

        for task_id, task in ordered_tasks.items():
            self.tasks.append(Task.from_dict(task))

    def test_build_stn(self):
        self.stn.build_temporal_network(self.tasks)
        print("STN: \n", self.stn)
        print(self.stn.nodes.data())
        print(self.stn.edges.data())

        minimal_stnu = self.stn.floyd_warshall()
        self.stn.update_edges(minimal_stnu)

        alpha, schedule = self.scheduler.get_schedule(self.stn, "earliest")
        print("Schedule: \n", schedule)

        completion_time = self.scheduler.get_completion_time(schedule)
        makespan = self.scheduler.get_makespan(schedule)

        print("Completion time: ", completion_time)
        print("Makespan: ", makespan)

        self.assertEqual(completion_time, 100)
        self.assertEqual(makespan, 100)


if __name__ == '__main__':
    unittest.main()