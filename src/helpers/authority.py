from flask import redirect, url_for

from proxies import user
from .flashes import flash_error

from functools import wraps
import typing as t


ViewHandler = t.Callable


def login_required(handler: ViewHandler) -> ViewHandler:
    @wraps(handler)
    def wrapper(*args, **kwargs):
        if not user:
            flash_error(f"You have to log in to perform this operation.")
            return redirect(url_for("auth.login"))
        return handler(*args, **kwargs)

    return wrapper


def admin_rights_required(handler: ViewHandler) -> ViewHandler:
    @wraps(handler)
    def wrapper(*args, **kwargs):
        if not user or not user.is_admin:
            flash_error(f"Only administrator has rights for this operation.")
            return redirect(url_for("auth.login"))
        return handler(*args, **kwargs)

    return wrapper


def cashier_rights_required(handler: ViewHandler) -> ViewHandler:
    @wraps(handler)
    def wrapper(*args, **kwargs):
        if not user or not (user.is_admin or user.is_cashier):
            flash_error(f"This operation requires at least cashier's rights.")
            return redirect(url_for("auth.login"))
        return handler(*args, **kwargs)

    return wrapper

