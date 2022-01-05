import json

dumps = json.dumps
loads = json.loads

try:
    import ujson
except ImportError:
    pass
else:
    dumps = ujson.dumps
    loads = ujson.loads

try:
    import orjson
except ImportError:
    pass
else:
    dumps = orjson.dumps
    loads = orjson.loads
