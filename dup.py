import yaml
from collections import Counter

res = yaml.load(open('.github/workflows/sync.yaml', 'r', encoding='utf8'), Loader=yaml.SafeLoader)

raw = res['jobs']['build']['strategy']['matrix']['syncs']

for i, _ in enumerate(raw):
    raw[i] = raw[i].strip('\" ')

max_len = max([len(item.split(' ')[0]) for item in raw]) + 20

c = Counter()
for item in raw:
    item = item.strip('\" ')
    ss = item.split('  ')
    if len(ss) == 1:
        c[item.split('/')[-1].strip()] += 1
    else:
        c[ss[-1]] += 1

for k, v in c.items():
    if v != 1:
        message = f"{k} more than 1"
        raise Exception(message)

syncs = []

for item in raw:
    raw_name = item.split(' ')[0].strip()

    new_name = item.split(' ')[-1].strip() if len(item.split(' ')) > 1 else ''

    syncs.append('"%s%s%s"' % (raw_name, ' ' * (max_len - len(raw_name)), new_name))

syncs.sort()
res['jobs']['build']['strategy']['matrix']['syncs'] = syncs

# yaml.dump(res, open('.github/workflows/sync.yaml', 'w', encoding='utf8'))

print(yaml.dump(res, allow_unicode=False, default_flow_style=False, indent=4, width=10 ** 4))
