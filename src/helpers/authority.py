from flask import redirect, url_for

from proxies import user
from .flashes import flash_error

from functools import wraps
import typing as t


ViewHandler = t.Callable


def login_required(view: ViewHandler) -> ViewHandler:
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not user:
            flash_error(f"You have to log in to perform this operation.")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapper


def admin_rights_required(view: ViewHandler) -> ViewHandler:
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not user or not user.is_admin:
            flash_error(f"Only administrator has rights for this operation")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapper
