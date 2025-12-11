#!/usr/bin/env python3
import json
import os.path
import sys



try:
    fix_sync_path = os.path.join(os.path.dirname(os.readlink(os.path.abspath(__file__))), 'fixed-tasks.json')
except OSError:
    fix_sync_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixed-tasks.json')

with open(fix_sync_path, 'r', encoding='utf8') as f:
    fix_data = json.loads(f.read())

try:
    sync_path = os.path.join(os.path.dirname(os.readlink(os.path.abspath(__file__))), 'random-tasks.json')
except OSError:
    sync_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'random-tasks.json')

with open(sync_path, 'r', encoding='utf8') as f:
    random_data = json.loads(f.read())

if __name__ == '__main__':
    repo_tag = sys.argv[1].strip()
    repo, tag = '', ''
    if len(repo_tag.split(':')) == 2:
        repo, tag = repo_tag.split(':')
    else:
        repo, tag = repo_tag, "latest"
    if repo in fix_data:
        print('only handle random repo')
        sys.exit(1)
    s_img = f'{repo}:{tag}'
    if repo in random_data:
        ds = set(random_data[repo])
        ds.add(tag)
        random_data[repo] = list(ds)
    else:
        random_data[repo] = [tag]
    with (open(sync_path, 'w', encoding='utf8')) as f:
        f.write(json.dumps(random_data, indent=4, ensure_ascii=False))
    from trans_image_name import trans_image
    with open('/tmp/sc.sh', 'w', encoding='utf8') as f:
        f.write(f'''
source ~/script/.customer_script.sh
skopeo_copy {s_img} {trans_image(s_img)}
cd ~/k8s/sync
eval "$(print_proxy.py)"
git add .
git commit -m "{s_img}"
git push 
''')
    os.system('zsh /tmp/sc.sh')
