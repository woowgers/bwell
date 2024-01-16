from bwell.db import *


def db_get_pharmacy_items(db: DBCursor) -> tuple[tuple[Drug, float, int]]:
    SQL_QUERY = """
        SELECT
            pharmacy_has_item.item_id,
            drug_group.drug_group_id,
            drug_group.name,
            drug.cipher,
            drug.name,
            manufacturer.manufacturer_id,
            country.country_id,
            country.name,
            manufacturer.name,
            pharmacy_item.price,
            pharmacy_has_item.amount
        FROM
            pharmacy_has_item
            JOIN pharmacy_item USING (item_id)
            JOIN drug USING (drug_id)
            JOIN drug_group USING (drug_group_id)
            JOIN manufacturer USING (manufacturer_id)
            JOIN country USING (country_id)
    """
    return tuple(
        (
            Drug.from_primitives(*item_tuple[:9]),
            float(item_tuple[9]),
            int(item_tuple[10]),
        )
        for item_tuple in db_execute(db, SQL_QUERY)
    )


def db_get_pharmacy_items_filtered(
    db: DBCursor, *, drug_group_name=None, price_min=None, price_max=None,
) -> tuple[tuple[Drug, float, int]]:
    SQL_QUERY = """
        SELECT
            pharmacy_has_item.item_id,
            drug_group.drug_group_id,
            drug_group.name,
            drug.cipher,
            drug.name,
            manufacturer.manufacturer_id,
            country.country_id,
            country.name,
            manufacturer.name,
            pharmacy_item.price,
            pharmacy_has_item.amount
        FROM
            pharmacy_has_item
            JOIN pharmacy_item USING (item_id)
            JOIN drug USING (drug_id)
            JOIN drug_group USING (drug_group_id)
            JOIN manufacturer USING (manufacturer_id)
            JOIN country USING (country_id)
        WHERE pharmacy_has_item.item_id IS NOT NULL
    """

    if drug_group_name:
        SQL_QUERY += f"\nAND drug_group.name = '{drug_group_name}'"
    if price_min:
        SQL_QUERY += f"\nAND pharmacy_item.price >= {price_min}"
    if price_max:
        SQL_QUERY += f"\nAND pharmacy_item.price <= {price_max}"

    return tuple(
        (
            Drug.from_primitives(*item_tuple[:9]),
            float(item_tuple[9]),
            int(item_tuple[10]),
        )
        for item_tuple in db_execute(db, SQL_QUERY)
    )


def db_get_pharmacy_item_amount(db: DBCursor, item_id) -> int:
    SQL_QUERY = """
        SELECT amount FROM pharmacy_has_item
        WHERE item_id = %s
    """
    amount_tuples = db_execute(db, SQL_QUERY, (item_id))
    if not amount_tuples:
        return 0
    return amount_tuples[0][0]
