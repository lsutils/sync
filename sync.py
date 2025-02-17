import json
import os
import random
import subprocess
import sys


def get_tags(rep):
    data = set()
    try:
        cmd = f"skopeo list-tags docker://{rep}"
        out = subprocess.getoutput(cmd)
        print(rep, cmd, out)
        data = set(json.loads(out)['Tags'])
    except Exception as e :
        print(e)
    return data

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
data = list(h - a)
random.shuffle(data)

i = 0
for tag in data:
    cmd = f'skopeo copy --all --insecure-policy docker://{item}:{tag} docker://registry.cn-hangzhou.aliyuncs.com/acejilam/{base_image}:{tag}'
    print(i, "/", len(data), cmd, flush=True)
    os.system(cmd)
    i += 1
# os.system(f'skopeo sync --src docker --dest docker {item.f} {item.t} --src-tls-verify=false --dest-tls-verify=false')
