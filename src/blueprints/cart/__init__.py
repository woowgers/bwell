from flask import Blueprint, render_template, redirect, url_for, request

from helpers.authority import *
from helpers.flashes import *
from proxies import *

from forms import AddItemToCartForm


bp = Blueprint(
    "cart",
    __name__,
    url_prefix="/cart",
    template_folder="templates",
    static_folder="static",
)


@bp.route("/")
@login_required
def read():
    if user.is_admin:
        return render_template("choose_cart_type.j2")
    else:
        return redirect(url_for("cart.customer"))


@bp.route("/admin", methods=("GET", "POST"))
@admin_rights_required
def admin():
    if request.method == "GET":
        return render_template(
            "admin_cart.j2", items=db_get_admin_cart_items(db, user.user_id)
        )

    else:
        form = AddItemToCartForm(request.form.to_dict())
        if not form.is_valid:
            return redirect(request.referrer)

        try:
            db_add_item_to_admin_cart(db, user.user_id, form.item_id, form.amount)
        except ModelError as error:
            flash_error(error)

        return redirect(request.referrer)


@bp.route("/customer", methods=("GET", "POST"))
@login_required
def customer():
    if request.method == "GET":
        return render_template(
            "customer_cart.j2", items=db_get_customer_cart_items(db, user.user_id)
        )
