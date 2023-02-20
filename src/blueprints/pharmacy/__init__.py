from flask import Blueprint, render_template, request, redirect, session

from helpers.flashes import *
from helpers.authority import *
from db import *
from proxies import db

from forms import DrugFilterForm


bp = Blueprint(
    "pharmacy",
    __name__,
    url_prefix="/pharmacy",
    template_folder="templates",
    static_folder="static",
)


@bp.route("/")
def read():
    if 'pharmacy-items' not in session:
        items = db_get_pharmacy_items(db)
    else:
        items = session['pharmacy-items']

    return render_template(
        "pharmacy.j2",
        items=items,
        drug_groups=db_get_drug_groups(db)
    )


@bp.post("/filter")
def items_filtered():
    form = DrugFilterForm(request.form.to_dict())
    if not form.is_valid:
        return redirect(request.referrer)

    session['pharmacy-items'] = db_get_pharmacy_items_filtered(db, **form.fields)
    return redirect(request.referrer)
