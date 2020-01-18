import functools
import json

pretty_json = functools.partial(json.dumps, indent=4)
