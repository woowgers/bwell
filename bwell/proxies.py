import contextlib
import typing as t

from flask import abort, current_app, g, session
from werkzeug.local import LocalProxy

from bwell.db import *
from bwell.db.models import *


def get_db_proxy() -> DBCursor:
    if "db" not in g:
        try:
            g.db = get_db(**current_app.config["DATABASE"])
        except DBError:
            abort(503)

    return g.db


def get_user_proxy() -> User | None:
    if "user" not in g:
        user_dict = session.get("user")
        if not user_dict:
            g.user = None
        else:
            g.user = User(**user_dict)

    return g.user


def close_db_proxy(_=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        with contextlib.suppress(DBError):
            commit_db(db)
        close_db(db)


db: DBCursor = t.cast(DBCursor, LocalProxy(get_db_proxy))
user: User = t.cast(User, LocalProxy(get_user_proxy))
