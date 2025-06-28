#!/usr/bin/env python3
import os.path
import sys

import yaml
from collections import defaultdict

base = 'registry.cn-hangzhou.aliyuncs.com/acejilam'


def trans_image_name():
    sync_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".github", 'workflows', 'sync.yaml')
    if not os.path.exists(sync_path):
        sync_path = '/Users/acejilam/k8s/sync/.github/workflows/sync.yaml'
    res = yaml.safe_load(open(sync_path, 'r', encoding='utf8'))
    syncs = res['jobs']['build']['strategy']['matrix']['syncs']

    trans_images = {}
    raws = defaultdict(list)

    for item in syncs:
        ss = item.strip('\" ').split(' ')
        if len(ss) == 1:
            base_name = ss[0].split('/')[-1]
            trans_images[ss[0]] = '%s/%s' % (base, base_name)
            raws[trans_images[ss[0]]].append(ss[0])

        else:
            trans_images[ss[0]] = '%s/%s' % (base, ss[-1])
            raws[trans_images[ss[0]]].append(ss[0])

    for k, vs in raws.items():
        if len(vs) > 1:
            print(vs, '======>', k)
    return trans_images


if __name__ == '__main__':
    sys.argv = ['/Users/acejilam/script/trans_image_name.py', 'dir', '/tmp/kube-prometheus/manifests']
    ts = trans_image_name()
    new_ts = {}
    for k, v in ts.items():
        if k.startswith('docker.io/'):
            new_ts[k[10:]] = v
    if sys.argv[1] == "dir":
        for _cd , dirs, files in os.walk(sys.argv[2]):
            for file in files:
                if file.endswith('.yaml') or file.endswith('.yml'):
                    file_path = os.path.join(_cd , file)
                    with open(file_path, 'r', encoding='utf8') as f:
                        text = f.read()
                        for k, v in ts.items():
                            text = text.replace(k, v)
                        for k, v in new_ts.items():
                            text = text.replace(k, v)
                        print(f"Handing {file_path}")
                    with open(file_path, 'w', encoding='utf8') as f:
                        f.write(text)
    elif sys.argv[1] == "file":
        with open(sys.argv[1], 'r', encoding='utf8') as f:
            text = f.read()
            for k, v in ts.items():
                text = text.replace(k, v)

            for k, v in new_ts.items():
                text = text.replace(k, v)

            print(text)
        with open(sys.argv[2], 'w', encoding='utf8') as f:
            f.write(text)
    else:
        text = input()
        for k, v in ts.items():
            text = text.replace(k, v)
        for k, v in new_ts.items():
            text = text.replace(k, v)
        print(text)
