from db import *


def db_add_item_to_customer_cart(db: DBCursor, user_id, item_id, amount) -> None:
    db_callproc(db, "customer_cart_add_item", (user_id, item_id, amount))


def db_get_customer_cart_items(db: DBCursor, user_id) -> tuple[tuple[Item, int]]:
    SQL_QUERY = """
        SELECT
            customer_cart_has_item.item_id,
            drug.drug_id,
            drug_group.drug_group_id,
            drug_group.name,
            drug.cipher,
            drug.name,
            manufacturer.manufacturer_id,
            country.country_id,
            country.name,
            manufacturer.name,
            pharmacy_item.price,
            customer_cart_has_item.amount
        FROM
            customer_cart_has_item
            JOIN pharmacy_item USING (item_id)
            JOIN drug USING (drug_id)
            JOIN drug_group USING (drug_group_id)
            JOIN manufacturer USING (manufacturer_id)
            JOIN country USING (country_id)
        WHERE customer_cart_has_item.user_id = %s
    """
    return tuple(
        (Item.from_primitives(*item_tuple[:-1]), item_tuple[-1])
        for item_tuple in db_execute(db, SQL_QUERY, (user_id,))
    )
