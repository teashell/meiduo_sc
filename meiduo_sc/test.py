# import re
#
# str = 'mobiles/13645788794/count/'
# result = re.match('^mobiles/(?P<mobile>1[345789]\d{9})/count/', str)
#
# print()
# print(result)


class A(object):

    def __init__(self):
        print(f'{self}已经初始化了!')

    a = 10

    @classmethod
    def say(cls):
        a1 = cls()
        print(type(a1))
        print(cls.a)
        print(a1.a)

a2 = A()
a2.say()
