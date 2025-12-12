#!/usr/bin/env python3
import json
import os
import sys
from collections import defaultdict

skopeo_bin = 'skopeo'
tags = []

res = defaultdict(list)

try:
    fix_sync_path = os.path.join(os.path.dirname(os.readlink(os.path.abspath(__file__))), 'fixed-tasks.json')
except OSError:
    fix_sync_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixed-tasks.json')

with open(fix_sync_path, 'r', encoding='utf8') as f:
    data = json.load(f)
    for k, v in data.items():
        res[k].extend(v)

try:
    sync_path = os.path.join(os.path.dirname(os.readlink(os.path.abspath(__file__))), 'random-tasks.json')
except OSError:
    sync_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'random-tasks.json')

with open(sync_path, 'r', encoding='utf8') as f:
    data = json.load(f)
    for k, v in data.items():
        res[k].extend(v)

if 'darwin' in sys.platform.lower():
    skopeo_bin = '/opt/homebrew/bin/skopeo'

for k, tags in res.items():
    if len(tags) == 0:
        continue
    for tag in tags:
        source_image = f'{k}:{tag}'
        with open('/tmp/sl.sh', 'w', encoding='utf8') as f:
            f.write(f'''
    source ~/script/.customer_script.sh
    eval "$(print_proxy.py)"
    trans-image-to-ls-harbor.py --arch all --source {source_image}
    ''')
        os.system('zsh /tmp/sl.sh')
