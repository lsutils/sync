import json
import os
import random
import sys
import redis
import subprocess

source_image = sys.argv[1]

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
    x = set()
    for _item in _data:
        if _item.startswith("v") or _item.startswith("1") or _item.startswith("2") or _item == "latest":
            x.add(_item)
    # if len(x) == 0:
        # x = _data
    
    for k, _ in rdata.items():
        if "latest" == k:
            continue
        x.remove(str(k))

    return x


base = 'registry.cn-hangzhou.aliyuncs.com/acejilam'
print(sys.argv)
base_image = source_image.split('/')[-1]
data = list(get_tags(source_image))

print(len(data))

random.shuffle(data)

i = 0
for tag in data:
    if tag.endswith('.sbom'):
        print(f"skip {tag}")
        continue
    cmd = f'skopeo copy --all --insecure-policy docker://{source_image}:{tag} docker://registry.cn-hangzhou.aliyuncs.com/acejilam/{base_image}:{tag}'
    print(i, "/", len(data), cmd, flush=True)
    res = subprocess.run(cmd, shell=True)
    if res.returncode == 0:
        client.hset(source_image, tag, "1")
        i += 1
