import json
import os

with open('random-tasks.json', 'r', encoding='utf8') as f:
    data = list(json.loads(f.read()).keys())
    data.sort()
    for i, item in enumerate(data):
        print(f'[{i}/{len(data)}] {item}')
        # REDIS_HOST={REDIS_HOST} REDIS_PASSWORD={REDIS_PASSWORD} python3 local_run.py
        code = 1
        while code != 0:
            os.system(f'python3 sync.py {item} -v')
            with open('/tmp/sync.txt', 'r', encoding='utf8') as f:
                code = int(f.read())
