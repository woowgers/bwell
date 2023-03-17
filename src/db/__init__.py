from flask import flash
import psycopg2
import psycopg2._psycopg

from .models import *

import typing as t


DBError = psycopg2.Error
DBIntegrityError = psycopg2.IntegrityError
DBOperationalError = psycopg2.OperationalError
DBProgrammingError = psycopg2.ProgrammingError
DBInterfaceError = psycopg2.InterfaceError
DBInternalError = psycopg2.InternalError

DBConnection = psycopg2._psycopg.connection
DBCursor = psycopg2._psycopg.cursor


ModelError = DBIntegrityError
DBUsageError = DBError


class DefaultModelError(ModelError):
    def __init__(self, error: DBIntegrityError):
        super().__init__(f"Unexpected database error: {error}.")


global __connection
__connection: DBConnection


def get_db(**config) -> DBCursor:
    global __connection
    __connection = psycopg2.connect(**config)
    return __connection.cursor()


def commit_db(db: DBCursor) -> None:  # pyright: ignore
    __connection.commit()


def close_db(db: DBCursor) -> None:  # pyright: ignore
    __connection.close()


def db_execute(
    db: DBCursor, statement: str, params: tuple = (), **kwargs
) -> t.Sequence:
    try:
        db.execute(statement, params, **kwargs)
    except (
        DBOperationalError,
        DBProgrammingError,
        DBInterfaceError,
        DBInternalError,
    ) as error:
        raise DBUsageError(error)

    try:
        return db.fetchall()
    except DBError:
        return ()


def db_executemany(
    db: DBCursor, statement: str, params_tuples: t.Sequence[tuple] = (), **kwargs
) -> None:
    try:
        db.executemany(statement, params_tuples, **kwargs)
    except (
        DBOperationalError,
        DBProgrammingError,
        DBInterfaceError,
        DBInternalError,
    ) as error:
        raise DBUsageError(error)


def db_callproc(
    db: DBCursor, procedure: str, params: tuple = (), **kwargs
) -> t.Sequence:
    try:
        out_args = db.callproc(procedure, params, **kwargs)
        if isinstance(out_args, dict):
            return tuple(out_args.values())
        if isinstance(out_args, tuple):
            return out_args
    except (
        DBOperationalError,
        DBProgrammingError,
        DBInterfaceError,
        DBInternalError,
    ) as error:
        raise DBUsageError(error)

    return ()


class ModelWebUIContext:
    def __enter__(self) -> None:
        pass

    def __exit__(self, exc_type, exc_val, _) -> bool | None:
        if exc_type in (ModelError, DBUsageError):
            flash(str(exc_val), category="error")
            return True


from .operations.manufacturer import *
from .operations.drug import *
from .operations.user import *
from .operations.vendor import *

from .operations.vendor_item import *
from .operations.pharmacy_item import *

from .operations.admin_cart import *
from .operations.customer_cart import *
