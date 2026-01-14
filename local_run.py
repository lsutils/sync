import json
import random
import os

with open('random-tasks.json', 'r', encoding='utf8') as f:
    data = list(json.loads(f.read()).keys())
    random.shuffle(data)
    for item in data:
        # REDIS_HOST={REDIS_HOST} REDIS_PASSWORD={REDIS_PASSWORD} python3 local_run.py
        os.system(f'python3 sync.py {item} -v')
