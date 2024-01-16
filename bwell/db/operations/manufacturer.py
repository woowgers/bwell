from bwell.db import *


def db_get_countries(db: DBCursor) -> tuple[Country]:
    SQL_QUERY = """
        SELECT
            country_id,
            name
        FROM country
    """
    return tuple(Country(*country_tuple) for country_tuple in db_execute(db, SQL_QUERY))


def db_get_country_by_name_create_if_not_exists(db: DBCursor, country_name) -> Country:
    country_tuple = db_callproc(
        db, "get_country_create_if_not_exists", (None, country_name)
    )
    return Country(*country_tuple)


def db_get_manufacturers(db: DBCursor) -> tuple[Manufacturer]:
    SQL_QUERY = """
        SELECT
            manufacturer.manufacturer_id,
            country.country_id,
            country.name,
            manufacturer.name
        FROM manufacturer JOIN country USING (country_id)
    """
    mf_tuples = db_execute(db, SQL_QUERY)
    return tuple(Manufacturer.from_primitives(*mf_tuple) for mf_tuple in mf_tuples)


def db_get_manufacturer(db: DBCursor, mf_id) -> Manufacturer:
    SQL_QUERY = """
        SELECT
            manufacturer.manufacturer_id,
            country.country_id,
            country.name,
            manufacturer.name
        FROM
            manufacturer
            JOIN country USING (country_id)
        WHERE manufacturer.manufacturer_id = %s
    """
    mf_tuples = db_execute(db, SQL_QUERY, (mf_id,))
    if not mf_tuples:
        raise ModelError(f"Manufacturer with ID={mf_id} does not exist.")
    return Manufacturer.from_primitives(*mf_tuples[0])


def db_get_manufacturer_companies(db: DBCursor) -> tuple[str]:
    SQL_QUERY = """
        SELECT name
        FROM manufacturer
    """
    return tuple(company_tuple[0] for company_tuple in db_execute(db, SQL_QUERY))


def db_get_manufacturer_by_name(db: DBCursor, mf_name) -> Manufacturer:
    SQL_QUERY = """
        SELECT
            manufacturer.manufacturer_id,
            country.country_id,
            country.name,
            manufacturer.name
        FROM manufacturer JOIN country USING (country_id)
        WHERE manufacturer.name = %s
    """
    mf_tuples = db_execute(db, SQL_QUERY, (mf_name,))
    if not mf_tuples:
        raise ModelError("Manufacturer with given company name does not exist.")
    return Manufacturer.from_primitives(*mf_tuples[0])


def db_add_manufacturer(db: DBCursor, country_name, company_name) -> None:
    SQL_QUERY = """
        INSERT INTO manufacturer (country_id, name) VALUES (%s, %s)
    """

    companies = db_get_manufacturer_companies(db)
    if company_name in companies:
        raise ModelError("Manufacturer with given company name already exists.")

    country = db_get_country_by_name_create_if_not_exists(db, country_name)
    db_execute(db, SQL_QUERY, (country.country_id, company_name))


def db_delete_manufacturer(db: DBCursor, mf_id) -> None:
    SQL_QUERY = """
        DELETE FROM manufacturer
        WHERE manufacturer_id = %s
    """

    try:
        db_execute(db, SQL_QUERY, (mf_id,))
    except DBIntegrityError:
        raise ModelError(
            f"Could not delete manufacturer with ID={mf_id} because there are drugs in the system manufactured by it."
        )
