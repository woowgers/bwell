from flask import Blueprint, render_template, request, url_for, redirect

from proxies import db
from helpers.authority import admin_rights_required
from helpers.flashes import *
from forms import *
from db import *
from db.models import *


bp = Blueprint(
    "vendor",
    __name__,
    url_prefix="/vendor",
    static_folder="static",
    template_folder="templates",
)


@bp.get("/")
@admin_rights_required
def all():
    return render_template(
        "vendors.j2", cities=db_get_cities(db), vendors=db_get_vendors(db)
    )


@bp.post("/")
@admin_rights_required
def add():
    form = VendorRegisterForm(fields_dict=request.form.to_dict())
    if not form.is_valid:
        return redirect(url_for("vendor.read"))

    with ModelWebUIContext():
        db_add_vendor(
            db,
            form.cipher,
            form.company_name,
            form.city_name,
            form.agreement_conclusion_date,
        )

    return redirect(request.referrer)


@bp.post("/<int:vendor_id>/delete")
@admin_rights_required
def delete(vendor_id: int):
    with ModelWebUIContext():
        db_delete_vendor(db, vendor_id)

    return redirect(request.referrer)


@bp.post("/<int:vendor_id>/terminate-agreement")
@admin_rights_required
def terminate_agreement(vendor_id: int):
    form = VendorAgreementTerminationForm(fields_dict=request.form.to_dict())
    if not form.is_valid:
        return redirect(url_for("vendor.read"))

    with ModelWebUIContext():
        db_vendor_terminate_agreement(db, vendor_id, form.termination_date)

    return redirect(request.referrer)


@bp.get("/<int:vendor_id>/items")
@admin_rights_required
def items(vendor_id: int):
    try:
        with ModelWebUIContext():
            vendor = db_get_vendor(db, vendor_id)
    except (ModelError, DBUsageError):
        return redirect(request.referrer)

    return render_template(
        "vendors_items.j2",
        drugs=db_get_drugs(db),
        vendor=vendor,
        items=db_get_vendor_items(db, vendor_id),
        storefront_items=db_get_vendor_storefront_items_amounts(db, vendor_id),
    )


@bp.post("/<int:vendor_id>/items/add")
@admin_rights_required
def add_item(vendor_id: int):
    form = VendorAddItemForm(fields_dict=request.form.to_dict())
    if not form.is_valid:
        return redirect(url_for("vendor.items", vendor_id=vendor_id))
    else:
        flash_success("Item has been successfully added!")

    with ModelWebUIContext():
        db_add_vendor_item(db, vendor_id, form.drug_id, form.price)

    return redirect(request.referrer)


@bp.post("/<int:vendor_id>/storefront/add")
@admin_rights_required
def add_storefront_item(vendor_id: int):
    form = VendorAddStorefrontItemForm(fields_dict=request.form.to_dict())
    if not form.is_valid:
        return redirect(request.referrer)

    with ModelWebUIContext():
        db_add_vendor_storefront_item(db, vendor_id, form.item_id, form.amount)

    return redirect(request.referrer)


@bp.post("/items/delete/<int:item_id>")
@admin_rights_required
def delete_item(item_id: int):
    with ModelWebUIContext():
        db_delete_vendor_item(db, item_id)
    return redirect(request.referrer)


@bp.post("/<int:vendor_id>/storefront/delete/<int:item_id>")
@admin_rights_required
def delete_storefront_item(vendor_id: int, item_id: int):
    with ModelWebUIContext():
        db_delete_vendor_storefront_item(db, vendor_id, item_id)
    return redirect(request.referrer)
