#!/usr/bin/env python3
import json
import os.path
import sys
from collections import defaultdict

base = 'registry.cn-hangzhou.aliyuncs.com/acejilam'


def trans_image_name():
    try:
        sync_path = os.path.join(os.path.dirname(os.readlink(os.path.abspath(__file__))),'tasks.json')
    except OSError:
        sync_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'tasks.json')

    syncs = json.load(open(sync_path, 'r', encoding='utf8'))

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
    ts = trans_image_name()
    new_ts = {}
    for k, v in ts.items():
        if k.startswith('docker.io/'):
            new_ts[k[10:]] = v
    target = sys.argv[1]

    if os.path.isdir(target):
        for _cd, dirs, files in os.walk(target):
            for file in files:
                if file.endswith('.yaml') or file.endswith('.yml'):
                    file_path = os.path.join(_cd, file)
                    with open(file_path, 'r', encoding='utf8') as f:
                        text = f.read()
                        for k, v in ts.items():
                            text = text.replace(k, v)
                        for k, v in new_ts.items():
                            text = text.replace(k, v)
                        print(f"Handing {file_path}")
                    with open(file_path, 'w', encoding='utf8') as f:
                        f.write(text)
    elif os.path.isfile(target):
        with open(target, 'r', encoding='utf8') as f:
            text = f.read()
            for k, v in ts.items():
                text = text.replace(k, v)
            for k, v in new_ts.items():
                text = text.replace(k, v)
            print(text)
        with open(target, 'w', encoding='utf8') as f:
            f.write(text)
    else:
        text = input()
        for k, v in ts.items():
            text = text.replace(k, v)
        for k, v in new_ts.items():
            text = text.replace(k, v)
        print(text)
