import json
from stn.stp import STP
STNU = "data/stnu_two_tasks.json"


if __name__ == '__main__':
    with open(STNU) as json_file:
        stnu_dict = json.load(json_file)

    # Convert the dict to a json string
    stnu_json = json.dumps(stnu_dict)

    stp = STP('dsc_lp')
    stn = stp.get_stn(stn_json=stnu_json)

    print(stn)
    stn_dict = stn.to_dict()

    print(stn_dict)
    print(type(stn_dict['nodes'][0]['data']))
