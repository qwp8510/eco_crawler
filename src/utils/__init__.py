import json


def get_json_content(path):
    with open(path, 'r') as js:
        content = json.load(js)
        js.close()
    return content


def dump_json_content(path, data):
    with open(path, 'w') as js:
        json.dump(data, js)
        js.close()
