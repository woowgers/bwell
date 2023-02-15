from flask import flash
import mysql.connector
import mysql.connector.cursor

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
    db: DBCursor, statement: str, params: t.Sequence = (), **kwargs
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


def db_callproc(
    db: DBCursor, procedure: str, params: t.Sequence = (), **kwargs
) -> t.Sequence:
    try:
        db.callproc(procedure, params, **kwargs)
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


def db_get_users(db: DBCursor) -> t.Sequence[User]:
    SQL_QUERY = "SELECT user_id, email, user_type, name, pw_hash FROM user"
    return tuple(User(*user_tuple) for user_tuple in db_execute(db, SQL_QUERY))


def db_get_user_by_email(db: DBCursor, email) -> t.Optional[User]:
    SQL_QUERY = """
        SELECT user_id, email, user_type, name, pw_hash
        FROM user WHERE email = %s
    """
    user_tuples = db_execute(db, SQL_QUERY, (email,))
    if not user_tuples:
        return None
    return User(*(user_tuples[0]))


def db_add_user(db: DBCursor, user_type, email, username, pw_hash):
    SQL_QUERY = """
        INSERT INTO user (user_type, email, name, pw_hash)
        VALUE (%s, %s, %s, %s)
    """
    db_execute(db, SQL_QUERY, (user_type, email, username, pw_hash))


def db_delete_user(db: DBCursor, user_id: int) -> None:
    db_callproc(db, "user_delete", (user_id,))


def db_get_countries(db: DBCursor) -> t.Sequence[Country]:
    SQL_QUERY = "SELECT country.country_id, country.name FROM country"
    return tuple(Country(*country_tuple) for country_tuple in db_execute(db, SQL_QUERY))


def db_get_cities(db: DBCursor) -> t.Sequence[City]:
    SQL_QUERY = "SELECT city.city_id, city.name FROM city"
    return tuple(City(*city_tuple) for city_tuple in db_execute(db, SQL_QUERY))


def db_add_manufacturer(db: DBCursor, company_name, country_name) -> None:
    db_callproc(db, "manufacturer_add", (company_name, country_name))


def db_delete_manufacturer(db: DBCursor, mf_id) -> None:
    db_callproc(db, "manufacturer_delete", (mf_id,))


def db_get_manufacturers(db: DBCursor) -> t.Sequence[Manufacturer]:
    SQL_QUERY = """
        SELECT
            manufacturer.manufacturer_id,
            country.name,
            manufacturer.name
        FROM manufacturer JOIN country USING (country_id)
    """
    mf_tuples = db_execute(db, SQL_QUERY)
    return tuple(Manufacturer(*mf_tuple) for mf_tuple in mf_tuples)


def db_get_manufacturer_by_name(db: DBCursor, mf_name) -> t.Optional[Manufacturer]:
    SQL_QUERY = """
        SELECT
            manufacturer.manufacturer_id,
            country.name,
            manufacturer.name
        FROM manufacturer JOIN country USING (country_id)
        WHERE manufacturer.name = %s
    """
    mf_tuples = db_execute(db, SQL_QUERY, (mf_name,))
    if not mf_tuples:
        return None
    return Manufacturer(*mf_tuples[0])


def db_add_vendor(
    db: DBCursor, cipher, company_name, city_name, conclusion_date
) -> Vendor:
    try:
        vendor_tuples = db_callproc(
            db, "vendor_add", (cipher, company_name, city_name, conclusion_date)
        )
        return Vendor(*vendor_tuples[0])
    except DBIntegrityError as error:
        if not error.msg:
            raise ModelError(f"Unexpected database error: {error}")
        if error.msg and error.msg.find("cipher") >= 0:
            raise ModelError("Vendor with given cipher already exists.")
        if error.msg and error.msg.find("company_name") >= 0:
            raise ModelError("Vendor with given company name already exists.")
        raise error


def db_delete_vendor(db: DBCursor, vendor_id):
    vendor = db_get_vendor(db, vendor_id)
    if not vendor:
        raise ModelError("Vendor with given ID does not exist.")
    if not vendor.termination_date:
        raise ModelError("Agreement with given vendor is not terminated yet.")

    db_callproc(db, "vendor_delete", (vendor_id,))


def db_get_vendor(db: DBCursor, vendor_id) -> Vendor:
    SQL_QUERY = """
        SELECT
            vendor.vendor_id,
            vendor.cipher,
            vendor.company_name,
            city.name,
            vendor.conclusion_date,
            vendor.termination_date
        FROM
            vendor
            JOIN city USING (city_id)
        WHERE vendor_id = %s
    """
    vendor_tuples = db_execute(db, SQL_QUERY, (vendor_id,))
    if not vendor_tuples:
        raise ModelError(f"Vendor with ID={vendor_id} does not exist.")

    return Vendor(*vendor_tuples[0])


def db_get_vendors(db: DBCursor) -> t.Sequence[Vendor]:
    SQL_QUERY = """
        SELECT
            vendor.vendor_id,
            vendor.cipher,
            vendor.company_name,
            city.name,
            vendor.conclusion_date,
            vendor.termination_date
        FROM
            vendor
            JOIN city USING (city_id)
    """
    vendor_tuples = db_execute(db, SQL_QUERY)
    return tuple(Vendor(*vendor_tuple) for vendor_tuple in vendor_tuples)


def db_vendor_terminte_agreement(db: DBCursor, vendor_id, termination_date) -> None:
    SQL_QUERY = "UPDATE vendor SET termination_date = %s WHERE vendor_id = %s"

    vendor = db_get_vendor(db, vendor_id)
    if not vendor:
        raise ModelError("Vendor with given ID does not exist.")

    if vendor.termination_date:
        raise ModelError("Agreement with given vendor is already terminated.")

    db_execute(db, SQL_QUERY, (termination_date, vendor_id))


def db_get_drug_groups(db: DBCursor) -> t.Sequence[DrugGroup]:
    SQL_QUERY = "SELECT drug_group.drug_group_id, drug_group.name FROM drug_group"
    drug_group_tuples = db_execute(db, SQL_QUERY)
    return tuple(DrugGroup(*dg_tuple) for dg_tuple in drug_group_tuples)


def db_get_drugs(db: DBCursor) -> t.Sequence[Drug]:
    SQL_QUERY = """
        SELECT
            drug.drug_id,
            drug_group.name,
            drug.cipher,
            drug.name,
            manufacturer.name
        FROM
            drug
            JOIN drug_group USING (drug_group_id)
            JOIN manufacturer USING (manufacturer_id)
    """
    drug_tuples = db_execute(db, SQL_QUERY)
    return tuple(Drug(*drug_tuple) for drug_tuple in drug_tuples)


def db_add_drug(db: DBCursor, mf_id, drug_cipher, drug_group_name, drug_name):
    db_callproc(db, "drug_add", (mf_id, drug_cipher, drug_group_name, drug_name))


def db_get_drug_names(db: DBCursor) -> t.Sequence[str]:
    SQL_QUERY = "SELECT DISTINCT name FROM drug"
    return tuple(drug_name_tuple[0] for drug_name_tuple in db_execute(db, SQL_QUERY))


def db_get_vendor_items(db: DBCursor, vendor_id) -> t.Sequence[Item]:
    SQL_QUERY = """
        SELECT
            vendor_item.item_id,
            vendor_item.drug_id,
            drug_group.name,
            drug.cipher,
            drug.name,
            manufacturer.name,
            vendor_item.price
        FROM
            vendor_item
            JOIN drug USING (drug_id)
            JOIN drug_group USING (drug_group_id)
            JOIN manufacturer USING (manufacturer_id)
        WHERE vendor_id = %s
    """
    return tuple(
        Item(*item_tuple) for item_tuple in db_execute(db, SQL_QUERY, (vendor_id,))
    )


def db_get_vendor_storefront_items(db: DBCursor, vendor_id) -> t.Sequence[ItemAmount]:
    SQL_QUERY = """
        SELECT
            vendor_has_item.item_id,
            vendor_item.drug_id,
            drug_group.name,
            drug.cipher,
            drug.name,
            manufacturer.name,
            vendor_item.price,
            vendor_has_item.amount
        FROM
            vendor_has_item
            JOIN vendor_item USING (item_id)
            JOIN drug USING (drug_id)
            JOIN drug_group USING (drug_group_id)
            JOIN manufacturer USING (manufacturer_id)
        WHERE vendor_has_item.vendor_id = %s
    """
    return tuple(
        ItemAmount(*item_tuple)
        for item_tuple in db_execute(db, SQL_QUERY, (vendor_id,))
    )


def db_add_vendor_item(db: DBCursor, vendor_id, drug_id, price):
    SQL_QUERY = """
        INSERT INTO vendor_item (vendor_id, drug_id, price)
        VALUE (%s, %s, %s)
    """
    db_execute(db, SQL_QUERY, (vendor_id, drug_id, price))


def db_add_vendor_storefront_item(db: DBCursor, vendor_id, item_id, amount):
    SQL_QUERY = """
        INSERT INTO vendor_has_item (vendor_id, item_id, amount)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE amount = amount + %s
    """
    db_execute(db, SQL_QUERY, (vendor_id, item_id, amount, int(amount)))


def db_delete_vendor_storefront_item(db: DBCursor, vendor_id, item_id):
    SQL_QUERY = """
        DELETE FROM vendor_has_item
        WHERE vendor_id = %s AND item_id = %s
    """
    db_execute(db, SQL_QUERY, (vendor_id, item_id))


def db_delete_vendor_item(db: DBCursor, item_id):
    SQL_QUERY = "DELETE FROM vendor_item WHERE item_id = %s"
    db_execute(db, SQL_QUERY, (item_id,))


def db_get_pharmacy_items(db: DBCursor) -> t.Sequence[Item]:
    SQL_QUERY = """
        SELECT
            pharmacy_has_item.item_id,
            pharmacy_item.drug_id,
            drug_group.name,
            drug.cipher,
            drug.name,
            manufacturer.name,
            pharmacy_item.price,
            pharmacy_has_item.amount
        FROM
            pharmacy_has_item
            JOIN pharmacy_item USING (item_id)
            JOIN drug USING (drug_id)
            JOIN drug_group USING (drug_group_id)
    """
    return tuple(Item(*item_tuple) for item_tuple in db_execute(db, SQL_QUERY))


def db_get_admin_cart_items(db: DBCursor, user_id) -> t.Sequence[Item]:
    SQL_QUERY = """
        SELECT
            admin_cart_has_item.item_id,
            drug.drug_id,
            drug_group.name,
            drug.cipher,
            drug.name,
            manufacturer.name,
            vendor_item.price,
            admin_cart_has_item.amount
        FROM
            admin_cart_has_item
            JOIN vendor_item USING (item_id)
            JOIN drug USING (drug_id)
            JOIN drug_group USING (drug_group_id)
            JOIN manufacturer USING (manufacturer_id)
        WHERE admin_cart_has_item.user_id = %s
    """
    return tuple(
        Item(*item_tuple) for item_tuple in db_execute(db, SQL_QUERY, (user_id,))
    )


def db_add_item_to_admin_cart(db: DBCursor, user_id, item_id, amount) -> None:
    SQL_QUERY = """
        INSERT INTO admin_cart_has_item (user_id, item_id, amount)
        VALUE (%s, %s, %s)
    """
    db_execute(db, SQL_QUERY, (user_id, item_id, amount))


def db_get_customer_cart_items(db: DBCursor, user_id) -> t.Sequence[Item]:
    SQL_QUERY = """
        SELECT
            customer_cart_has_item.item_id,
            drug.drug_id,
            drug_group.name,
            drug.cipher,
            drug.name,
            manufacturer.name,
            pharmacy_item.price,
            customer_cart_has_item.amount
        FROM
            customer_cart_has_item
            JOIN pharmacy_item USING (item_id)
            JOIN drug USING (drug_id)
            JOIN drug_group USING (drug_group_id)
            JOIN manufacturer USING (manufacturer_id)
        WHERE customer_cart_has_item.user_id = %s
    """
    return tuple(
        Item(*item_tuple) for item_tuple in db_execute(db, SQL_QUERY, (user_id,))
    )
