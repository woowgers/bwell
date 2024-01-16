from flask import Blueprint, redirect, render_template, request, url_for

from bwell.db import *
from bwell.forms.forms import DrugRegisterForm
from bwell.helpers.authority import *
from bwell.helpers.flashes import *
from bwell.proxies import db

bp = Blueprint(
    "drug",
    __name__,
    url_prefix="/drug",
    static_folder="static",
    template_folder="templates",
)


@bp.route("/")
@admin_rights_required
def all():
    manufacturers = db_get_manufacturers(db)
    if len(manufacturers) == 0:
        flash_info(
            """There are no manufacturers currently.
              You must create some manufacturers first to add drugs.""",
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
    form = DrugRegisterForm(fields_dict=request.form.to_dict())
    if not form.is_valid:
        return redirect(request.referrer)

    manufacturer = db_get_manufacturer_by_name(db, form.manufacturer_name)
    if not manufacturer:
        flash_error(
            f'Manufacturer with company name "{form.manufacturer_name}" does not exist.',
        )
        return redirect(request.referrer)

    with ModelWebUIContext():
        db_add_drug(
            db,
            manufacturer.manufacturer_id,
            form.cipher,
            form.drug_group_name,
            form.drug_name,
        )

    return redirect(request.referrer)


@bp.post("/delete/<int:drug_id>")
@admin_rights_required
def delete(drug_id):
    with ModelWebUIContext():
        db_delete_drug(db, drug_id)
    return redirect(url_for("drug.all"))
