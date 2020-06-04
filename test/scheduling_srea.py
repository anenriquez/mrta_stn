from stn.stp import STP
import json


def load_stn(file_path, stp_solver):
    with open(file_path) as json_file:
        stn_dict = json.load(json_file)

    stn_json = json.dumps(stn_dict)
    stp = STP(stp_solver)
    stn = stp.get_stn(stn_json=stn_json)
    return stp, stn


def get_schedule(dispatchable_graph, stn):
    task_id = dispatchable_graph.get_task_id(position=1)
    r_navigation_start = dispatchable_graph.get_time(task_id, 'navigation')
    print("r_navigation_start: ", r_navigation_start)

    dispatchable_graph.assign_timepoint(r_navigation_start, position=1)
    stn.assign_timepoint(r_navigation_start, position=1)

    r_finish = stn.get_time(task_id, 'finish', False)
    print("r_finish: ", r_finish)

    if stp.is_consistent(stn):
        print("The assignment is consistent")
        node_ids = dispatchable_graph.get_task_node_ids(task_id)
        schedule = dispatchable_graph.get_subgraph(n_tasks=1)
        print("Schedule:", schedule)

        return schedule
    else:
        print("Inconsistent assignment")


if __name__ == '__main__':

    stp, stn = load_stn("data/pstn_five_tasks.json", 'srea')
    n_tasks = 3
    print("STN: ", stn)

    dispatchable_graph = stp.solve(stn)
    print("Guide: ", dispatchable_graph)

    schedule = get_schedule(dispatchable_graph, stn)

    if schedule:
        sub_stn = stn.get_subgraph(n_tasks=3)
        print("Sub STN: ", sub_stn)

        # Instantiate next point in the schedule and check consistency in
        # the substn
        task_id = dispatchable_graph.get_task_id(position=1)
        r_start = dispatchable_graph.get_time(task_id, 'start')
        print("rstart: ", r_start)

        schedule.assign_timepoint(r_start, position=2)
        sub_stn.assign_timepoint(r_start, position=2)

        print("Schedule: ", schedule)
        print("SubSTN: ", sub_stn)

        if stp.is_consistent(sub_stn):
            print("Substn: The assignment is consistent")
            print(sub_stn)

        if stp.is_consistent(stn):
            print("Stn: The assignment is consistent")
            print(stn)


