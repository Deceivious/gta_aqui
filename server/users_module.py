import string
import random
import hashlib
import os
import json
from server.exceptions import UserExists, NotPermitted, UserDoesnotExist
from server.env import ROOT, ADMIN_USER, ADMIN_PASS

user_file_path = os.path.join(ROOT, "userdata")
os.makedirs(user_file_path, exist_ok=True)


def get_hash(password):
    return hashlib.sha224(password.encode()).hexdigest()


def create_user(username, password):
    if username == ADMIN_USER:
        raise Exception("User name exists.")
    user_path = os.path.join(user_file_path, username + ".json")
    if os.path.exists(user_path):
        raise UserExists()
    else:
        with open(user_path, "w") as file:
            key = get_hash(password)
            data = {"password": key, "permission": False, "token": None}
            json.dump(data, file)


def check_user(username, password):
    if username == ADMIN_USER and password == ADMIN_PASS:
        return True
    user_path = os.path.join(user_file_path, username + ".json")
    if not os.path.exists(user_path):
        raise UserDoesnotExist()
    else:
        with open(user_path, "r") as file:
            data = json.load(file)
    stored_key = data["password"]
    key = get_hash(password)
    if key == stored_key:
        return True
    else:
        raise Exception("Password error.")


def check_token(username, token):
    if username == ADMIN_USER and password == ADMIN_PASS:
        return True
    user_path = os.path.join(user_file_path, username + ".json")
    if not os.path.exists(user_path):
        raise UserDoesnotExist()
    else:
        with open(user_path, "r") as file:
            data = json.load(file)

    if token == data["token"]:
        return True
    else:
        raise Exception("Password error.")


def set_permission(username):
    if username == ADMIN_USER:
        return
    user_path = os.path.join(user_file_path, username + ".json")
    if not os.path.exists(user_path):
        raise Exception("User does not exist.")

    with open(user_path, "r") as file:
        data = json.load(file)
    data["token"] = ''.join((random.choice(string.ascii_letters + string.digits) for _ in range(47)))
    data["permission"] = True
    with open(user_path, "w") as file:
        json.dump(data, file)


def get_token(username):
    user_path = os.path.join(user_file_path, username + ".json")
    if not os.path.exists(user_path):
        raise UserDoesnotExist
    with open(user_path, "r") as file:
        data = json.load(file)
    if data["token"] is None:
        raise NotPermitted()
    return data["token"]


def get_approval_list():
    user_to_approve = []
    for user in os.listdir(user_file_path):
        with open(os.path.join(user_file_path, user), "r") as file:
            data = json.load(file)
        if not data["permission"]:
            user_to_approve.append(user.replace('.json', ''))
    return user_to_approve


def bind_ip_to_user(user, ip):
    user_file = os.path.join(user_file_path, user + ".json")
    with open(user_file, "r") as file:
        data = json.load(file)
    data["registered_ip"] = ip
    with open(user_file, "w") as file:
        json.dump(data, file)


def get_users():
    users = []
    for i in os.listdir(user_file_path):
        with open(os.path.join(user_file_path, i), "r") as file:
            data = json.load(file)
        registered_ip = data.get("registered_ip", None)
        username = i.replace(".json","")
        if registered_ip is not None:
            users.append({"username": username, "registered_ip": registered_ip,"Actions":f"<a href='/delete/{username}'>Delete</a>"})
    return users
