import pickle
import base64


def dumps(dict):
    dict_bytes = pickle.dumps(dict)
    dict_secret = base64.b64encode(dict_bytes)
    dict_json = dict_secret.decode()
    return dict_json


def loads(dict_json):
    dict_secret = dict_json.encode()
    dict_bytes = base64.b64decode(dict_secret)
    dict = pickle.loads(dict_bytes)
    return dict
