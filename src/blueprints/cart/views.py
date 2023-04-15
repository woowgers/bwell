from flask import render_template, redirect, url_for, request

from helpers.authority import *
from helpers.flashes import *
from proxies import *

from forms import (
    AddItemToCartForm,
    AddItemToCustomerCartForm,
    ChangeItemAmountForm,
    ChangeCustomerCartItemAmountForm,
)


from . import bp


@bp.get("/")
@login_required
def my():
    if user.is_admin:
        return render_template("choose_cart_type.j2")
    else:
        return redirect(url_for("cart.customer"))


@bp.get("/admin")
@admin_rights_required
def admin():
    return render_template(
        "admin_cart.j2", items=db_get_admin_cart_items_amounts(db, user.user_id)
    )


@bp.post("/admin/order")
@admin_rights_required
def admin_order():
    days_to_wait = datetime.timedelta(0)

    with ModelWebUIContext():
        db_order_admin_cart(
            db,
            user.user_id,
            datetime.date.today(),
            datetime.date.today() + days_to_wait,
        )

    return redirect(request.referrer)


@bp.post("/admin/add/<int:item_id>")
@admin_rights_required
def admin_add(item_id: int):
    form = AddItemToCartForm(fields_dict=request.form.to_dict())
    if not form.is_valid:
        return redirect(request.referrer)

    with ModelWebUIContext():
        db_push_admin_cart_item_amount(db, user.user_id, item_id, form.amount)

    return redirect(request.referrer)


@bp.post("/admin/delete/<int:item_id>")
@admin_rights_required
def admin_item_delete(item_id: int):
    with ModelWebUIContext():
        db_delete_admin_cart_item(db, user.user_id, item_id)

    return redirect(request.referrer)


@bp.post("/admin/update/<int:item_id>")
@admin_rights_required
def admin_item_update(item_id: int):
    form = ChangeItemAmountForm(fields_dict=request.form.to_dict())
    if not form.is_valid:
        return redirect(request.referrer)

    with ModelWebUIContext():
        db_update_admin_cart_item_amount(db, user.user_id, item_id, form.amount)

    return redirect(request.referrer)


@bp.get("/customer")
@login_required
def customer():
    return render_template(
        "customer_cart.j2", items=db_get_customer_cart_items(db, user.user_id)
    )


@bp.post("/customer")
@login_required
def customer_add():
    form = AddItemToCustomerCartForm(fields_dict=request.form.to_dict())
    if not form.is_valid:
        return redirect(request.referrer)

    with ModelWebUIContext():
        db_push_customer_cart_item_amount(
            db, user.user_id, form.drug_id, form.price, form.amount
        )

    return redirect(request.referrer)


@bp.post("/customer/update/<int:item_id>")
def customer_item_update(item_id: int):
    form = ChangeCustomerCartItemAmountForm(fields_dict=request.form.to_dict())
    if not form.is_valid:
        return redirect(request.referrer)

    with ModelWebUIContext():
        db_update_customer_cart_item_amount(db, user.user_id, item_id, form.amount)

    return redirect(request.referrer)


@bp.post("/customer/<int:user_id>/order")
@login_required
def customer_order(user_id: int):
    if user_id != user.user_id:
        abort(503)

    with ModelWebUIContext():
        db_order_customer_cart(
            db, user.user_id, datetime.date.today(), datetime.date.today()
        )

    return redirect(request.referrer)
