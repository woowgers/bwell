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

    if amount_in_cart_already != 0 and total_amount_wanted > amount_vendor_has:
        raise ModelError(
            f'You already have {amount_in_cart_already} of "{item.drug.name}" in cart, vendor has not enough of this item on storefront.'
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


def db_get_admins_orders(db: DBCursor) -> tuple[Order]:
    SQL_QUERY = """
        SELECT
            order_id,
            user.user_id,
            user.email,
            user.user_type,
            user.name,
            user.pw_hash,
            create_date,
            expect_receive_date,
            receive_date,
            cost
        FROM admin_order JOIN user USING (user_id)
    """
    return tuple(
        Order.from_primitives(*order_tuple) for order_tuple in db_execute(db, SQL_QUERY)
    )


def db_get_admin_orders(db: DBCursor, user_id) -> tuple[Order]:
    SQL_QUERY = """
        SELECT
            order_id,
            user.user_id,
            user.email,
            user.user_type,
            user.name,
            user.pw_hash,
            create_date,
            expect_receive_date,
            receive_date,
            cost
        FROM admin_order JOIN user USING (user_id)
        WHERE user_id = %s
    """
    return tuple(
        Order.from_primitives(*order_tuple)
        for order_tuple in db_execute(db, SQL_QUERY, (user_id,))
    )


def db_get_admins_orders_filtered(
    db: DBCursor,
    *,
    create_date_min=None,
    create_date_max=None,
    receive_date_min=None,
    receive_date_max=None,
    cost_min=None,
    cost_max=None,
    is_received=None
):
    SQL_QUERY = """
        SELECT
            order_id,
            user.user_id,
            user.email,
            user.user_type,
            user.name,
            user.pw_hash,
            create_date,
            expect_receive_date,
            receive_date,
            cost
        FROM admin_order JOIN user USING (user_id)
        WHERE order_id is not null
    """
    if create_date_min:
        SQL_QUERY += f"\nAND create_date >= '{create_date_min}'"
    if create_date_max:
        SQL_QUERY += f"\nAND create_date <= '{create_date_max}'"
    if is_received is not None:
        if is_received:
            SQL_QUERY += f"\nAND receive_date is not null"
        else:
            SQL_QUERY += f"\nAND receive_date is null"
    else:
        if receive_date_min:
            SQL_QUERY += f"\nAND receive_date >= '{receive_date_min}'"
        if receive_date_max:
            SQL_QUERY += f"\nAND receive_date <= '{receive_date_max}'"
    if cost_min:
        SQL_QUERY += f"\nAND cost >= {cost_min}"
    if cost_max:
        SQL_QUERY += f"\nAND cost <= {cost_max}"

    print(SQL_QUERY)

    return tuple(
        Order.from_primitives(*order_tuple)
        for order_tuple in db_execute(db, SQL_QUERY)
    )


def db_get_admin_order(db: DBCursor, order_id) -> Order:
    SQL_QUERY = """
        SELECT
            order_id,
            user.user_id,
            user.email,
            user.user_type,
            user.name,
            user.pw_hash,
            create_date,
            expect_receive_date,
            receive_date,
            cost
        FROM admin_order JOIN user USING (user_id)
        WHERE order_id = %s
    """
    order_tuples = db_execute(db, SQL_QUERY, (order_id,))
    if not order_tuples:
        raise ModelError(f"Admin order with ID={order_id} does not exist.")
    return Order.from_primitives(*order_tuples[0])


def db_move_item_from_admin_cart_to_order(
    db: DBCursor, user_id: int, item_id: int, amount: int, order_id: int
) -> None:
    try:
        item, amount_vendor_has = db_get_vendor_storefront_item_amount(db, item_id)
    except ModelError:
        db_delete_admin_cart_item(db, user_id, item_id)
        raise

    if amount > amount_vendor_has:
        raise ModelError(
            f'Vendor does not have enough of "{item.drug.name}" (price: {item.price}; cipher: {item.drug.cipher}).'
        )

    db_callproc(
        db, "move_item_from_admin_cart_to_order", (user_id, order_id, item_id, amount)
    )


def db_create_admin_order(
    db: DBCursor, user_id, create_date, expect_receive_date
) -> Order:
    order_tuple = db_callproc(
        db,
        "create_admin_order",
        (None, user_id, create_date, expect_receive_date, None, None),
    )
    user = db_get_user(db, user_id)
    return Order(order_tuple[0], user, *order_tuple[2:])


def db_order_admin_cart(
    db: DBCursor, user_id, create_date, expect_receive_date
) -> None:
    item_amounts_in_cart = db_get_admin_cart_items_amounts(db, user_id)
    if not item_amounts_in_cart:
        raise ModelError("You cannot make an empty order. Pick something in your cart.")

    order = db_create_admin_order(db, user_id, create_date, expect_receive_date)

    for item, amount in item_amounts_in_cart:
        db_move_item_from_admin_cart_to_order(
            db, user_id, item.item_id, amount, order.order_id
        )


def db_get_admin_order_items_amounts(db: DBCursor, order_id) -> tuple[tuple[Item, int]]:
    SQL_QUERY = """
        SELECT
            admin_order_has_item.item_id,
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
            admin_order_has_item.amount
        FROM
            admin_order_has_item
            JOIN vendor_item USING (item_id)
            JOIN drug USING (drug_id)
            JOIN drug_group USING (drug_group_id)
            JOIN manufacturer USING (manufacturer_id)
            JOIN country USING (country_id)
        WHERE admin_order_has_item.order_id = %s
    """
    return tuple(
        (Item.from_primitives(*item_tuple[:-1]), item_tuple[-1])
        for item_tuple in db_execute(db, SQL_QUERY, (order_id,))
    )


def db_receive_admin_order(
    db: DBCursor, order_id, receive_date=datetime.date.today()
) -> None:
    db_callproc(db, "receive_admin_order", (order_id, receive_date))
