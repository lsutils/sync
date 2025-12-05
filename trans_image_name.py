#!/usr/bin/env python3
import hashlib
import json
import os.path
import sys
from collections import defaultdict

base = 'registry.cn-hangzhou.aliyuncs.com/acejilam'

inner_repo = [
    'ib-qzektvsmnc', 'ib-ruijlfpdsx', 'ib-msfhubercn', 'ib-ownytfkadb',
    'ib-bfijvokmgn', 'ib-miszxulobc', 'ib-nyifoskdez', 'ib-ybtpavlcow',
    'ib-lakmjqpzso', 'ib-lnfbysmexd', 'ib-jznfirseqv', 'ib-irxtlfvnyd',
    'ib-hmbsdvxrca', 'ib-jafegbonpx', 'ib-ibxjuryzfk', 'ib-jodklrnfyv',
    'ib-morclntjdx', 'ib-lcaxbsknre', 'ib-ybcsphvmdf', 'ib-zlumcpbrsx',
    'ib-zbanxhwkge', 'ib-yhpmzaevik', 'ib-zuxyiseklo', 'ib-tglovcamhy',
    'ib-dwbsonmiuv', 'ib-lqcuoxzkrp', 'ib-scoazytebu', 'ib-siraobxwnq',
    'ib-chpmflbzgi', 'ib-envawyrpbl',
]


def trans_image_name():
    try:
        sync_path = os.path.join(os.path.dirname(os.readlink(os.path.abspath(__file__))), 'tasks.json')
    except OSError:
        sync_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tasks.json')

    syncs = json.load(open(sync_path, 'r', encoding='utf8'))

    raws = defaultdict(list)

    for item in syncs:
        ss = item.strip('\" ').split(' ')
        if len(ss) == 1:
            image = ss[0]
            raws[image].append(image)
        elif len(ss) == 2:
            fixed_name = ss[0].strip().split('/')
            fixed_name[-1] = ss[-1]
            raws['/'.join(fixed_name)].append(ss)

    for k, vs in raws.items():
        if len(vs) > 1:
            print(vs, '======>', k)
            sys.exit(1)

    for item in syncs:
        ss = item.strip('\" ').split(' ')
        if len(ss) == 1:
            image = ss[0]
            raws[image].append(image)
        else:
            fixed_name = ss[0].strip().split('/')
            fixed_name[-1] = ss[1]
            raws['/'.join(fixed_name)].append(ss[0])
    trans_images = {}  # raw_name -> inner name

    for new_name, old_images in raws.items():
        old_image = old_images[0]
        md5_bytes = hashlib.md5(new_name.encode('utf-8')).digest()
        image_repo = hashlib.md5(old_image.encode('utf-8')).hexdigest()
        inner_bucket = inner_repo[int.from_bytes(md5_bytes, byteorder="big") % len(inner_repo)]
        trans_images[old_image] = f'{base}/{inner_bucket}:{image_repo}-'

    return trans_images


def replace_image_name(_file_path, _repo_map, _new_ts):
    new_text = ''
    # 'quay.io/submariner/lighthouse-agent:' -> 'registry.cn-hangzhou.aliyuncs.com/acejilam/ib-hryzvxljcf:e78c12fb1ec7ea366f4e6d12ddd02c39-'
    # 'quay.io/submariner/lighthouse-agent' -> 'registry.cn-hangzhou.aliyuncs.com/acejilam/ib-hryzvxljcf:e78c12fb1ec7ea366f4e6d12ddd02c39-latest'

    with open(_file_path, 'r', encoding='utf8') as f:
        for line in f.readlines():
            if line.strip().startswith('image: '):
                image_index = line.index('image: ')
                new_line = line.strip().split('#')[0].strip()
                raw_new_line = new_line.strip()
                for _k, _v in repo_map.items():
                    new_line = new_line.replace(_k + ':', _v)
                    new_line = new_line.replace(_k + '', _v + 'latest')
                for _k, _v in new_ts.items():
                    new_line = new_line.replace(_k + ':', _v)
                    new_line = new_line.replace(_k + '', _v + 'latest')

                if raw_new_line != new_line:
                    new_text += line[:image_index] + new_line + '\n'
                    new_text += line[:image_index] + f'# {raw_new_line}\n'
                else:
                    new_text += line
            else:
                new_text += line
    return new_text


if __name__ == '__main__':
    repo_map = trans_image_name()
    new_ts = {}
    for k, v in repo_map.items():
        if k.startswith('docker.io/'):
            new_ts[k[10:]] = v

    target = sys.argv[1]

    if os.path.isdir(target):
        for _cd, dirs, files in os.walk(target):
            for file in files:
                if file.endswith('.yaml') or file.endswith('.yml'):
                    file_path = os.path.join(_cd, file)

                    text = replace_image_name(file_path, repo_map, new_ts)
                    print(f"Handing {file_path}")
                    with open(file_path, 'w', encoding='utf8') as f:
                        f.write(text)
    elif os.path.isfile(target):
        with open(target, 'r', encoding='utf8') as f:
            text = f.read()
            text = replace_image_name(text, repo_map, new_ts)
            print(text)
        with open(target, 'w', encoding='utf8') as f:
            f.write(text)
    else:
        text = target
        text = replace_image_name(text, repo_map, new_ts)
        print(text)
