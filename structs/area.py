''' Taken from https://github.com/ropod-project/ropod_common
'''

class SubArea(object):
    def __init__(self):
        self.id = ''
        self.name = ''
        self.type = ''
        self.capacity = ''

    def to_dict(self):
        sub_area_dict = dict()
        sub_area_dict['name'] = self.name
        sub_area_dict['id'] = self.id
        sub_area_dict['type'] = self.type
        sub_area_dict['capacity'] = self.capacity
        return sub_area_dict

    @staticmethod
    def from_dict(sub_area_dict):
        sub_area = SubArea()
        sub_area.name = sub_area_dict['name']
        sub_area.id = sub_area_dict['id']
        sub_area.type = sub_area_dict['type']
        sub_area.capacity = sub_area_dict['capacity']
        return sub_area


class SubAreaReservation(object):
    def __init__(self):
        self.sub_area_id = -1
        self.task_id = ''
        self.robot_id = ''
        self.reservation_start_time = ''
        self.reservation_end_time = ''
        self.status = 'unknown'    # unknown or scheduled or cancelled
        self.required_capacity = -1

    def to_dict(self):
        sub_area_reservation_dict = dict()
        sub_area_reservation_dict['subAreaId'] = self.sub_area_id
        sub_area_reservation_dict['taskId'] = self.task_id
        sub_area_reservation_dict['robotId'] = self.robot_id
        sub_area_reservation_dict['startTime'] = self.start_time
        sub_area_reservation_dict['endTime'] = self.end_time
        sub_area_reservation_dict['status'] = self.status
        sub_area_reservation_dict['requiredCapacity'] = self.required_capacity
        return sub_area_reservation_dict

    @staticmethod
    def from_dict(sub_area_reservation_dict):
        sub_area_reservation = SubAreaReservation()
        sub_area_reservation.sub_area_id = sub_area_reservation_dict['subAreaId']
        sub_area_reservation.task_id = sub_area_reservation_dict['taskId']
        sub_area_reservation.robot_id = sub_area_reservation_dict['robotId']
        sub_area_reservation.start_time = sub_area_reservation_dict['startTime']
        sub_area_reservation.end_time = sub_area_reservation_dict['endTime']
        sub_area_reservation.status = sub_area_reservation_dict['status']
        sub_area_reservation.required_capacity = sub_area_reservation_dict['requiredCapacity']
        return sub_area_reservation

    def __repr__(self):
        return "<SubArea id:%(sub_area_id)s Robot id:%(robot_id)s Task id:%(task_id)s Start time:,\
         %(start_time)s End time:%(end_time)s Status:%(status)s>"%{
            'sub_area_id': self.sub_area_id, 'robot_id': self.robot_id, 'task_id': self.task_id, 'start_time': self.start_time, \
            'end_time': self.end_time, 'status': self.status
         }


class Area(object):
    def __init__(self):
        self.id = ''
        self.name = ''
        self.sub_areas = list()
        self.floor_number = 0
        self.type = ''

    def to_dict(self):
        area_dict = dict()
        area_dict['id'] = self.id
        area_dict['name'] = self.name
        area_dict['subAreas'] = list()
        area_dict['floorNumber'] = self.floor_number
        area_dict['type'] = self.type
        for sub_area in self.sub_areas:
            area_dict['subAreas'].append(sub_area.to_dict())
        return area_dict

    @staticmethod
    def from_dict(area_dict):
        area = Area()
        area.id = area_dict['id']
        area.name = area_dict['name']
        area.floor_number = area_dict['floorNumber']
        area.type = area_dict['type']
        for sub_areas_dict in area_dict['subAreas']:
            sub_area = SubArea.from_dict(sub_areas_dict)
            area.sub_areas.append(sub_area)
        return area
