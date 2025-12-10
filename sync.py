import json
import subprocess
import sys

from trans_image_name import trans_image

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
    cmd = f'{skopeo_bin} copy --all --insecure-policy docker://{source_image}:{tag} docker://{trans_image(source_image + ":" + tag)}'
    print(i, "/", len(tags), cmd, flush=True)
    (code, text) = subprocess.getstatusoutput(cmd)
    print(text, flush=True)
    if code == 0:
        i += 1
    elif 'unsupported' in text or 'unknown' in text:
        i += 1
    elif 'toomanyrequests' in text:
        sys.exit(1)
