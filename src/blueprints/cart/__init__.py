from flask import Blueprint, render_template, redirect, url_for, request

from helpers.authority import *
from helpers.flashes import *
from proxies import *

from forms import AddItemToCartForm, AddItemToCustomerCartForm, ChangeItemAmountForm, ChangeCustomerCartItemAmountForm


bp = Blueprint(
    "cart",
    __name__,
    url_prefix="/cart",
    template_folder="templates",
    static_folder="static",
)


@bp.get("/")
@login_required
def read():
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
def order_admin_cart():
    days_to_wait = datetime.timedelta(0)

    try:
        db_order_admin_cart(
            db,
            user.user_id,
            datetime.date.today(),
            datetime.date.today() + days_to_wait,
        )
    except ModelError as error:
        flash_error(error)

    return redirect(request.referrer)


@bp.post("/admin/add/<int:item_id>")
@admin_rights_required
def add_to_admin_cart(item_id: int):
    form = AddItemToCartForm(request.form.to_dict())
    if not form.is_valid:
        return redirect(request.referrer)

    try:
        db_push_admin_cart_item_amount(db, user.user_id, item_id, form.amount)
    except ModelError as error:
        flash_error(error)

    return redirect(request.referrer)


@bp.post("/admin/<int:item_id>/delete")
@admin_rights_required
def delete_from_admin_cart(item_id: int):
    try:
        db_delete_admin_cart_item(db, user.user_id, item_id)
    except ModelError as error:
        flash_error(error)

    return redirect(request.referrer)


@bp.post("/admin/change-item-amount")
@admin_rights_required
def admin_cart_change_item_amount():
    form = ChangeItemAmountForm(request.form.to_dict())
    if not form.is_valid:
        return redirect(request.referrer)

    try:
        db_update_admin_cart_item_amount(db, user.user_id, form.item_id, form.amount)
    except ModelError as error:
        flash_error(error)

    return redirect(request.referrer)


@bp.get("/customer")
@login_required
def customer():
    return render_template(
        "customer_cart.j2",
        items=db_get_customer_cart_items(db, user.user_id)
    )


@bp.post("/customer")
@login_required
def add_to_customer_cart():
    form = AddItemToCustomerCartForm(request.form.to_dict())
    if not form.is_valid:
        return redirect(request.referrer)

    try:
        db_push_customer_cart_item_amount(db, user.user_id, form.drug_id, form.price, form.amount)
    except ModelError as error:
        flash_error(error)

    return redirect(request.referrer)


@bp.post("/customer/change-item-amount")
def customer_cart_change_item_amount():
    form = ChangeCustomerCartItemAmountForm(request.form.to_dict())
    if not form.is_valid:
        return redirect(request.referrer)

    try:
        db_update_customer_cart_item_amount(db, user.user_id, form.drug_id, form.price, form.amount)
    except ModelError as error:
        flash_error(error)

    return redirect(request.referrer)


@bp.post("/customer/<int:user_id>/order")
@login_required
def order_customer_cart(user_id: int):
    if user_id != user.user_id:
        abort(503)

    try:
        db_order_customer_cart(db, user.user_id, datetime.date.today(), datetime.date.today())
    except ModelError as error:
        flash_error(error)

    return redirect(request.referrer)
