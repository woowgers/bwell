from flask import Blueprint, render_template, redirect, url_for, request, flash

from helpers.flashes import *
from helpers.authority import *
from proxies import db
from db import *
from forms import DrugRegisterForm


bp = Blueprint(
    "drugs",
    __name__,
    url_prefix="/drugs",
    static_folder="static",
    template_folder="templates",
)


@bp.route("/")
@admin_rights_required
def read():
    manufacturers = db_get_manufacturers(db)
    if len(manufacturers) == 0:
        flash(
            """There are no manufacturers currently.
              You must create some manufacturers first to add drugs.""",
            category="info",
        )
    return render_template(
        "drugs.j2",
        drugs=db_get_drugs(db),
        drug_groups=db_get_drug_groups(db),
        manufacturers=manufacturers,
        drug_names=db_get_drug_names(db),
    )


@bp.post("/")
@admin_rights_required
def post():
    form = DrugRegisterForm(request.form.to_dict())
    if not form.is_valid:
        return redirect(url_for("drugs.read"))

    manufacturer = db_get_manufacturer_by_name(db, form.manufacturer_name)  # type: ignore
    if not manufacturer:
        flash_error(
            f'Manufacturer with company name "{form.manufacturer_name}" does not exist.'
        )
        return redirect(url_for("drugs.read"))

    try:
        db_add_drug(
            db,
            manufacturer.manufacturer_id,
            form.cipher,
            form.drug_group_name,
            form.drug_name,
        )
    except ModelError as error:
        flash_error(error)
        return redirect(request.referrer)

    return redirect(url_for("drugs.read"))


@bp.post("/delete-drug/<int:drug_id>")
@admin_rights_required
def delete_drug(drug_id):
    SQL_PROCEDURE = "drug_delete"

    try:
        db.callproc(SQL_PROCEDURE, (drug_id,))
    except DBIntegrityError as error:
        flash_error(f"Unexpected database error: {error}.")

    return redirect(url_for("drugs.read"))
