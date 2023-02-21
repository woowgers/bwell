from db import *


def db_get_cities(db: DBCursor) -> tuple[City]:
    SQL_QUERY = """
        SELECT city.city_id, city.name
        FROM city
    """
    return tuple(City(*city_tuple) for city_tuple in db_execute(db, SQL_QUERY))


def db_get_city_by_name_create_if_not_exists(db: DBCursor, city_name) -> City:
    country_tuple = db_callproc(
        db,
        "get_city_create_if_not_exists",
        (
            None,
            city_name,
        ),
    )
    return City(*country_tuple)


def db_get_vendors(db: DBCursor) -> tuple[Vendor]:
    SQL_QUERY = """
        SELECT
            vendor.vendor_id,
            vendor.cipher,
            vendor.company_name,
            city.city_id,
            city.name,
            vendor.conclusion_date,
            vendor.termination_date
        FROM
            vendor
            JOIN city USING (city_id)
    """
    vendor_tuples = db_execute(db, SQL_QUERY)
    return tuple(
        Vendor.from_primitives(*vendor_tuple) for vendor_tuple in vendor_tuples
    )


def db_get_vendor(db: DBCursor, vendor_id) -> Vendor:
    SQL_QUERY = """
        SELECT
            vendor.vendor_id,
            vendor.cipher,
            vendor.company_name,
            city.city_id,
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

    return Vendor.from_primitives(*vendor_tuples[0])


def db_add_vendor(
    db: DBCursor, cipher, company_name, city_name, conclusion_date
) -> None:
    SQL_QUERY = """
        INSERT INTO vendor (cipher, company_name, city_id, conclusion_date)
        VALUES (%s, %s, %s, %s)
    """

    city = db_get_city_by_name_create_if_not_exists(db, city_name)

    try:
        db_execute(db, SQL_QUERY, (cipher, company_name, city.city_id, conclusion_date))
    except DBIntegrityError as error:
        if not error.msg:
            raise DefaultModelError(error)
        if error.msg.find("cipher") >= 0:
            raise ModelError("Vendor with given cipher already exists.")
        if error.msg.find("company_name") >= 0:
            raise ModelError("Vendor with given company name already exists.")
        raise DefaultModelError(error)


def db_delete_vendor(db: DBCursor, vendor_id):
    SQL_QUERY = """
        DELETE FROM vendor
        WHERE vendor_id = %s
    """

    vendor = db_get_vendor(db, vendor_id)
    if not vendor:
        raise ModelError("Vendor with given ID does not exist.")
    if not vendor.termination_date:
        raise ModelError("Agreement with given vendor is not terminated yet.")

    try:
        db_execute(db, SQL_QUERY, (vendor_id,))
    except DBIntegrityError as error:
        if not error.msg:
            raise DefaultModelError(error)
        if error.msg.find("vendor_has_item") >= 0:
            raise ModelError(
                "Could not delete specified vendor because there are items of this vendor."
            )
        raise DefaultModelError(error)


def db_vendor_terminate_agreement(db: DBCursor, vendor_id, termination_date) -> None:
    SQL_QUERY = """
        UPDATE vendor
        SET termination_date = %s
        WHERE vendor_id = %s
    """

    vendor = db_get_vendor(db, vendor_id)
    if not vendor:
        raise ModelError("Vendor with given ID does not exist.")
    if vendor.termination_date:
        raise ModelError("Agreement with given vendor is already terminated.")
    if vendor.conclusion_date > termination_date:
        raise ModelError("Termination date must not be earlier than conclusion date.")

    db_execute(db, SQL_QUERY, (termination_date, vendor_id))
