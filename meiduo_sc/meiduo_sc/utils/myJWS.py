# 自己写的json数据传输加密的py文件
from itsdangerous import JSONWebSignatureSerializer
from django.conf import settings


# 加密
def dumps(obj):
    secret_key = settings.SECRET_KEY
    s = JSONWebSignatureSerializer(secret_key)
    json_str = s.dumps(obj).decode()
    return json_str


# 解密
def loads(json):
    secret_key = settings.SECRET_KEY
    s = JSONWebSignatureSerializer(secret_key)
    try:
        obj = s.loads(json)
    except:
        return None
    else:
        return obj


