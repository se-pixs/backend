import json


def open_json(filepath):
    with open(filepath, 'r') as f:
        return json.loads(f.read())


def hex_to_rgb(hex):
    hex = hex.lstrip('#')
    return tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))
