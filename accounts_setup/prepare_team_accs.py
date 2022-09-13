from collections import defaultdict

import json
import numpy as np
import pandas as pd

PATH_TO_TEAMS_CSV = './Twitter_Accounts.csv'
SPORTS_TAGS = [
    'BASE', 'MBB', 'WBB', 'WVB', 'FB', 'MXC',
    'MGOLF', 'MGYM', 'MHKY', 'MITF', 'MLAX', 'MOTF', 'MSOC', 'MSD', 'MTEN',
    'WREST', 'WXC', 'FH', 'WGOLF', 'WGYM', 'WITF', 'WLAX', 'WOTF', 'WROW',
    'WTEN', 'WSD', 'SB', 'WSOC'
]
PATH_TO_SAVE = 'team_accounts.json'

df = pd.read_csv(PATH_TO_TEAMS_CSV)
acc_tags = defaultdict(set)

for _, row in df.iterrows():
    team_tag = row['TEAM_TAG']
    for tag in SPORTS_TAGS:
        acc = row[tag]
        if isinstance(acc, float):
            continue
        acc = acc.replace(' ', '')
        acc_tags[acc].add(tag.lower())
        acc_tags[acc].add(team_tag.lower())

# {
#     "name": "Gophertags",
#     "tags": [],
#     "desc": "Minnesota",
#     "id": 0
#   }

js = []
for acc, tags in acc_tags.items():
    acc = acc.split(',')
    acc_name, acc_id = acc[0], int(acc[1])
    js.append({
        "name": acc_name,
        "tags": list(tags),
        "desc": acc_name,
        "id": acc_id
    })

with open(PATH_TO_SAVE, 'w') as f:
    json.dump(js, f, indent=2)

# print(js)
