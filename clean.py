data = []

from trans_image_name import trans_image_name

tp = set(trans_image_name().values())
exists = set()
for pre_item in data:
    for item in pre_item['data']['data']['repos']:
        it = f'registry.cn-hangzhou.aliyuncs.com/%s/%s' % (item['repoNamespace'], item['repoName'])
        exists.add(it)

print(exists - tp)
