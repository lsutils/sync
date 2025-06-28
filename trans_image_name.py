import os.path
import yaml
from collections import defaultdict

base = 'registry.cn-hangzhou.aliyuncs.com/acejilam'

def trans_image_name():
    sync_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".github", 'workflows', 'sync.yaml')
    res = yaml.safe_load(open(sync_path, 'r', encoding='utf8'))
    syncs = res['jobs']['build']['strategy']['matrix']['syncs']

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
    return trans_images


if __name__ == '__main__':
    ts = trans_image_name()
    text = input()
    for k, v in ts.items():
        text = text.replace(k, v)
    print(text)
