from db import *

from .manufacturer import *


def db_get_drug_groups(db: DBCursor) -> tuple[DrugGroup]:
    SQL_QUERY = """
        SELECT
            drug_group_id,
            name
        FROM drug_group
    """
    drug_group_tuples = db_execute(db, SQL_QUERY)
    return tuple(DrugGroup(*dg_tuple) for dg_tuple in drug_group_tuples)


def db_get_drug_group_by_name_create_if_not_exists(
    db: DBCursor, drug_group_name
) -> DrugGroup:
    drug_group_tuple = db_callproc(
        db, "get_drug_group_create_if_not_exists", (None, drug_group_name)
    )
    return DrugGroup(*drug_group_tuple)


def db_get_drugs(db: DBCursor) -> tuple[Drug]:
    SQL_QUERY = """
        SELECT
            drug.drug_id,
            drug_group.drug_group_id,
            drug_group.name,
            drug.cipher,
            drug.name,
            manufacturer.manufacturer_id,
            country.country_id,
            country.name,
            manufacturer.name
        FROM
            drug
            JOIN drug_group USING (drug_group_id)
            JOIN manufacturer USING (manufacturer_id)
            JOIN country USING (country_id)
    """
    drug_tuples = db_execute(db, SQL_QUERY)
    return tuple(Drug.from_primitives(*drug_tuple) for drug_tuple in drug_tuples)


def db_get_drug_names(db: DBCursor) -> tuple[str]:
    SQL_QUERY = """
        SELECT DISTINCT name
        FROM drug
    """
    return tuple(drug_name_tuple[0] for drug_name_tuple in db_execute(db, SQL_QUERY))


def db_add_drug(db: DBCursor, mf_id, drug_cipher, drug_group_name, drug_name) -> None:
    SQL_QUERY = """
        INSERT INTO drug (drug_group_id, cipher, name, manufacturer_id)
        VALUES (%s, %s, %s, %s)
    """
    manufacturer = db_get_manufacturer(db, mf_id)
    drug_group = db_get_drug_group_by_name_create_if_not_exists(db, drug_group_name)
    db_execute(
        db,
        SQL_QUERY,
        (
            drug_group.drug_group_id,
            drug_cipher,
            drug_name,
            manufacturer.manufacturer_id,
        ),
    )


def db_delete_drug(db: DBCursor, drug_id) -> None:
    SQL_QUERY = """
        DELETE FROM drug WHERE drug_id = %s
    """
    try:
        db_execute(db, SQL_QUERY, (drug_id,))
    except DBIntegrityError:
        raise ModelError(
            f"Could not delete specified drug because there are vendor items comprising this drug."
        )
