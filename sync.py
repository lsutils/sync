import json
import os
import random
import re
import sys
import redis
import subprocess

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

rdata = client.hgetall(source_image)


# data = list(range(2, 10))
# data.append('')
# seq = random.sample(list(data), k=1)[0]
# os.system(f"skopeo login -u pulldownload{seq}@gmail.com docker.io -p pulldownload{seq}")


def get_tags(rep):
    _data = set()
    _out = ""
    try:
        _cmd = f"skopeo list-tags docker://{rep}"
        _out = subprocess.getoutput(_cmd)
        print(rep, _cmd)
        _data = set(json.loads(_out)['Tags'])
    except Exception as e:
        print(e, _out)

    x = {"latest"}
    for _item in _data:
        if len(re.findall(r"^v?[0-9-.]+$", _item)) > 0:
            x.add(_item)

    for k, _ in rdata.items():
        if "latest" == k:
            continue
        try:
            x.remove(str(k))
        except:
            pass
    return x


base = 'registry.cn-hangzhou.aliyuncs.com/acejilam'
# base = 'ccr.ccs.tencentyun.com/acejilam'

if len(ss) != 1:
    new_name = ss[-1]
else:
    new_name = ss[0].split('/')[-1]

data = list(get_tags(source_image))
print(len(data))
random.shuffle(data)

i = 0
for tag in data:
    cmd = f'skopeo copy --all --insecure-policy docker://{source_image}:{tag} docker://{base}/{new_name}:{tag}'
    print(i, "/", len(data), cmd, flush=True)
    (code, text) = subprocess.getstatusoutput(cmd)
    if code == 0:
        client.hset(source_image, tag, "1")
        i += 1
    elif 'unsupported' in text or 'unknown' in text:
        client.hset(source_image, tag, "2")
        i += 1
    elif 'toomanyrequests' in text:
        sys.exit(1)
    else:
        print(text, flush=True)
