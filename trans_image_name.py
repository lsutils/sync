#!/usr/bin/env python3
import hashlib
import json
import os.path
import sys
from collections import defaultdict

base = 'registry.cn-hangzhou.aliyuncs.com/ls-acejilam'

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


def __trans_random_image_name():
    try:
        sync_path = os.path.join(os.path.dirname(os.readlink(os.path.abspath(__file__))), 'random-tasks.json')
    except OSError:
        sync_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'random-tasks.json')

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


def __trans_fixed_image_name():
    try:
        sync_path = os.path.join(os.path.dirname(os.readlink(os.path.abspath(__file__))), 'fixed-tasks.json')
    except OSError:
        sync_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixed-tasks.json')

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
            sys.exit(1)
    return trans_images


def __inner_trans_image():
    _a = __trans_random_image_name()
    _b = __trans_fixed_image_name()
    for _k, _v in _b.items():
        _a[_k] = _v
    return _a


def __handle_image(_line):
    if _line.strip().startswith('image: '):
        return _line.index('image: ')
    elif _line.strip().startswith('- image: '):
        return _line.index('- image: ')
    else:
        return -1


def trans_image(x):
    return __input_replace(x)


def __file_replace_image_name(_lines, _repo_map, _new_ts):
    new_text = ''
    # 'quay.io/submariner/lighthouse-agent:' -> 'registry.cn-hangzhou.aliyuncs.com/ls-acejilam/ib-hryzvxljcf:e78c12fb1ec7ea366f4e6d12ddd02c39-'
    # 'quay.io/submariner/lighthouse-agent' -> 'registry.cn-hangzhou.aliyuncs.com/ls-acejilam/ib-hryzvxljcf:e78c12fb1ec7ea366f4e6d12ddd02c39-latest'
    for _line in _lines:
        image_index = __handle_image(_line)
        if image_index > 0:
            new_line = _line.strip().split('#')[0].strip()
            raw_new_line = new_line.strip()
            for _k, _v in _repo_map.items():
                new_line = new_line.replace(_k + ':', _v)
                new_line = new_line.replace(_k + '', _v + 'latest')
            for _k, _v in _new_ts.items():
                new_line = new_line.replace(_k + ':', _v)
                new_line = new_line.replace(_k + '', _v + 'latest')

            if raw_new_line != new_line:
                new_text += _line[:image_index] + new_line + '\n'
                new_text += _line[:image_index] + f'# {raw_new_line}\n'
            else:
                new_text += _line
        else:
            new_text += _line
    return new_text


def __input_replace(_repo):
    _b = __trans_fixed_image_name()
    ss = _repo.split(":")
    if ss[0] in _b:
        if len(ss) == 1:
            return _b[ss[0]] + ':latest'
        else:
            return _b[ss[0]] + ':' + ss[-1]

    _a = __trans_random_image_name()
    ss = _repo.split(":")
    if ss[0] in _a:
        if len(ss) == 1:
            return _a[ss[0]] + 'latest'
        else:
            return _a[ss[0]] + ss[-1]
    return _repo


if __name__ == '__main__':
    repo_map = __inner_trans_image()
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
                    lines = []
                    with open(file_path, 'r', encoding='utf8') as f:
                        for line in f.readlines():
                            lines.append(line)
                    text = __file_replace_image_name(lines, repo_map, new_ts)
                    print(f"Handing {file_path}")
                    with open(file_path, 'w', encoding='utf8') as f:
                        f.write(text)
    elif os.path.isfile(target):
        lines = []
        with open(target, 'r', encoding='utf8') as f:
            for line in f.readlines():
                lines.append(line)
        text = __file_replace_image_name(lines, repo_map, new_ts)
        with open(target, 'w', encoding='utf8') as f:
            f.write(text)
    else:
        print(__input_replace(target.strip()))
