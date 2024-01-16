from bwell.db import *


def db_push_customer_cart_item_amount(
    db: DBCursor, user_id, item_id, amount
) -> None:
    SQL_QUERY = """
        INSERT INTO customer_cart_has_item (user_id, item_id, price, amount)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id, item_id)
        ON DUPLICATE KEY UPDATE amount = amount + %s
    """

    if amount <= 0:
        raise ModelError("Amount must be positive.")

    amount_pharmacy_has = db_get_pharmacy_item_amount(db, item_id)
    amount_in_cart_already = db_get_customer_cart_item_amount(
        db, user_id, item_id
    )
    total_amount_wanted = amount_in_cart_already + amount

    if amount_in_cart_already != 0 and total_amount_wanted > amount_pharmacy_has:
        raise ModelError(
            f"You already have {amount_in_cart_already} of given drug in cart, pharmacy has not enough of this drug."
        )
    elif total_amount_wanted > amount_pharmacy_has:
        raise ModelError(f"Vendor does not have enough of given drug.")

    db_execute(db, SQL_QUERY, (user_id, item_id, amount, amount))


def db_delete_customer_cart_item(db: DBCursor, user_id, item_id) -> None:
    SQL_QUERY = """
        DELETE FROM customer_cart_has_item
        WHERE user_id = %s AND item_id %s
    """
    db_execute(db, SQL_QUERY, (user_id, item_id))


def db_get_customer_cart_items(db: DBCursor, user_id) -> tuple[tuple[Item, int]]:
    SQL_QUERY = """
        SELECT
            customer_cart_has_item.item_id,
            drug_group.drug_group_id,
            drug_group.name,
            drug.cipher,
            drug.name,
            manufacturer.manufacturer_id,
            country.country_id,
            country.name,
            manufacturer.name,
            customer_cart_has_item.price,
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
        (
            Item.from_primitives(*item_tuple[:9]),
            int(item_tuple[10]),
        )
        for item_tuple in db_execute(db, SQL_QUERY, (user_id,))
    )


def db_get_customer_cart_item_amount(db: DBCursor, user_id, item_id) -> int:
    SQL_QUERY = """
        SELECT amount FROM customer_cart_has_item
        WHERE user_id = %s AND item_id = %s
    """
    amount_tuples = db_execute(db, SQL_QUERY, (user_id, item_id))
    if not amount_tuples:
        return 0
    return amount_tuples[0][0]


def db_get_customers_orders(db: DBCursor) -> tuple[Order]:
    SQL_QUERY = """
        SELECT
            order_id,
            user_id,
            email,
            user_type,
            name,
            pw_hash,
            create_date,
            expect_receive_date,
            receive_date,
            cost
        FROM customer_order JOIN user USING (user_id)
    """
    return tuple(
        Order.from_primitives(*order_tuple) for order_tuple in db_execute(db, SQL_QUERY)
    )


def db_get_customers_orders_filtered(
    db: DBCursor,
    *,
    create_date_min=None,
    create_date_max=None,
    receive_date_min=None,
    receive_date_max=None,
    cost_min=None,
    cost_max=None,
    is_received=None,
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
        FROM customer_order JOIN user USING (user_id)
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
        Order.from_primitives(*order_tuple) for order_tuple in db_execute(db, SQL_QUERY)
    )


def db_get_customer_orders(db: DBCursor, user_id) -> tuple[Order]:
    SQL_QUERY = """
        SELECT
            order_id,
            user_id,
            email,
            user_type,
            name,
            pw_hash,
            create_date,
            expect_receive_date,
            receive_date,
            cost
        FROM customer_order JOIN user USING (user_id)
        WHERE user_id = %s
    """
    return tuple(
        Order.from_primitives(*order_tuple)
        for order_tuple in db_execute(db, SQL_QUERY, (user_id,))
    )


def db_get_customer_order(db: DBCursor, order_id) -> Order:
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
        FROM customer_order JOIN user USING (user_id)
        WHERE order_id = %s
    """
    order_tuples = db_execute(db, SQL_QUERY, (order_id,))
    if not order_tuples:
        raise ModelError(f"Customer order with ID={order_id} does not exist.")
    return Order.from_primitives(*order_tuples[0])


def db_update_customer_cart_item_amount(
    db: DBCursor, user_id, item_id, amount
) -> None:
    SQL_QUERY = """
        UPDATE customer_cart_has_item
        SET amount = %s
        WHERE user_id = %s AND item_id = %s
    """

    if amount < 0:
        raise ModelError("Amount must not be negative.")

    if amount == 0:
        return db_delete_customer_cart_item(db, user_id, item_id)

    amount_pharmacy_has = db_get_pharmacy_item_amount(db, item_id)
    if amount > amount_pharmacy_has:
        raise ModelError(f"Pharmacy does not have enough of given drug.")

    db_execute(db, SQL_QUERY, (amount, user_id, item_id))


def db_create_customer_order(
    db: DBCursor, user_id, create_date, expect_receive_date
) -> Order:
    order_tuple = db_callproc(
        db,
        "create_customer_order",
        (None, user_id, create_date, expect_receive_date, None, None),
    )
    user = db_get_user(db, user_id)
    return Order(order_tuple[0], user, *order_tuple[2:])


def db_move_drug_from_customer_cart_to_order(
    db: DBCursor, user_id, order_id, item_id, amount
) -> None:
    try:
        amount_pharmacy_has = db_get_pharmacy_item_amount(db, item_id)
    except ModelError:
        db_delete_customer_cart_item(db, user_id, item_id)
        raise

    if amount > amount_pharmacy_has:
        drug = db_get_drug(db, item_id)
        raise ModelError(
            f"Pharmacy does not have enough of drug with cipher={drug.cipher}."
        )

    db_callproc(
        db,
        "move_drug_from_customer_cart_to_order",
        (user_id, order_id, item_id, amount),
    )


def db_order_customer_cart(
    db: DBCursor, user_id, create_date, expect_receive_date
) -> None:
    cart_items = db_get_customer_cart_items(db, user_id)
    if not cart_items:
        raise ModelError("You cannot make an empty order. Pick something in your cart.")

    order = db_create_customer_order(db, user_id, create_date, expect_receive_date)

    for item, amount in cart_items:
        db_move_drug_from_customer_cart_to_order(
            db, user_id, order.order_id, drug.drug_id, amount
        )


def db_receive_customer_order(
    db: DBCursor, order_id, receive_date=datetime.date.today()
) -> None:
    db_callproc(db, "receive_customer_order", (order_id, receive_date))


def db_get_customer_order_items(
    db: DBCursor, order_id
) -> tuple[tuple[Drug, float, int]]:
    SQL_QUERY = """
        SELECT
            customer_order_has_drug.drug_id,
            drug_group.drug_group_id,
            drug_group.name,
            drug.cipher,
            drug.name,
            manufacturer.manufacturer_id,
            country.country_id,
            country.name,
            manufacturer.name,
            customer_order_has_drug.price,
            customer_order_has_drug.amount
        FROM
            customer_order_has_drug
            JOIN drug USING (drug_id)
            JOIN drug_group USING (drug_group_id)
            JOIN manufacturer USING (manufacturer_id)
            JOIN country USING (country_id)
        WHERE customer_order_has_drug.order_id = %s
    """
    return tuple(
        (
            Drug.from_primitives(*item_tuple[:9]),
            float(item_tuple[9]),
            int(item_tuple[10]),
        )
        for item_tuple in db_execute(db, SQL_QUERY, (order_id,))
    )
