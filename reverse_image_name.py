#!/usr/bin/env python3

import hashlib
import sys

from trans_image_name import __trans_random_image_name

_a = __trans_random_image_name()

res = ''
for line in sys.stdin.read().split('\n'):
    if line.strip() == '':
        continue
    line = line.strip()
    if 'acejilam/ib-' not in line:
        res += line + '\n'
        continue

    mda = line.split(':')[-1].split('-')[0]

    for old_image in _a:
        image_repo_md5 = hashlib.md5(old_image.encode('utf-8')).hexdigest()
        if image_repo_md5 == mda:
            res += old_image + ':' + '-'.join(line.split(':')[-1].split('-')[1:]) + '\n '
print(res)
# ╰─ trans_image_name.py docker.io/library/buildpack-deps:24.04                                             192.168.1.12   M3 ─╯
# registry.cn-hangzhou.aliyuncs.com/acejilam/ib-miszxulobc:c2607219cd5d6f2c4570f4e3986db743-24.04
