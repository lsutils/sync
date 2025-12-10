#!/usr/bin/env python3
import copy
import hashlib
import sys

from trans_image_name import __trans_random_image_name

_a = __trans_random_image_name()
# 检查是否有命令行参数
if len(sys.argv) > 1:
    # 从命令行参数获取数据
    lines = sys.argv[1:]
else:
    # 从stdin获取数据
    lines = sys.stdin.read().split('\n')

lines_bak = copy.deepcopy(lines)

res = ''
for line in lines:
    if line.strip() == '':
        continue
    line = line.strip()
    if 'acejilam/ib-' not in line:
        res += line.strip() + '\n'
        continue

    mda = line.split(':')[-1].split('-')[0]

    for old_image in _a:
        image_repo_md5 = hashlib.md5(old_image.encode('utf-8')).hexdigest()
        if image_repo_md5 == mda:
            new_line = old_image + ':' + '-'.join(line.split(':')[-1].split('-')[1:])
            new_line = new_line.strip()
            res += new_line + '\n'
print(res)


