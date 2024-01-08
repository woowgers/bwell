import typing as t
from functools import wraps

from flask import redirect, url_for

from bwell.helpers.flashes import flash_error
from bwell.proxies import user

ViewHandler: t.TypeAlias = t.Callable


def login_required(handler: ViewHandler) -> ViewHandler:
    @wraps(handler)
    def wrapper(*args, **kwargs):
        if not user:
            flash_error("You have to log in to perform this operation.")
            return redirect(url_for("auth.login"))
        return handler(*args, **kwargs)

    return wrapper


def admin_rights_required(handler: ViewHandler) -> ViewHandler:
    @wraps(handler)
    def wrapper(*args, **kwargs):
        if not user or not user.is_admin:
            flash_error("Only administrator has rights for this operation.")
            return redirect(url_for("auth.login"))
        return handler(*args, **kwargs)

    return wrapper


def cashier_rights_required(handler: ViewHandler) -> ViewHandler:
    @wraps(handler)
    def wrapper(*args, **kwargs):
        if not user or not (user.is_admin or user.is_cashier):
            flash_error("This operation requires at least cashier's rights.")
            return redirect(url_for("auth.login"))
        return handler(*args, **kwargs)

    return wrapper
