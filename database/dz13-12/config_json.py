import json

def to_json():
    db_conf = {
        "host":     "localhost",
        "port":     3306,
        "database": "py192",
        "user":     "py192_user",
        "password": "pass_192"
    }
    # Serializing json
    json_object = json.dumps(db_conf)
 
    # Writing to sample.json
    with open("config_file.json", "w") as outfile:
        outfile.write(json_object)


def from_json():
    with open('config_file.json', 'r') as f:
        data = json.load(f)

    print(data)
    return data




to_json()
from_json()