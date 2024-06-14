import json
import os
import subprocess

trans = [
    'docker.io/labring/kubernetes-docker',
    'docker.io/labring/kubernetes',
    'docker.io/labring/helm',
    'docker.io/labring/flannel',
    'docker.io/labring/calico',
    'docker.io/library/ubuntu',
    'docker.io/library/centos',
]


def get_tags(rep):
    data = set()
    try:
        data = set(json.loads(subprocess.getoutput(f"skopeo list-tags docker://{rep}"))['Tags'])
    except Exception:
        pass
    print(rep, data)
    return data


base = 'registry.cn-hangzhou.aliyuncs.com/acejilam'

for item in trans:
    base_image = item.split('/')[-1]
    data = list(get_tags(item) - get_tags(base + '/' + base_image))
    i = 0
    for tag in sorted(data):
        cmd = f'skopeo copy --all --insecure-policy docker://{item}:{tag} docker://registry.cn-hangzhou.aliyuncs.com/acejilam/{base_image}:{tag}'
        print(i, "/", len(data), cmd, flush=True)
        os.system(cmd)
        i += 1
    # os.system(f'skopeo sync --src docker --dest docker {item.f} {item.t} --src-tls-verify=false --dest-tls-verify=false')
