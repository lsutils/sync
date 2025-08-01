import json
import os
import platform
import random
import re
import subprocess
import sys

import redis

from trans_image_name import trans_image_name

_input = sys.argv[1]
print(sys.argv)
ss = _input.strip(' "').split(' ')
source_image = ss[0].strip()

client = redis.StrictRedis(
    host=os.getenv("REDIS_HOST"),
    port=26379,
    db=10,
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)
todo_client = redis.StrictRedis(
    host=os.getenv("REDIS_HOST"),
    port=26379,
    db=11,
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)
rdata = client.hgetall(source_image)
todo_data = todo_client.hgetall(source_image)

skopeo_bin = 'skopeo'
if platform.system() == 'Darwin':
    skopeo_bin = '/opt/homebrew/bin/skopeo'


# data = list(range(2, 10))
# data.append('')
# seq = random.sample(list(data), k=1)[0]
# os.system(f"skopeo login -u pulldownload{seq}@gmail.com docker.io -p pulldownload{seq}")


def get_tags(rep):
    _data = set()
    _out = ""
    try:
        _cmd = f"{skopeo_bin} list-tags docker://{rep}"
        _out = subprocess.getoutput(_cmd)
        print(rep, _cmd)
        _data = set(json.loads(_out)['Tags'])
    except Exception as e:
        print(e, _out)

    x = set()
    for _item in _data:
        if _item == "latest":
            x.add(_item)
        if len(_item) > 10 and '.' not in _item[:9]:
            continue
        if len(re.findall(r"^v?[0-9-.]+.*", _item)) > 0:
            x.add(_item)

    for k, _ in rdata.items():
        if "latest" == k:
            continue
        try:
            x.remove(str(k))
        except:
            pass
    for k, _ in todo_data.items():
        x.add(str(k))
    return x


image_map = trans_image_name()

data = list(get_tags(source_image))

print(len(data))
random.shuffle(data)
print(data)

i = 0
for tag in data:
    cmd = f'{skopeo_bin} copy --all --insecure-policy docker://{source_image}:{tag} docker://{image_map[source_image]}:{tag}'
    print(i, "/", len(data), cmd, flush=True)
    (code, text) = subprocess.getstatusoutput(cmd)
    print(text, flush=True)
    if code == 0:
        client.hset(source_image, tag, "1")
        i += 1
    elif 'unsupported' in text or 'unknown' in text:
        client.hset(source_image, tag, "2")
        i += 1
    elif 'toomanyrequests' in text:
        sys.exit(1)
