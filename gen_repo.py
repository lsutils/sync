import random
import string

data = list(string.digits + string.ascii_lowercase)

bus = []
for i in range(100):
    random.shuffle(data)
    bus.append(''.join(data)[:10])
print(bus)