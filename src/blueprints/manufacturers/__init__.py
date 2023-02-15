from flask import Blueprint, render_template, redirect, url_for, request

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


@bp.route("/")
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
        return redirect(url_for("manufacturers.read"))

    try:
        db_add_manufacturer(db, form.company_name, form.country_name)
    except ModelError as error:
        flash_error(error)

    return redirect(url_for("manufacturers.read"))


@bp.delete("/<int:manufacturer_id>")
def delete(manufacturer_id: int):
    try:
        db_delete_manufacturer(db, manufacturer_id)
    except ModelError as error:
        flash_error(error)

    return redirect(url_for("manufacturers.read"))
