from flask import Flask, render_template, redirect, request, session
from server.firewall_helper import delete_all_rules, update_rules
from server.users_module import create_user, check_user, get_token, get_approval_list, set_permission, check_token, \
    bind_ip_to_user, get_users, delete_user
from server.env import ADMIN_USER, ADMIN_PASS, IP_ADDRESS, PORT, ROOT, SECRET_KEY
from server.exceptions import UserExists, NotPermitted, UserDoesnotExist
import os
from functools import wraps

app = Flask("__name__")
app.template_folder = os.path.join(ROOT, 'server', 'templates')
app.secret_key = SECRET_KEY


def is_admin(fxn,*args,**kargs):
    """ Allows only admin users to access the function. """

    @wraps(fxn)
    def inner(*args,**kargs):
        if session["username"] != ADMIN_USER:
            return redirect("/")
        return fxn(*args,**kargs)

    return inner


@app.route("/", methods=["GET"])
def login():
    """ Entry point for log in page. """

    # Redirection for logged in users
    if "username" in session:
        if session["username"] == ADMIN_USER:
            # Admins are redirected to listing page
            return redirect("/list")
        try:
            # Approved users are shown their token
            token = get_token(session["username"])
            return f"<a href='/logout'>Logout</a><br>Your Token is <br><input style='width:100%;' disabled value='{token}'>"
        except NotPermitted:
            # Non approved users are displyed message
            return "Wait for approval.<a href='/logout'>LogOut</a>"
    return render_template("login.html")


@is_admin
@app.route("/approve", methods=["GET"])
@is_admin
def approve():
    """ Display page for approval list. """

    # Get username that needs approval
    approval_list = get_approval_list()

    # Generate Option string for HTML
    approval_list = [f"<option value='{i}'>{i}</option>" for i in approval_list]

    # Return HTML
    return f"<form taget='/approve' method='POST'><select name='username'>{approval_list}</select><input type='submit'></form>"


@app.route("/approve", methods=["POST"])
@is_admin
def approve_post():
    """ Approves selected user. """
    user = dict(request.form)["username"]
    set_permission(user)
    return redirect("/approve")


@app.route("/", methods=["POST"])
def login_post():
    """ Username and password check for login. """
    user_data = dict(request.form)

    # Handle login data
    if user_data["btn"] == 'login':

        # Redirect admin users to list page
        if user_data["username"] == ADMIN_USER and user_data["password"] == ADMIN_PASS:
            session["username"] = ADMIN_USER
            return redirect("/list")

        # Display token for verified users
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

    # Handle sign up data
    elif user_data["btn"] == 'signup':
        try:
            create_user(user_data["username"], user_data["password"])
        except UserExists:
            return "User exists."
        return "Wait for approval.<a href='/logout'>LogOut</a>"


@app.route("/register_ip", methods=["POST"])
def register_ip():
    """ Register new IP for user. """
    data = request.json
    token = data["token"]
    user = data["username"]
    if not check_token(user, token):
        return "Your token is invalid."
    remote_ip = request.environ['REMOTE_ADDR']
    bind_ip_to_user(user, remote_ip)

    # Reset firewall rules
    delete_all_rules()
    update_rules()
    return f"You have registered with IP : {remote_ip}."


@app.route("/logout")
def logout():
    """ Removes user out of session. """
    if "username" in session:
        del session["username"]
    return redirect("/")


@app.route("/list", methods=["GET"])
@is_admin
def root_get():
    """ Fetches list of verified users. """
    list_data = get_users()
    return render_template("index.html", list_data=list_data, server_ip=f"http://{IP_ADDRESS}:{PORT}")


@app.route("/delete/<rule_name>", methods=["GET"])
@is_admin
def delete_rule_entry(rule_name):
    """ Deletes user data. """
    delete_user(rule_name)

    # Reset firewall rules
    delete_all_rules()
    update_rules()
    return redirect("/list")


@app.route("/add", methods=["GET"])
@is_admin
def add_user_get():
    """ Display add rules UI. """
    return render_template("add_rule.html")


@app.route("/stop", methods=["GET"])
@is_admin
def stop_session():
    """ Deletes all rules. """
    delete_all_rules()
    return "Session Stopped"

@app.route("/reset",methods=["GET"])
@is_admin
def reset_rules():
    """ Restarts the rules. """
    delete_all_rules()
    update_rules()
    return "Session Reset"
