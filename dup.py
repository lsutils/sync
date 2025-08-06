import json

import yaml

from trans_image_name import trans_image_name


def split_list(lst, n):
    avg = len(lst) // n
    remainder = len(lst) % n
    result = []
    start = 0
    for i in range(n):
        end = start + avg + (1 if i < remainder else 0)
        result.append(lst[start:end])
        start = end
    return result


with open("tasks.json", "r") as f:
    raw = json.loads(f.read())

for i, _ in enumerate(raw):
    raw[i] = raw[i].strip('\" ')

syncs = set()
max_len = max([len(item.split(' ')[0]) for item in raw]) + 20

for item in raw:
    raw_name = item.split(' ')[0].strip()
    new_name = item.split(' ')[-1].strip() if len(item.split(' ')) > 1 else ''
    syncs.add("%s%s%s" % (raw_name, ' ' * (max_len - len(raw_name)), new_name))

template = yaml.safe_load(open('sync-template.yaml', 'r', encoding='utf8'))
trans_image_name()

syncs = list(syncs)
syncs.sort()
with open("tasks.json", "w", encoding='utf8') as f:
    f.write(json.dumps(syncs, indent=4, ensure_ascii=False))

for i, part in enumerate(split_list(syncs, 3)):
    template['name'] = f"sync-{i}"
    template['jobs']['build']['strategy']['matrix']['syncs'] = part
    with open(f'.github/workflows/sync-{i}.yaml', 'w', encoding='utf8') as f:
        f.write(yaml.dump(template, allow_unicode=False, default_flow_style=False, indent=4, width=10 ** 10))
