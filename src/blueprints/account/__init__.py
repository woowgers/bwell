from flask import Blueprint, render_template, redirect, url_for, request, abort

from db import *
from helpers.flashes import *
from helpers.authority import *
from proxies import db, user

from forms import Form


bp = Blueprint(
    "account",
    __name__,
    url_prefix="/account",
    template_folder="templates",
    static_folder="static",
)


@bp.get("/")
@login_required
def my():
    logout_form = Form(action=url_for("auth.do_logout"), submit_value="Log Out")
    delete_form = Form(action=url_for("account.delete_my", user_id=user.user_id), submit_value="Delete Account")
    return render_template("account.j2", logout_form=logout_form, delete_form=delete_form)


@bp.get("/all")
@admin_rights_required
def all():
    def delete_form(user_id: int) -> Form:
        return Form(submit_value="Delete", action=url_for("account.delete", user_id=user_id))

    users = db_get_users(db)
    return render_template("accounts.j2", users=users, delete_form=delete_form)


@bp.post("/delete/<int:user_id>")
@admin_rights_required
def delete(user_id: int):
    if user_id == user.user_id and request.referrer != url_for(
        "account.my", _external=True
    ):
        flash_info("You can only delete your account via personal account page.")
        return redirect(request.referrer)

    try:
        with ModelWebUIContext():
            db_delete_user(db, user_id)
    except (DBUsageError, ModelError):
        return redirect(request.referrer)

    return redirect(url_for("account.all"), code=307)


@bp.post("/delete_my/<int:user_id>")
@login_required
def delete_my(user_id: int):
    if user_id != user.user_id:
        abort(
            406,
            f'You are not allowed to delete this user'
        )

    try:
        with ModelWebUIContext():
            db_delete_user(db, user_id)
    except (DBUsageError, ModelError):
        return redirect(request.referrer)

    return redirect(url_for("auth.do_logout"), code=307)
