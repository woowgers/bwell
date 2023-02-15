from werkzeug.local import LocalProxy
from flask import current_app, g, abort, session

from db import *
from db.models import *

import typing as t


def get_db_proxy() -> DBCursor:
    if "db" not in g:
        try:
            g.db = get_db(**current_app.config["DATABASE"])
        except DBError:
            abort(503)

    return g.db


def get_user_proxy() -> t.Optional[User]:
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
        try:
            commit_db(db)
        except DBError:
            pass
        close_db(db)


db: DBCursor = LocalProxy(get_db_proxy)  # type: ignore[Assignment]
user: User = LocalProxy(get_user_proxy)  # type: ignore[Assignment]
