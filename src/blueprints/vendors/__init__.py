from flask import Blueprint, render_template, request, url_for, redirect

from proxies import db
from helpers.authority import admin_rights_required
from helpers.flashes import *
from forms import *
from db import *
from db.models import *


bp = Blueprint(
    "vendors",
    __name__,
    url_prefix="/vendors",
    static_folder="static",
    template_folder="templates",
)


@bp.route("/", methods=("GET", "POST"))
@admin_rights_required
def read():
    if request.method == "GET":
        return render_template(
            "vendors.j2", cities=db_get_cities(db), vendors=db_get_vendors(db)
        )

    else:
        form = VendorRegisterForm(request.form.to_dict())
        if not form.is_valid:
            return redirect(url_for("vendors.read"))

        try:
            vendor = db_add_vendor(db, *form.fields.values())
        except ModelError as error:
            flash_error(error)
        else:
            flash_success(f'You have successfully registered "{vendor.company_name}".')

        return redirect(url_for("vendors.read"))


@bp.post("/delete_vendor/<int:vendor_id>")
@admin_rights_required
def delete_vendor(vendor_id: int):
    try:
        db_delete_vendor(db, vendor_id)
    except ModelError as error:
        flash_error(error)

    return redirect(request.referrer)


@bp.post("/terminate_agreement")
@admin_rights_required
def terminate_agreement():
    form = VendorAgreementTerminationForm(request.form.to_dict())
    if not form.is_valid:
        return redirect(url_for("vendors.read"))

    try:
        vendor = db_get_vendor(db, form.vendor_id)
        db_vendor_terminte_agreement(db, form.vendor_id, form.termination_date)
    except ModelError as error:
        flash_error(error)
    else:
        flash_success(
            f'You have successfully terminated agreeement with "{vendor.company_name}".'
        )

    return redirect(url_for("vendors.read"))


@bp.route("/items/<int:vendor_id>", methods=("GET", "POST"))
@admin_rights_required
def items(vendor_id: int):
    if request.method == "GET":
        try:
            vendor = db_get_vendor(db, vendor_id)
        except ModelError as error:
            flash_error(error)
            return redirect(request.referrer)

        return render_template(
            "vendors_items.j2",
            drugs=db_get_drugs(db),
            vendor=vendor,
            items=db_get_vendor_items(db, vendor_id),
            storefront_items=db_get_vendor_storefront_items(db, vendor_id),
        )

    else:
        form = VendorAddItemForm(request.form.to_dict())
        if not form.is_valid:
            return redirect(url_for("vendors.items", vendor_id=vendor_id))

        try:
            db_add_vendor_item(db, vendor_id, form.drug_id, form.price)
        except ModelError as error:
            flash_error(error)
            return redirect(request.referrer)

        return redirect(request.referrer)


@bp.post("/storefront-items/<int:vendor_id>")
@admin_rights_required
def storefront_items(vendor_id: int):
    form = VendorAddStorefrontItemForm(request.form.to_dict())
    if not form.is_valid:
        return redirect(request.referrer)

    try:
        db_add_vendor_storefront_item(db, vendor_id, form.item_id, form.amount)
    except ModelError as error:
        flash_error(error)

    return redirect(request.referrer)


@bp.post("/delete-item/<int:vendor_id>/<int:item_id>")
@admin_rights_required
def delete_item(vendor_id: int, item_id: int):
    try:
        db_delete_vendor_item(db, item_id)
    except ModelError as error:
        flash_error(error)

    return redirect(url_for("vendors.items", vendor_id=vendor_id))
