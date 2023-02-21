from flask import Blueprint, render_template, redirect, url_for, session, request, abort

from db import *
from helpers.flashes import *
from helpers.authority import *
from proxies import db, user


bp = Blueprint(
    "account",
    __name__,
    url_prefix="/account",
    template_folder="templates",
    static_folder="static",
)


@bp.get("/")
@login_required
def read():
    return render_template("account.j2")


@bp.post("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("read"))


@bp.get("/accounts")
@admin_rights_required
def accounts():
    users = db_get_users(db)
    return render_template("accounts.j2", users=users)


@bp.post("/delete_account/<int:user_id>")
@admin_rights_required
def delete_account(user_id: int):
    if user_id == user.user_id and request.referrer != url_for('account.read', _external=True):
        flash_info("You can only delete your account via personal account page.")
        return redirect(request.referrer)
    else:
        try:
            db_delete_user(db, user_id)
        except ModelError as error:
            flash_error(error)
            return redirect(request.referrer)

    return redirect(url_for('account.logout'), code=307)


@bp.post("/delete_my_account/<int:user_id>")
@login_required
def delete_my_account(user_id: int):
    if user_id != user.user_id:
        abort(503)

    try:
        db_delete_user(db, user_id)
    except ModelError as error:
        flash_error(error)
        return redirect(request.referrer)

    return redirect(url_for("account.logout"), code=307)
