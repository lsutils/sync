import json
import os
import re
import subprocess

import yaml

res = yaml.safe_load(open('.github/workflows/sync.yaml', 'r', encoding='utf8'))

raw = res['jobs']['build']['strategy']['matrix']['syncs']

try:
    os.mkdir('txts')
except:
    pass


def filter_tag(_item):
    if '.' not in _item:
        return True
    if 'SNAPSHOT' in _item:
        return True
    if 'debian' in _item:
        return True
    if '-ol-' in _item:
        return True
    if '-r' in _item:
        return True
    if 'mips64le' in _item:
        return True
    if 'ppc64le' in _item:
        return True
    if 's390x' in _item:
        return True
    if 'beta' in _item:
        return True
    if 'alpha' in _item:
        return True
    if 'snapshot' in _item:
        return True
    return False


for i, _ in enumerate(raw):
    raw[i] = raw[i].strip('\" ')

    ss = raw[i].strip(' "').split(' ')
    source_image = ss[0].strip()

    if len(ss) != 1:
        new_name = ss[-1]
    else:
        new_name = ss[0].split('/')[-1]

    _cmd = f"skopeo list-tags docker://{source_image}"
    if os.path.exists(f"txts/{new_name}.txt"):
        continue

    _out = subprocess.getoutput(_cmd)
    _data = set(json.loads(_out)['Tags'])
    x = {"latest"}
    for _item in _data:
        if len(re.findall(r"^v?[0-9-.]+$", _item)) > 0:
            x.add(_item)
    # if len(x) == 0:
    _data = x

    print("%s/%s" % (i, len(raw)), _cmd, len(_data))

    with open('txts/{}.txt'.format(new_name), 'w', encoding='utf8') as f:
        f.write(json.dumps(list(_data), ensure_ascii=False, indent=4))
