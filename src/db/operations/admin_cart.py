from db import *

from .vendor_item import *


def db_get_admin_cart_items_amounts(db: DBCursor, user_id) -> tuple[tuple[Item, int]]:
    SQL_QUERY = """
        SELECT
            admin_cart_has_item.item_id,
            drug.drug_id,
            drug_group.drug_group_id,
            drug_group.name,
            drug.cipher,
            drug.name,
            manufacturer.manufacturer_id,
            country.country_id,
            country.name,
            manufacturer.name,
            vendor_item.price,
            admin_cart_has_item.amount
        FROM
            admin_cart_has_item
            JOIN vendor_item USING (item_id)
            JOIN drug USING (drug_id)
            JOIN drug_group USING (drug_group_id)
            JOIN manufacturer USING (manufacturer_id)
            JOIN country USING (country_id)
        WHERE admin_cart_has_item.user_id = %s
    """
    return tuple(
        (Item.from_primitives(*item_tuple[:-1]), item_tuple[-1])
        for item_tuple in db_execute(db, SQL_QUERY, (user_id,))
    )


def db_get_admin_cart_item_amount(db: DBCursor, user_id, item_id) -> int:
    SQL_QUERY = """
        SELECT
            admin_cart_has_item.amount
        FROM
            admin_cart_has_item
            JOIN vendor_item USING (item_id)
            JOIN drug USING (drug_id)
            JOIN drug_group USING (drug_group_id)
            JOIN manufacturer USING (manufacturer_id)
            JOIN country USING (country_id)
        WHERE
            admin_cart_has_item.user_id = %s
            AND admin_cart_has_item.item_id = %s
    """
    item_tuples = db_execute(db, SQL_QUERY, (user_id, item_id))
    if not item_tuples:
        return 0
    return int(item_tuples[0][0])


def db_push_admin_cart_item_amount(db: DBCursor, user_id, item_id, amount) -> None:
    SQL_QUERY = """
        INSERT INTO admin_cart_has_item (user_id, item_id, amount)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE amount = amount + %s
    """

    if amount <= 0:
        raise ModelError("Amount must be positive.")

    item, amount_vendor_has = db_get_vendor_storefront_item_amount(db, item_id)
    amount_in_cart_already = db_get_admin_cart_item_amount(db, user_id, item_id)
    total_amount_wanted = amount_in_cart_already + amount

    print(
        f"item: {item}\namount_in_cart_already: {amount_in_cart_already}\namount_vendor_has: {amount_vendor_has}\ntotal_amount_wanted: {total_amount_wanted}"
    )

    if amount_in_cart_already != 0 and total_amount_wanted > amount_vendor_has:
        raise ModelError(
            f'You already have {amount_in_cart_already} of "{item.drug.name}" in cart, vendor has not enough if this item on storefront.'
        )
    elif total_amount_wanted > amount_vendor_has:
        raise ModelError(
            f'Vendor does not have enough of "{item.drug.name}" on storefront.'
        )

    db_execute(db, SQL_QUERY, (user_id, item_id, amount, amount))


def db_update_admin_cart_item_amount(db: DBCursor, user_id, item_id, amount) -> None:
    SQL_QUERY = """
        UPDATE admin_cart_has_item
        SET amount = %s
        WHERE user_id = %s AND item_id = %s
    """

    if amount < 0:
        raise ModelError("Amount must not be negative.")

    if amount == 0:
        return db_delete_admin_cart_item(db, user_id, item_id)

    item, amount_vendor_has = db_get_vendor_storefront_item_amount(db, item_id)
    if amount > amount_vendor_has:
        raise ModelError(
            f'Vendor does not have enough of "{item.drug.name}" on storefront.'
        )

    db_execute(db, SQL_QUERY, (amount, user_id, item_id))


def db_delete_admin_cart_items(db: DBCursor, user_id) -> None:
    SQL_QUERY = """
        DELETE FROM admin_cart_has_item
        WHERE user_id = %s
    """
    db_execute(db, SQL_QUERY, (user_id,))


def db_delete_admin_cart_item(db: DBCursor, user_id, item_id) -> None:
    SQL_QUERY = """
        DELETE FROM admin_cart_has_item
        WHERE user_id = %s AND item_id = %s
    """
    db_execute(db, SQL_QUERY, (user_id, item_id))


def db_delete_admin_carts_item(db: DBCursor, item_id) -> None:
    SQL_QUERY = """
        DELETE FROM admin_cart_has_item
        WHERE item_id = %s
    """
    db_execute(db, SQL_QUERY, (item_id,))


def db_create_admin_order(db: DBCursor, create_date, expect_receive_date) -> Order:
    order_tuple = db_callproc(
        db, "create_admin_order", (None, create_date, expect_receive_date, None, None)
    )
    return Order(*order_tuple)


def db_order_admin_cart(
    db: DBCursor, user_id, create_date, expect_receive_date
) -> None:
    SQL_QUERY = """
        INSERT INTO admin_order_has_item (order_id, item_id, amount)
        VALUES (%s, %s, %s)
    """

    item_amounts_in_cart = db_get_admin_cart_items_amounts(db, user_id)
    if not item_amounts_in_cart:
        raise ModelError("You cannot make an empty order. Pick something in your cart.")

    order = db_create_admin_order(db, create_date, expect_receive_date)

    def make_param_tuple_from_item_amount(
        item_amount: tuple[Item, int]
    ) -> tuple[int, int, int]:
        item, amount = item_amount
        return order.order_id, item.item_id, amount

    param_tuples = tuple(map(make_param_tuple_from_item_amount, item_amounts_in_cart))

    db_executemany(db, SQL_QUERY, param_tuples)
    db_delete_admin_cart_items(db, user_id)
