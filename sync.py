import json
import os
import subprocess
import sys

from trans_image import trans_image

_input = sys.argv[1]
print(sys.argv)
ss = _input.strip(' "').split(' ')
source_image = ss[0].strip()

skopeo_bin = 'skopeo'
tags = []

with open('random-tasks.json', 'r', encoding='utf8') as f:
    data = json.load(f)
    if _input in data:
        tags = data[_input]
with open('fixed-tasks.json', 'r', encoding='utf8') as f:
    data = json.load(f)
    if _input in data:
        tags = data[_input]

if 'darwin' in sys.platform.lower():
    skopeo_bin = '/opt/homebrew/bin/skopeo'

print(tags)

i = 0
for tag in tags:
    with open('/tmp/sync.sh', 'w', encoding='utf8') as f:
        f.write(f'''
source ~/script/.customer_script.sh
eval "$(print_proxy.py)"
rm -rf /tmp/sync.txt
set -x 
{skopeo_bin} copy --all --insecure-policy docker://{source_image}:{tag} docker://{trans_image(source_image + ":" + tag)}
echo $?> /tmp/sync.txt
''')

    print(i, "/", len(tags), flush=True)
    os.system(f'bash /tmp/sync.sh')
    with open('/tmp/sync.txt', 'r', encoding='utf8') as f:
        sys.exit(int(f.read()))
