import re

str = 'mobiles/13645788794/count/'
result = re.match('^mobiles/(?P<mobile>1[345789]\d{9})/count/', str)

print()
print(result)