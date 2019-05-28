''' Taken from https://github.com/ropod-project/ropod_common
'''

from src.structs.area import Area

SUCCESS = 0
FAILED = 1
TERMINATED = 2
ONGOING = 3
UNALLOCATED = 10
ALLOCATED = 15
COMPLETED = 20


class RobotStatus(object):
    def __init__(self):
        self.robot_id = ''
        self.current_location = Area()
        self.current_operation = ''
        self.status = ''
        self.available = False
        self.battery_status = -1.

    def to_dict(self):
        status_dict = dict()
        status_dict['robotId'] = self.robot_id
        status_dict['currentOperation'] = self.current_operation
        status_dict['currentLocation'] = self.current_location.to_dict()
        status_dict['status'] = self.status
        status_dict['available'] = self.available
        status_dict['batteryStatus'] = self.battery_status

        return status_dict

    @staticmethod
    def from_dict(status_dict):
        status = RobotStatus()
        status.robot_id = status_dict['robotId']
        status.current_operation = status_dict['currentOperation']
        status.current_location = Area.from_dict(status_dict['currentLocation'])
        status.status = status_dict['status']
        status.available = status_dict['available']
        status.battery_status = status_dict['batteryStatus']

        return status


class TaskStatus(object):
    UNALLOCATED = 1
    ALLOCATED = 2
    ONGOING = 3
    COMPLETED = 4
    TERMINATED = 5

    def __init__(self):
        self.task_id = ''
        self.status = ''
        self.current_robot_action = dict()
        self.completed_robot_actions = dict()
        self.estimated_task_duration = -1.

    def to_dict(self):
        task_dict = dict()
        task_dict['task_id'] = self.task_id
        task_dict['status'] = self.status
        task_dict['estimated_task_duration'] = self.estimated_task_duration
        task_dict['current_robot_actions'] = self.current_robot_action
        task_dict['completed_robot_actions'] = self.completed_robot_actions
        return task_dict

    @staticmethod
    def from_dict(status_dict):
        status = TaskStatus()
        status.task_id = status_dict['task_id']
        status.status = status_dict['status']
        status.estimated_task_duration = status_dict['estimated_task_duration']
        status.current_robot_action = status_dict['current_robot_actions']
        status.completed_robot_actions = status_dict['completed_robot_actions']
        return status
