from stp.stp import STP
import json

PSTN = "data/pstn_one_task.json"

if __name__ == '__main__':
    with open(PSTN) as json_file:
        pstn_dict = json.load(json_file)

    # Convert the dict to a json string
    pstn_json = json.dumps(pstn_dict)

    stp = STP('srea')
    pstn = stp.load_stn(pstn_json)

    print("PSTN: ", pstn)

    print("Getting GUIDE...")
    alpha, guide = stp.get_dispatchable_graph(pstn)
    print("GUIDE")
    print(guide)
    print("Alpha: ", alpha)

    completion_time = guide.get_completion_time()
    makespan = guide.get_makespan()
    print("Completion time: ", completion_time)
    print("Makespan: ", makespan)
