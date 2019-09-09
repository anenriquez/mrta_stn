class STNTask(object):
    def __init__(self, id,
                 r_earliest_navigation_start_time,
                 r_earliest_start_time,
                 r_latest_start_time,
                 start_pose_name,
                 finish_pose_name,
                 **kwargs):

        """ Constructor for the Task object

        Args:
            id (UUID): An instance of an UUID object
            r_earliest_navigation_start_time (float): earliest navigation start time relative to the ztp
            r_earliest_start_time (float): earliest start time relative to the ztp
            r_latest_start_time (float): latest start time relative to the ztp
            start_pose_name (str): Name of the location where the robot should execute the task
            finish_pose_name (str): Name of the location where the robot must terminate task execution
            hard_constraints (bool): False if the task can be
                                    scheduled ASAP, True if the task is not flexible. Defaults to True
        """
        self.id = id
        self.r_earliest_navigation_start_time = round(r_earliest_navigation_start_time, 2)
        self.r_earliest_start_time = round(r_earliest_start_time, 2)
        self.r_latest_start_time = round(r_latest_start_time, 2)
        self.start_pose_name = start_pose_name
        self.finish_pose_name = finish_pose_name
        self.hard_constraints = kwargs.get('hard_constraints', True)
