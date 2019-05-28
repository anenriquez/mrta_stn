''' Taken from https://github.com/ropod-project/ropod_common
'''

from src.structs.area import Area, SubArea

class Action(object):
    def __init__(self):
        self.id = ''
        self.type = ''

        # fields for goto actions
        self.areas = list()
        self.subareas = list()

        # fields for elevator request actions
        self.start_floor = -1
        self.goal_floor = -1

        # fields for entering/exiting elevators
        self.level = -1
        self.elevator_id = -1

        # pending, in progress, etc.
        self.execution_status = ''
        self.eta = -1.

    def to_dict(self):
        action_dict = dict()

        action_dict['id'] = self.id
        action_dict["type"] = self.type
        action_dict["start_floor"] = self.start_floor
        action_dict["goal_floor"] = self.goal_floor
        action_dict["level"] = self.level
        action_dict["elevator_id"] = self.elevator_id
        action_dict["execution_status"] = self.execution_status
        action_dict["eta"] = self.eta

        action_dict['areas'] = list()
        for area in self.areas:
            area_dict = area.to_dict()
            action_dict['areas'].append(area_dict)

        action_dict['subareas'] = list()
        for subarea in self.subareas:
            subarea_dict = subarea.to_dict()
            action_dict['subareas'].append(subarea_dict)

        return action_dict

    @staticmethod
    def from_dict(action_dict):
        action = Action()

        action.id = action_dict['id']
        action.type = action_dict['type']

        action.start_floor = action_dict['start_floor']
        action.goal_floor = action_dict['goal_floor']

        action.level = action_dict['level']
        action.elevator_id = action_dict['elevator_id']

        action.execution_status = action_dict['execution_status']
        action.eta = action_dict['eta']

        for area_dict in action_dict['areas']:
            area = Area.from_dict(area_dict)
            action.areas.append(area)

        for subarea_dict in action_dict['subareas']:
            subarea = SubArea.from_dict(subarea_dict)
            action.subareas.append(subarea)

        return action
