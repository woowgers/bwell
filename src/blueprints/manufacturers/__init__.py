from flask import Blueprint, render_template, redirect, request

from helpers.flashes import flash_error
from helpers.authority import admin_rights_required
from proxies import db
from db import *
from forms import ManufacturerAddForm


bp = Blueprint(
    "manufacturers",
    __name__,
    url_prefix="/manufacturers",
    static_folder="static",
    template_folder="templates",
)


@bp.get("/")
@admin_rights_required
def read():
    return render_template(
        "manufacturers.j2",
        countries=db_get_countries(db),
        manufacturers=db_get_manufacturers(db),
    )


@bp.post("/")
@admin_rights_required
def create():
    form = ManufacturerAddForm(request.form.to_dict())
    if not form.is_valid:
        return redirect(request.referrer)

    try:
        db_add_manufacturer(db, form.country_name, form.company_name)
    except ModelError as error:
        flash_error(error)

    return redirect(request.referrer)


@bp.post("/<int:manufacturer_id>/delete")
@admin_rights_required
def delete(manufacturer_id: int):
    try:
        db_delete_manufacturer(db, manufacturer_id)
    except ModelError as error:
        flash_error(error)

    return redirect(request.referrer)
