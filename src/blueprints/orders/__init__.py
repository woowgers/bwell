from flask import Blueprint, render_template, redirect, request, session
from forms import OrderFilterForm

from helpers.authority import cashier_rights_required, admin_rights_required
from helpers.flashes import *
from proxies import db
from db import *


bp = Blueprint(
    "orders",
    __name__,
    url_prefix="/orders",
    static_folder="static",
    template_folder="templates",
)


@bp.get("/")
@cashier_rights_required
def read():
    return render_template("orders_choose_type.j2")


@bp.get("/admins")
@admin_rights_required
def admins_orders():
    if not "orders" in session:
        return render_template("admins_orders.j2", orders=db_get_admins_orders(db))
    else:
        return render_template("admins_orders.j2", orders=session["orders"])


@bp.get("/admins/<orders>")
@admin_rights_required
def admins_orders_filtered_get(orders):
    return render_template("admins_orders.j2", orders=orders)


@bp.get("/admin/<int:user_id>")
@admin_rights_required
def admin_orders(user_id: int):
    return render_template("admin_orders.j2", orders=db_get_admin_orders(db, user_id))


@bp.get("/<int:order_id>/admin")
@admin_rights_required
def admin_order(order_id: int):
    return render_template(
        "admin_order.j2",
        order=db_get_admin_order(db, order_id),
        items_amounts=db_get_admin_order_items_amounts(db, order_id),
    )


@bp.post("/<int:order_id>/admin")
@admin_rights_required
def receive_admin_order(order_id: int):
    try:
        db_receive_admin_order(db, order_id)
    except ModelError as error:
        flash_error(error)

    return redirect(request.referrer)


@bp.post("/admins/filter")
@admin_rights_required
def admins_orders_filtered():
    form = OrderFilterForm(request.form.to_dict())
    if not form.is_valid:
        return redirect(request.referrer)

    session["orders"] = db_get_admins_orders_filtered(
        db,
        create_date_min=form.create_date_min,
        create_date_max=form.create_date_max,
        receive_date_min=form.receive_date_min,
        receive_date_max=form.receive_date_max,
        cost_min=form.cost_min,
        cost_max=form.cost_max,
        is_received=form.is_received,
    )
    return redirect(request.referrer)


@bp.get("/customers")
@cashier_rights_required
def customers_orders():
    if "customers_orders" not in session:
        return render_template(
            "customers_orders.j2", orders=db_get_customers_orders(db)
        )
    else:
        print(session["customers_orders"])
        orders = tuple(Order(**order) for order in session["customers_orders"])
        return render_template("customers_orders.j2", orders=orders)


@bp.post("/customers/filter")
@cashier_rights_required
def customers_orders_filtered():
    form = OrderFilterForm(request.form.to_dict())
    if not form.is_valid:
        return redirect(request.referrer)

    session["customers_orders"] = db_get_customers_orders_filtered(
        db,
        create_date_min=form.create_date_min,
        create_date_max=form.create_date_max,
        receive_date_min=form.receive_date_min,
        receive_date_max=form.receive_date_max,
        cost_min=form.cost_min,
        cost_max=form.cost_max,
        is_received=form.is_received,
    )
    return redirect(request.referrer)


@bp.get("/customer/<int:user_id>")
@cashier_rights_required
def customer_orders(user_id: int):
    return render_template(
        "customer_orders.j2", orders=db_get_customer_orders(db, user_id)
    )


@bp.get("/<int:order_id>/customer")
@cashier_rights_required
def customer_order(order_id: int):
    return render_template(
        "customer_order.j2",
        order=db_get_customer_order(db, order_id),
        items=db_get_customer_order_items(db, order_id),
    )


@bp.post("/<int:order_id>/customer")
@cashier_rights_required
def receive_customer_order(order_id: int):
    try:
        db_receive_customer_order(db, order_id)
    except ModelError as error:
        flash_error(error)

    return redirect(request.referrer)
