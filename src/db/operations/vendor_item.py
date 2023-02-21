from db import *

from .vendor import *


def db_get_vendor_items(db: DBCursor, vendor_id) -> tuple[Item]:
    SQL_QUERY = """
        SELECT
            vendor_item.item_id,
            vendor_item.drug_id,
            drug_group.drug_group_id,
            drug_group.name,
            drug.cipher,
            drug.name,
            manufacturer.manufacturer_id,
            country.country_id,
            country.name,
            manufacturer.name,
            vendor_item.price
        FROM
            vendor_item
            JOIN drug USING (drug_id)
            JOIN drug_group USING (drug_group_id)
            JOIN manufacturer USING (manufacturer_id)
            JOIN country USING (country_id)
        WHERE vendor_id = %s
    """
    return tuple(
        Item.from_primitives(*item_tuple)
        for item_tuple in db_execute(db, SQL_QUERY, (vendor_id,))
    )


def db_get_vendor_storefront_items_amounts(
    db: DBCursor, vendor_id
) -> tuple[tuple[Item, int]]:
    SQL_QUERY = """
        SELECT
            vendor_has_item.item_id,
            vendor_item.drug_id,
            drug_group.drug_group_id,
            drug_group.name,
            drug.cipher,
            drug.name,
            manufacturer.manufacturer_id,
            country.country_id,
            country.name,
            manufacturer.name,
            vendor_item.price,
            vendor_has_item.amount
        FROM
            vendor_has_item
            JOIN vendor_item USING (item_id)
            JOIN drug USING (drug_id)
            JOIN drug_group USING (drug_group_id)
            JOIN manufacturer USING (manufacturer_id)
            JOIN country USING (country_id)
        WHERE vendor_has_item.vendor_id = %s
    """
    return tuple(
        (Item.from_primitives(*item_tuple[:-1]), int(item_tuple[-1]))
        for item_tuple in db_execute(db, SQL_QUERY, (vendor_id,))
    )


def db_get_vendor_storefront_item_amount(db: DBCursor, item_id) -> tuple[Item, int]:
    SQL_QUERY = """
        SELECT
            vendor_has_item.item_id,
            vendor_item.drug_id,
            drug_group.drug_group_id,
            drug_group.name,
            drug.cipher,
            drug.name,
            manufacturer.manufacturer_id,
            country.country_id,
            country.name,
            manufacturer.name,
            vendor_item.price,
            vendor_has_item.amount
        FROM
            vendor_has_item
            JOIN vendor_item USING (item_id)
            JOIN drug USING (drug_id)
            JOIN drug_group USING (drug_group_id)
            JOIN manufacturer USING (manufacturer_id)
            JOIN country USING (country_id)
        WHERE vendor_has_item.item_id = %s
    """
    item_tuples = db_execute(db, SQL_QUERY, (item_id,))
    print(f"item_tuples: {item_tuples}")
    if not item_tuples:
        raise ModelError("Vendor does not have such items on storefront.")
    return Item.from_primitives(*item_tuples[0][:-1]), int(item_tuples[0][-1])


def db_add_vendor_item(db: DBCursor, vendor_id, drug_id, price) -> None:
    SQL_QUERY = """
        INSERT INTO vendor_item (vendor_id, drug_id, price)
        VALUES (%s, %s, %s)
    """
    db_execute(db, SQL_QUERY, (vendor_id, drug_id, price))


def db_add_vendor_storefront_item(db: DBCursor, vendor_id, item_id, amount) -> None:
    SQL_QUERY = """
        INSERT INTO vendor_has_item (vendor_id, item_id, amount)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE amount = amount + %s
    """
    db_execute(db, SQL_QUERY, (vendor_id, item_id, amount, int(amount)))


def db_delete_vendor_storefront_item(db: DBCursor, vendor_id, item_id) -> None:
    SQL_QUERY = """
        DELETE FROM vendor_has_item
        WHERE vendor_id = %s AND item_id = %s
    """
    db_delete_admin_carts_item(db, item_id)
    db_execute(db, SQL_QUERY, (vendor_id, item_id))


def db_delete_vendor_item(db: DBCursor, item_id) -> None:
    SQL_QUERY = """
        DELETE FROM vendor_item
        WHERE item_id = %s
    """
    try:
        db_execute(db, SQL_QUERY, (item_id,))
    except DBIntegrityError as error:
        if not error.msg:
            raise DefaultModelError(error)
        if error.msg.find("admin_cart_has_item") >= 0:
            raise ModelError(
                "Could not delete given item because it is contained in some admin's cart."
            )
        if error.msg.find("vendor_has_item") >= 0:
            raise ModelError(
                "Could not delete given item because it is on vendor's storefront."
            )
        raise DefaultModelError(error)
