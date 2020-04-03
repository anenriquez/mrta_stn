import logging.config
import yaml
from stn.task import Task, Edge
from stn.utils.uuid import generate_uuid


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
    travel_time = Edge(**task_dict.get("travel_time"))
    work_time = Edge(**task_dict.get("work_time"))
    timepoint_constraints = stn.create_timepoint_constraints(r_earliest_pickup, r_latest_pickup, travel_time, work_time)
    inter_timepoint_constraints = [travel_time, work_time]
    pickup_action_id = generate_uuid()
    delivery_action_id = generate_uuid()

    return Task(task_id, timepoint_constraints, inter_timepoint_constraints, pickup_action_id, delivery_action_id)
