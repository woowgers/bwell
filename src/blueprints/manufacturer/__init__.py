from flask import Blueprint, render_template, redirect, request

from helpers.authority import admin_rights_required
from proxies import db
from db import *
from forms import ManufacturerAddForm


bp = Blueprint(
    "manufacturer",
    __name__,
    url_prefix="/manufacturer",
    static_folder="static",
    template_folder="templates",
)


@bp.get("/")
@admin_rights_required
def all():
    return render_template(
        "manufacturers.j2",
        countries=db_get_countries(db),
        manufacturers=db_get_manufacturers(db),
    )


@bp.post("/")
@admin_rights_required
def create():
    form = ManufacturerAddForm(fields_dict=request.form.to_dict())
    if not form.is_valid:
        return redirect(request.referrer)

    with ModelWebUIContext():
        db_add_manufacturer(db, form.country_name, form.company_name)

    return redirect(request.referrer)


@bp.post("/<int:manufacturer_id>/delete")
@admin_rights_required
def delete(manufacturer_id: int):
    with ModelWebUIContext():
        db_delete_manufacturer(db, manufacturer_id)

    return redirect(request.referrer)
