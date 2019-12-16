import logging.config
import yaml
from stn.task import Task, InterTimepointConstraint


def config_logger(logging_file):

    with open(logging_file) as f:
        log_config = yaml.safe_load(f)
        logging.config.dictConfig(log_config)


def load_yaml(file):
    """ Reads a yaml file and returns a dictionary with its contents

    :param file: file to load
    :return: data as dict()
    """
    with open(file, 'r') as file:
        data = yaml.safe_load(file)
    return data


def create_task(stn, task_dict):
    task_id = task_dict.get("task_id")
    r_earliest_pickup = task_dict.get("earliest_pickup")
    r_latest_pickup = task_dict.get("latest_pickup")
    travel_time = InterTimepointConstraint(**task_dict.get("travel_time"))
    work_time = InterTimepointConstraint(**task_dict.get("work_time"))
    timepoint_constraints = stn.create_timepoint_constraints(r_earliest_pickup, r_latest_pickup, travel_time, work_time)
    inter_timepoint_constraints = [travel_time, work_time]

    return Task(task_id, timepoint_constraints, inter_timepoint_constraints)
