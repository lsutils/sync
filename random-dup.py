import json

import yaml


def split_list(d: dict, n):
    lst = []
    for k, v in d.items():
        if len(v) > 0:
            lst.append(k)
    avg = len(lst) // n
    remainder = len(lst) % n
    result = []
    start = 0
    for i in range(n):
        end = start + avg + (1 if i < remainder else 0)
        result.append(lst[start:end])
        start = end
    return result


with open("random-tasks.json", "r") as f:
    _syncs = json.loads(f.read())
    syncs = {}
    for k, v in _syncs.items():
        syncs[k.strip()] = v

template = yaml.safe_load(open('sync-template.yaml', 'r', encoding='utf8'))

with open("random-tasks.json", "w", encoding='utf8') as f:
    f.write(json.dumps(syncs, indent=4, ensure_ascii=False))

for i, part in enumerate(split_list(syncs, len(syncs) // 256 + 1)):
    template['name'] = f"random-sync-{i}"
    template['jobs']['build']['strategy']['matrix']['syncs'] = part
    with open(f'.github/workflows/random-sync-{i}.yaml', 'w', encoding='utf8') as f:
        f.write(yaml.dump(template, allow_unicode=False, default_flow_style=False, indent=4, width=10 ** 10))
