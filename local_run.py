import os
import yaml

res = yaml.safe_load(open('.github/workflows/sync.yaml', 'r', encoding='utf8'))

raw = res['jobs']['build']['strategy']['matrix']['syncs']
for item in raw:
    # REDIS_HOST={REDIS_HOST} REDIS_PASSWORD={REDIS_PASSWORD} python3 local_run.py
    os.system(f'python3 sync.py {item} -v')
