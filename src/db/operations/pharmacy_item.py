from db import *


def db_get_pharmacy_items(db: DBCursor) -> tuple[Item]:
    SQL_QUERY = """
        SELECT
            pharmacy_has_item.item_id,
            pharmacy_item.drug_id,
            drug_group.drug_group_id,
            drug_group.name,
            drug.cipher,
            drug.name,
            manufacturer.name,
            country.country_id,
            country.name,
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
        Item.from_primitives(*item_tuple) for item_tuple in db_execute(db, SQL_QUERY)
    )
