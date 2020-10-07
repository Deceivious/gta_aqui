import requests as r

import json
import os
from time import sleep


def register_ip():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if not os.path.exists(config_path):
        server_ip = input("Enter Server IP:")
        user = input("Enter your username:")
        token = input("Enter your token:")
        with open(config_path, "w") as file:
            json.dump({"ip": server_ip, "username": user, "token": token}, file)

    with open(config_path, "r") as file:
        data = json.load(file)
    url = data["ip"]
    del data["ip"]
    # data["remoteip"] = r.get('https://api.ipify.org').text
    res = r.post(url + "/register_ip", json=data)
    print(res.content + "\nThe application will close in 5 seconds.")
    sleep(5)
    exit()


if __name__ == "__main__":
    register_ip()
