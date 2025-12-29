import sys, os, json

try:
    sync_path = os.path.join(os.path.dirname(os.readlink(os.path.abspath(__file__))), 'random-tasks.json')
except OSError:
    sync_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'random-tasks.json')

with open(sync_path, 'r', encoding='utf8') as f:
    random_data = json.loads(f.read())

random_data['docker.io/alpine/k8s'] = ['1.34.1']

from trans_image_name import trans_image

print(trans_image('docker.io/alpine/k8s:1.34.1'))
