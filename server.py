from flask import Flask, render_template, redirect, request, session
from server.firewall_helper import delete_all_rules, update_rules
from server.users_module import create_user, check_user, get_token, get_approval_list, set_permission, check_token, \
    bind_ip_to_user, get_users, delete_user
from server.env import ADMIN_USER, ADMIN_PASS, IP_ADDRESS, PORT, ROOT
from server.exceptions import UserExists, NotPermitted, UserDoesnotExist
import os
from functools import wraps

app = Flask("__name__")
app.template_folder = os.path.join(ROOT, 'server', 'templates')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


def is_admin(fxn):
    @wraps(fxn)
    def inner():
        if session["username"] != ADMIN_USER:
            return redirect("/")
        return fxn()

    return inner


@app.route("/", methods=["GET"])
def login():
    if "username" in session:
        if session["username"] == ADMIN_USER:
            return redirect("/list")
        try:
            token = get_token(session["username"])
            return f"<a href='/logout'>Logout</a><br>Your Token is <br><input style='width:100%;' disabled value='{token}'>"
        except NotPermitted:
            return "Wait for approval.<a href='/logout'>LogOut</a>"
    return render_template("login.html")


@is_admin
@app.route("/approve", methods=["GET"])
@is_admin
def approve():
    approval_list = get_approval_list()
    approval_list = [f"<option value='{i}'>{i}</option>" for i in approval_list]
    return f"<form taget='/approve' method='POST'><select name='username'>{approval_list}</select><input type='submit'></form>"


@app.route("/approve", methods=["POST"])
@is_admin
def approve_post():
    user = dict(request.form)["username"]
    set_permission(user)
    return redirect("/approve")


@app.route("/", methods=["POST"])
def login_post():
    user_data = dict(request.form)
    if user_data["btn"] == 'login':
        if user_data["username"] == ADMIN_USER and user_data["password"] == ADMIN_PASS:
            session["username"] = ADMIN_USER
            return redirect("/list")
        try:
            user_check = check_user(user_data["username"], user_data["password"])
        except UserDoesnotExist:
            return "User does not exist."
        if user_check:
            session["username"] = user_data["username"]
            try:
                token = get_token(user_data["username"])
                return f"<a href='/logout'>Logout</a><br>Your Token is <br><input style='width:100%;' disabled value='{token}'>"
            except NotPermitted:
                return "Wait for approval.<a href='/logout'>LogOut</a>"
    elif user_data["btn"] == 'signup':
        try:
            create_user(user_data["username"], user_data["password"])
        except UserExists:
            return "User exists."
        return "Wait for approval.<a href='/logout'>LogOut</a>"


@app.route("/register_ip", methods=["POST"])
def register_ip():
    data = request.json
    token = data["token"]
    user = data["username"]
    if not check_token(user, token):
        return "Your token is invalid."
    remote_ip = data["remoteip"]
    bind_ip_to_user(user, remote_ip)
    delete_all_rules()
    update_rules()
    return f"You have registered with IP : {remote_ip}."


@app.route("/logout")
def logout():
    if "username" in session:
        del session["username"]
    return redirect("/")


@app.route("/list", methods=["GET"])
@is_admin
def root_get():
    list_data = get_users()
    return render_template("index.html", list_data=list_data, server_ip=f"http://{IP_ADDRESS}:{PORT}")


@app.route("/delete/<rule_name>", methods=["GET"])
@is_admin
def delete_rule_entry(rule_name):
    delete_user(rule_name)
    delete_all_rules()
    update_rules()
    return redirect("/list")


@app.route("/add", methods=["GET"])
@is_admin
def add_user_get():
    return render_template("add_rule.html")


@app.route("/reset", methods=["GET"])
@is_admin
def stop_session():
    delete_all_rules()
    return "Session Reset"


if __name__ == "__main__":
    app.run(IP_ADDRESS, PORT, threaded=False)
