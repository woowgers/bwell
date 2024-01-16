from flask import (
    Blueprint,
    abort,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_bcrypt import check_password_hash, generate_password_hash

from bwell.db import *
from bwell.db.models import *
from bwell.forms.forms import Form, LoginForm, RegisterForm
from bwell.helpers.authority import *
from bwell.helpers.authority import login_required
from bwell.helpers.flashes import *
from bwell.proxies import db, user

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


@bp.get("/")
@login_required
def my():
    logout_form = Form(action=url_for("auth.do_logout"), submit_value="Log Out")
    delete_form = Form(
        action=url_for("auth.delete_my", user_id=user.user_id),
        submit_value="Delete Account",
    )
    return render_template(
        "account.j2",
        logout_form=logout_form,
        delete_form=delete_form,
    )


@bp.get("/all")
@admin_rights_required
def all():
    def delete_form(user_id: int) -> Form:
        return Form(
            submit_value="Delete",
            action=url_for("auth.delete", user_id=user_id),
        )

    users = db_get_users(db)
    return render_template("accounts.j2", users=users, delete_form=delete_form)


@bp.post("/delete/<int:user_id>")
@admin_rights_required
def delete(user_id: int):
    if user_id == user.user_id and request.referrer != url_for(
        "account.my",
        _external=True,
    ):
        flash_info(
            "You can only delete your account via personal account page.",
        )
        return redirect(request.referrer)

    try:
        with ModelWebUIContext():
            db_delete_user(db, user_id)
    except (DBUsageError, ModelError):
        return redirect(request.referrer)

    return redirect(url_for("account."), code=307)


@bp.post("/delete_my/<int:user_id>")
@login_required
def delete_my(user_id: int):
    if user_id != user.user_id:
        abort(406, "You are not allowed to delete this user")

    try:
        with ModelWebUIContext():
            db_delete_user(db, user_id)
    except (DBUsageError, ModelError):
        return redirect(request.referrer)

    return redirect(url_for("auth.do_logout"), code=307)
