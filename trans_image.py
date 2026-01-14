#!/usr/bin/env python3
import hashlib
import json
import os.path
import sys
from collections import defaultdict
import subprocess


def trans_image(x, random_path=None, fixed_path=None):
    with open("/tmp/trans.sh", 'wb', encoding='utf8') as f:
        f.write(f"export RandomImagePath={random_path}\n")
        f.write(f"export FixImagePath={fixed_path}\n")
        f.write(f"trans-image-name {x}")
    return subprocess.getoutput('bash /tmp/trans.sh')
