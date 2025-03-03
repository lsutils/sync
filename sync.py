import json
import os
import random
import subprocess
import sys


data = list(range(2, 10))
data.append('')
seq = random.sample(list(data), k=1)[0]
os.system(f"skopeo login -u pulldownload{seq}@gmail.com docker.io -p pulldownload{seq}")

def get_tags(rep):
    data = set()
    try:
        cmd = f"skopeo list-tags docker://{rep}"
        out = subprocess.getoutput(cmd)
        print(rep, cmd)
        data = set(json.loads(out)['Tags'])
    except Exception as e:
        print(e, out)
    x = set()
    for item in data:
        if item.startswith("v") or item.startswith("1") or item.startswith("2"):
            x.add(item)
    if len(x) == 0:
        x = data
    return x


base = 'registry.cn-hangzhou.aliyuncs.com/acejilam'
print(sys.argv)
item = sys.argv[1]
base_image = item.split('/')[-1]
h = get_tags(item)
a = get_tags(base + '/' + base_image)
print(len(h))
if len(h) == 0:
    raise Exception("null")
print(len(a))
# data = list(h - a)
# random.shuffle(data)

data = h

i = 0
for tag in data:
    if tag.endswith('.sbom'):
        print(f"skip {tag}")
        continue
    cmd = f'skopeo copy --all --insecure-policy docker://{item}:{tag} docker://registry.cn-hangzhou.aliyuncs.com/acejilam/{base_image}:{tag}'
    print(i, "/", len(data), cmd, flush=True)
    os.system(cmd)
    i += 1
