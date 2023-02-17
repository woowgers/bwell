from flask import Blueprint, request, url_for, redirect, render_template

from helpers.authority import cashier_rights_required


bp = Blueprint(
    "orders",
    __name__,
    url_prefix="/orders",
    static_folder="static",
    template_folder="templates"
)


@bp.get("/")
@cashier_rights_required
def read():
    return render_template(
        "orders.j2",
        admin_orders=db_get_admins_orders(db),
        customer_orders=db_get_customers_orders(db)
    )


@bp.get("/admin/<int:order_id>")
@cashier_rights_required
def admin_order(order_id: int):
    return render_template(
        "admin_order.j2",
        order=db_get_admin_order(db, order_id)
    )

@bp.get("/customer/<int:order_id>")
@cashier_rights_required
def customer_order(order_id: int):
    return render_template(
        "customer_order.j2",
        order=db_get_customer_order(db, order_id)
    )

