from flask import Blueprint, render_template, redirect, url_for, request, session
from flask_bcrypt import generate_password_hash, check_password_hash

from db import *
from db.models import *
from proxies import db, user
from helpers.flashes import *

from helpers.authority import login_required
from forms import LoginForm, RegisterForm


bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
    template_folder="templates",
    static_folder="static",
)


@bp.route("/")
def root():
    return redirect(url_for("auth.login"))


@bp.route("/register")
def register():
    form = RegisterForm(action=url_for("auth.do_register"))
    return render_template("register.j2", register_form=form)


@bp.get("/login")
def login():
    form = LoginForm(action=url_for("auth.do_login"), submit_value="Log In")
    return render_template("login.j2", login_form=form)


@bp.post("/logout")
@login_required
def do_logout():
    session.clear()
    return redirect(url_for("root"))


@bp.post("/register")
def do_register():
    form = RegisterForm(fields_dict=request.form.to_dict())
    if not form.is_valid:
        return redirect(request.url)

    pw_hash = generate_password_hash(form.password)
    try:
        with ModelWebUIContext():
            db_add_user(db, form.user_type, form.email, form.username, pw_hash)
    except (ModelError, DBUsageError):
        return redirect(request.referrer)

    flash_success("You have successfully registered a new user")

    if not user:
        return redirect(url_for("auth.login"))

    return redirect(url_for("auth.register"))


@bp.post("/login")
def do_login():
    user = None
    form = LoginForm(fields_dict=request.form.to_dict())
    if not form.is_valid:
        return redirect(request.url)

    try:
        with ModelWebUIContext():
            user = db_get_user_by_email(db, form.email)
    except (ModelError, DBUsageError):
        return redirect(request.url)

    if not check_password_hash(user.pw_hash, form.password):
        flash_error("Invalid password.")
        return redirect(request.url)

    session["user"] = user
    return redirect(url_for("account.my"))

