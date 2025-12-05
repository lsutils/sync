import random
import string

repo = []
for i in range(0, 60):
    data = list(string.ascii_lowercase)
    random.shuffle(data)
    repo.append('inner-bucket-' + ''.join(data[:10]))

print(repo)
