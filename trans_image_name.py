#!/usr/bin/env python3
import hashlib
import json
import os.path
import sys
from collections import defaultdict

base = 'ccr.ccs.tencentyun.com/acejilam'

inner_repo = [
    'nmlabk1dsz', '0s6fw8l7rt', 'k8acwb59jt', 'asb7ey0ckh', 'cx0iujr1hd', 'dmk7blvfhi', 'm3qz8cr26i',
    'tcin8k239o', 'c3xyhfajvl', 'sqf3lrtm5d', '8friq1os9v', 'kl46e0x7v2', 't0cakez7u1', 'ut53ombafd',
    'er8c2l0ft4', 'm6hnixklv8', 'o0hy7f1l5q', 'pfs9xyuk8b', 'utj5z6cykp', '432aqtoflr', 'pxsuq87he9',
    't6yhnpcv7q', '7jstwmakc9', 'q2dkfymnh7', 'y1ef7ck6dr', 'cz7bpuhdlk', '3mck6e20t9', '8k34l57a6c',
    'wr0mfuk9d4', 'lh764rgbdj', 'xfv94yiwgz', 'l6jewm94pt', 'o95xz0mar1', 'kaemyf84i6', '7r5c2vef4i',
    'yq20ipejmw', '8hjuzgko01', '1nf85ctuov', 'pdrwk3f9on', '63rgv1d2fz', 'an9ydoeqsx', 'vi2tmfekdy',
    'op06w8m4dq', 'ruvpqdj23h', 'w92zmkustx', 'iszv5e2crb', 'u54f81rnay', '2c7e859ina', 'hpimk8va1l',
    '9vfu30gqos', 'y6vrbhjx3m', 'm8iyzvlj0t', 'i5mp02dgju', 'lneogt429q', 'g3am4cdkli', 'hnwopya265',
    'eg72vzc0fs', 'v4qel8dg23', 'b2h9zqputi', 'hq28x7jgaz', 'vw51banxem', 'zblwujy5oa', 'm40eudxnyz',
    'rax76uclqj', '1hf6imyk4b', '9edyokl1xz', 'urb3vy0qn1', 'h7ab0vx6yt', '6r0vqga49c', 'abo3cl4jef',
    'agd469misz', 'ij8gmonk7t', 'tjfpbmewh5', 'vdi3etfs5y', 'dveb417qg8', 'mxvpwiljub', 'jtwaylcz97',
    '3usd7z9y2x', 'h7ufbplxrk', 'mrqwp7yu6a', 'wfdlsk63yb', 'm9ujrlae28', 've34muab2x', 'ozu9sw6pgl',
    'w75yub6mip', 'oz5i4du0wp', 'k9sjui3vgb', 'lzyrndm3qf', 'eav12mkc9o', '6bao24gj01', '23mo0bl87g',
    '95zbwqlysf', '3uvkbcgmrf', 'xgfrjcd4h5', 'hy9opcvd5m', '0y1tg9wj7e', 'urhmniw452', 'nvgm6x8t71',
    'ag4sl3r8ot', 'qylw5i4623'
]

for i,item in enumerate(inner_repo):
    inner_repo[i] = 'ib-' + item

__random_image = {}
__fixed_image = {}


def __trans_random_image_name():
    global __random_image
    if len(__random_image) != 0:
        return __random_image
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
    __random_image = trans_images
    return trans_images


def __trans_fixed_image_name():
    global __fixed_image
    if len(__fixed_image) != 0:
        return __fixed_image
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
    __fixed_image = trans_images
    return trans_images


__trans_fixed_image_name()
__trans_random_image_name()


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
    fc = __input_replace(x)
    if fc != x:
        return fc
    if len(x.split('/')) == 1:
        _x = 'docker.io/library/' + x
        fc = __input_replace(_x)
        if fc != _x:
            return fc
    if len(x.split('/')) == 2:
        _x = 'docker.io/' + x
        fc = __input_replace(_x)
        if fc != _x:
            return fc
    return x


def __file_replace_image_name(_lines, _repo_map, _new_ts):
    new_text = ''
    # 'quay.io/submariner/lighthouse-agent:' -> 'ccr.ccs.tencentyun.com/acejilam/ib-hryzvxljcf:e78c12fb1ec7ea366f4e6d12ddd02c39-'
    # 'quay.io/submariner/lighthouse-agent' -> 'ccr.ccs.tencentyun.com/acejilam/ib-hryzvxljcf:e78c12fb1ec7ea366f4e6d12ddd02c39-latest'
    for _line in _lines:
        image_index = __handle_image(_line)  # 不包含 - image:
        if image_index > 0:
            new_line = _line.strip().split('#')[0].strip()
            raw_new_line = new_line.strip()
            if len(_line[image_index:].split('/')) == 1:
                new_line = new_line.replace(new_line.split(' ')[-1], 'docker.io/library/' + new_line.split(' ')[-1])
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
        print(trans_image(target.strip()))
