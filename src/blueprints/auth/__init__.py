from flask import Blueprint, render_template, redirect, url_for, request, session
from flask_bcrypt import generate_password_hash, check_password_hash

from db import *
from db.models import *
from proxies import db, user
from helpers.flashes import *

from forms import LoginForm, RegisterForm


bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
    template_folder="templates",
    static_folder="static",
)


@bp.route("/")
def read():
    return redirect(url_for("auth.login"))


@bp.route("/register")
def register():
    return render_template("register.j2")


@bp.get("/login")
def login():
    return render_template("login.j2")


@bp.post("/register")
def do_register():
    form = RegisterForm(request.form.to_dict())

    if not form.is_valid:
        return redirect(request.url)

    pw_hash = generate_password_hash(form.password)

    try:
        db_add_user(db, form.user_type, form.email, form.username, pw_hash)
    except ModelError as error:
        flash_error(f"User with given email already exists.")
        flash_error(f"Unexpected model error: {error}.")
        return redirect(request.referrer)

    flash_success("You have successfully registered a new user")
    if not user:
        return redirect(url_for("auth.login"))
    else:
        return redirect(url_for("auth.register"))


@bp.post("/login")
def do_login():
    form = LoginForm(request.form.to_dict())
    if not form.is_valid:
        return redirect(request.url)

    try:
        user = db_get_user_by_email(db, form.email)
    except ModelError as error:
        flash_error(error)
        return redirect(request.url)

    if not check_password_hash(user.pw_hash, form.password):
        flash_error("Invalid password.")
        return redirect(request.url)

    session["user"] = user
    return redirect(url_for("account.read"))
