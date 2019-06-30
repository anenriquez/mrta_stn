from scheduler.scheduler import Scheduler
import json

PSTN = "data/pstn_one_task.json"

if __name__ == '__main__':
    with open(PSTN) as json_file:
        pstn_dict = json.load(json_file)

    # Convert the dict to a json string
    pstn_json = json.dumps(pstn_dict)

    scheduler = Scheduler('srea', json_temporal_network=pstn_json)

    print("PSTN: ", scheduler.temporal_network)

    print("Getting GUIDE...")
    alpha, guide_stn = scheduler.get_dispatch_graph()
    print("GUIDE")
    print(guide_stn)
    print("Alpha: ", alpha)

    completion_time = guide_stn.get_completion_time()
    makespan = guide_stn.get_makespan()
    print("Completion time: ", completion_time)
    print("Makespan: ", makespan)
