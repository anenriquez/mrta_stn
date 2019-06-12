''' Taken from https://github.com/ropod-project/ropod_common
'''

from scheduler.utils.uuid import generate_uuid
from scheduler.structs.area import Area
from scheduler.structs.action import Action
from scheduler.structs.status import TaskStatus


class Task(object):
    EMERGENCY = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3

    def __init__(self, id='', robot_actions=dict(), loadType='', loadId='', team_robot_ids=list(),
                 earliest_start_time=-1, latest_start_time=-1,
                 earliest_pickup_time=-1, latest_pickup_time=-1,
                 estimated_duration=-1, start_time=-1, finish_time=-1,
                 pickup_pose=Area(), delivery_pose=Area(),
                 status=TaskStatus(), priority=NORMAL):

        if not id:
            self.id = generate_uuid()
        else:
            self.id = id
        self.robot_actions = robot_actions
        self.loadType = loadType
        self.loadId = loadId
        self.team_robot_ids = team_robot_ids
        self.earliest_start_time = earliest_start_time
        self.latest_start_time = latest_start_time
        self.earliest_pickup_time = earliest_pickup_time
        self.latest_pickup_time = latest_pickup_time
        self.earliest_delivery_time = earliest_pickup_time + estimated_duration
        self.latest_delivery_time = latest_pickup_time + estimated_duration
        self.start_time = start_time
        self.finish_time = finish_time
        self.estimated_duration = estimated_duration

        if isinstance(pickup_pose, Area):
            self.pickup_pose = pickup_pose
        else:
            raise Exception('pickup_pose must be an object of type Area')

        if isinstance(delivery_pose, Area):
            self.delivery_pose = delivery_pose
        else:
            raise Exception('delivery_pose must be an object of type Area')

        if isinstance(status, TaskStatus):
            self.status = status
        else:
            raise Exception("status must be an object of TaskStatus type")

        if priority in (self.EMERGENCY, self.NORMAL, self.HIGH, self.LOW):
            self.priority = priority
        else:
            raise Exception("Priority must have one of the following values:\n"
                            "0) Urgent\n"
                            "1) High\n"
                            "2) Normal\n"
                            "3) Low")

    def to_dict(self):
        task_dict = dict()
        task_dict['id'] = self.id
        task_dict['loadType'] = self.loadType
        task_dict['loadId'] = self.loadId
        task_dict['team_robot_ids'] = self.team_robot_ids
        task_dict['earliest_start_time'] = self.earliest_start_time
        task_dict['latest_start_time'] = self.latest_start_time
        task_dict['earliest_pickup_time'] = self.earliest_pickup_time
        task_dict['latest_pickup_time'] = self.latest_pickup_time
        task_dict['earliest_delivery_time'] = self.earliest_delivery_time
        task_dict['latest_delivery_time'] = self.latest_delivery_time
        task_dict['start_time'] = self.start_time
        task_dict['finish_time'] = self.finish_time
        task_dict['estimated_duration'] = self.estimated_duration
        task_dict['pickup_pose'] = self.pickup_pose.to_dict()
        task_dict['delivery_pose'] = self.delivery_pose.to_dict()
        task_dict['priority'] = self.priority
        task_dict['status'] = self.status.to_dict()
        task_dict['robot_actions'] = dict()
        for robot_id, actions in self.robot_actions.items():
            task_dict['robot_actions'][robot_id] = list()
            for action in actions:
                action_dict = Action.to_dict(action)
                task_dict['robot_actions'][robot_id].append(action_dict)
        return task_dict

    @staticmethod
    def from_dict(task_dict):
        task = Task()
        task.id = task_dict['id']
        task.loadType = task_dict['loadType']
        task.loadId = task_dict['loadId']
        task.team_robot_ids = task_dict['team_robot_ids']
        task.earliest_start_time = task_dict['earliest_start_time']
        task.latest_start_time = task_dict['latest_start_time']
        task.earliest_pickup_time = task_dict['earliest_pickup_time']
        task.latest_pickup_time = task_dict['latest_pickup_time']
        task.earliest_delivery_time = task_dict['earliest_delivery_time']
        task.latest_delivery_time = task_dict['latest_delivery_time']
        task.start_time = task_dict['start_time']
        task.finish_time = task_dict['finish_time']
        task.estimated_duration = task_dict['estimated_duration']
        task.pickup_pose = Area.from_dict(task_dict['pickup_pose'])
        task.delivery_pose = Area.from_dict(task_dict['delivery_pose'])
        task.priority = task_dict['priority']
        task.status = TaskStatus.from_dict(task_dict['status'])
        for robot_id, actions in task_dict['robot_actions'].items():
            task.robot_actions[robot_id] = list()
            for action_dict in actions:
                action = Action.from_dict(action_dict)
                task.robot_actions[robot_id].append(action)
        return task

    @staticmethod
    def from_request(request):
        task = Task()
        task.load_type = request.load_type
        task.load_id = request.load_id
        task.earliest_pickup_time = request.earliest_start_time
        task.latest_pickup_time = request.latest_start_time
        task.pickup_pose = request.pickup_pose
        task.delivery_pose = request.delivery_pose
        task.priority = request.priority
        task.status.status = "unallocated" # TODO This should be standardized
        task.status.task_id = task.id
        task.team_robot_ids = None

        return task

    ''' Updates the earliest and latest finish time of a task based on its estimated duration
    @param estimated duration: seconds (float)
    '''
    def update_earliest_and_latest_delivery_time(self, estimated_duration):
        self.earliest_delivery_time = self.earliest_pickup_time + estimated_duration
        self.latest_delivery_time = self.latest_pickup_time + estimated_duration

    '''@param time: seconds (float)
    '''
    def postpone_task(self, time):
        self.earliest_pickup_time += time
        self.latest_pickup_time += time
        self.earliest_delivery_time = self.earliest_pickup_time + self.estimated_duration
        self.latest_delivery_time = self.latest_pickup_time + self.estimated_duration

    ''' Updates the estimated duration and the earliest and latest delivery times
    @param estimated duration: seconds (float)
    '''
    def update_task_estimated_duration(self, estimated_duration):
        self.estimated_duration = estimated_duration
        self.update_earliest_and_latest_delivery_time(estimated_duration)
