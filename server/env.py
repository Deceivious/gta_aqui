import os
import json

ROOT = os.path.dirname(os.path.dirname(__file__))

with open(os.path.join(ROOT, "env.json"), "r") as file:
    data = json.load(file)

IP_ADDRESS = data["IP_ADDRESS"]
PORT = data["PORT"]
SECRET_KEY = data["SECRET_KEY"]
ADMIN_USER = data["ADMIN_USER"]
ADMIN_PASS = data["ADMIN_PASS"]
