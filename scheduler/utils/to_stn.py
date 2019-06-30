from datasets.dataset_loader import load_dataset
from scheduler.temporal_networks.stn import STN
from scheduler.temporal_networks.stnu import STNU
from scheduler.temporal_networks.pstn import PSTN

""" Converts a dataset to an STN in json format
"""


def to_stn(dataset_name):
    stn = STN()
    tasks = load_dataset(dataset_name)

    for i, task in enumerate(tasks):
            stn.add_task(task, i+1)

    return stn.to_json()


def to_stnu(dataset_name):
    stnu = STNU()
    tasks = load_dataset(dataset_name)

    for i, task in enumerate(tasks):
            stnu.add_task(task, i+1)

    return stnu.to_json()


def to_pstn(dataset_name):
    pstn = PSTN()
    tasks = load_dataset(dataset_name)

    for i, task in enumerate(tasks):
            pstn.add_task(task, i+1)

    return pstn.to_json()


if __name__ == '__main__':
    stn_json = to_stn('three_tasks.csv')
    print(stn_json)
