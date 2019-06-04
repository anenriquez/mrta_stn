import unittest
import os
import yaml
import collections
from temporal.networks.stn import STN
from temporal.structs.task import Task

DATASET = "data/two_tasks.yaml"


class TestBuildSTN(unittest.TestCase):
    def setUp(self):
        self.tasks = list()
        self.scheduled_tasks = list()
        self.stn = STN()

        my_dir = os.path.dirname(__file__)
        dataset_path = os.path.join(my_dir, DATASET)

        with open(dataset_path, 'r') as file:
            dataset = yaml.safe_load(file)

        ordered_tasks = collections.OrderedDict(sorted(dataset['tasks'].items(), reverse=True))

        for task_id, task in ordered_tasks.items():
            self.tasks.append(Task.from_dict(task))

    def test_build_stn(self):
        self.stn.build_stn(self.tasks)
        print(self.stn)
        print(self.stn.nodes.data())
        print(self.stn.edges.data())

        minimal_stnu = self.stn.floyd_warshall()


        self.stn.update_edges(minimal_stnu)
        # self.stn.update_time_schedule(minimal_stnu)

        print(self.stn)

        completion_time = self.stn.get_completion_time()
        makespan = self.stn.get_makespan()

        print("Completion time: ", completion_time)
        print("Makespan: ", makespan)




        # for task in self.tasks:
        #     self.insert_task(task)

    # def insert_task(self, task):
    #     n_scheduled_tasks = len(self.scheduled_tasks)
    #
    #     for i in range(0, n_scheduled_tasks + 1):
    #         self.scheduled_tasks.insert(i, task)
    #         self.stn.build_stn(self.scheduled_tasks)
    #
    #         print(self.stn)
    #         print(self.stn.nodes.data())
    #         print(self.stn.edges.data())
    #
    #         self.scheduled_tasks.pop(i)


if __name__ == '__main__':
    unittest.main()
