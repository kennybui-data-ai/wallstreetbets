import json

credentials_path = "../wsb/credentials.json"
with open(credentials_path, "r") as f:
    credentials = json.loads(f.read())

with open(credentials_path, "w") as f:
    f.write(json.dumps(credentials, indent=4))
