import json

dict_data = {"first": 1, 'second': 2}

res = json.dumps(dict_data).encode('utf-8')
res = bytes(res)
print(res)

from io import StringIO

res_json = json.load(StringIO(res.decode('utf-8')))

print(res_json)
