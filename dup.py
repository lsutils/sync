import yaml
from collections import Counter

res = yaml.safe_load(open('.github/workflows/sync.yaml', 'r', encoding='utf8'))

raw = res['jobs']['build']['strategy']['matrix']['syncs']

for i, _ in enumerate(raw):
    raw[i] = raw[i].strip('\" ')

max_len = max([len(item.split(' ')[0]) for item in raw]) + 20

counter = Counter()
for item in raw:
    item = item.strip('\" ')
    ss = item.split('  ')
    if len(ss) == 1:
        counter[item.split('/')[-1].strip()] += 1
    else:
        counter[ss[-1]] += 1

for k, v in counter.items():
    k = k.strip()
    if v != 1:
        message = f"{k} more than 1"
        print(message)

syncs = set()

for item in raw:
    raw_name = item.split(' ')[0].strip()

    new_name = item.split(' ')[-1].strip() if len(item.split(' ')) > 1 else ''

    syncs.add('"%s%s%s"' % (raw_name, ' ' * (max_len - len(raw_name)), new_name))

syncs = list(syncs)
syncs.sort()
res['jobs']['build']['strategy']['matrix']['syncs'] = syncs

# yaml.dump(res, open('.github/workflows/sync.yaml', 'w', encoding='utf8'))

with open('.github/workflows/sync.yaml', 'w', encoding='utf8') as f:
    f.write(yaml.dump(res, allow_unicode=False, default_flow_style=False, indent=4, width=10 ** 10))
