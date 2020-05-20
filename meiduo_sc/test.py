import pickle
import base64

dict = {
    'code': 1,
    'errmsg': '都好'
}

dict1 = pickle.dumps(dict)
print(type(dict1))
print(dict1)
print('-----------------')
dict2 = base64.b64encode(dict1)
print(type(dict2))
print(dict2)
print('-----------------')
dict3 = dict2.decode()
print(type(dict3))
print(dict3)
print('-----------------')