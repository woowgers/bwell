from flask import flash
import mysql.connector
import mysql.connector.cursor
import mysql.connector.types

from .models import *

import typing as t


DBError = mysql.connector.Error
DBIntegrityError = mysql.connector.IntegrityError
DBOperationalError = mysql.connector.OperationalError
DBProgrammingError = mysql.connector.ProgrammingError
DBInterfaceError = mysql.connector.InterfaceError
DBInternalError = mysql.connector.InternalError

DBConnection = t.Union[
    mysql.connector.connection.MySQLConnection,
    mysql.connector.pooling.PooledMySQLConnection,
]
DBCursor = mysql.connector.cursor.MySQLCursor


ModelError = DBIntegrityError


class DefaultModelError(ModelError):
    def __init__(self, error: DBIntegrityError):
        return super().__init__(f"Unexpected database error: {error}.")


global __connection
__connection: DBConnection


def get_db(**config) -> DBCursor:
    global __connection
    __connection = mysql.connector.connect(**config)
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
        flash(f'Database usage error: "{error}".', category="error")

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
        flash(f'Database usage error: "{error}".', category="error")


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
        flash(f'Database usage error: "{error}".', category="error")

    return ()


from .operations.manufacturer import *
from .operations.drug import *
from .operations.user import *
from .operations.vendor import *

from .operations.vendor_item import *
from .operations.pharmacy_item import *

from .operations.admin_cart import *
from .operations.customer_cart import *
