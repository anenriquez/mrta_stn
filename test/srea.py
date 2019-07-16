from stn.stp import STP
import json


if __name__ == '__main__':
    with open("data/pstn_one_task.json") as json_file:
        pstn_dict = json.load(json_file)

    # Convert the dict to a json string
    pstn_json = json.dumps(pstn_dict)

    stp = STP('srea')

    stn = stp.get_stn(stn_json=pstn_json)
    dispatchable_graph = stp.get_stn()

    print("STN: ", stn)
    print("Dispatchable graph: ", dispatchable_graph)

    print("Getting GUIDE...")
    alpha, guide = stp.compute_dispatchable_graph(stn)
    print("GUIDE")
    print(guide)
    print("Alpha: ", alpha)

    completion_time = guide.get_completion_time()
    makespan = guide.get_makespan()
    print("Completion time: ", completion_time)
    print("Makespan: ", makespan)
