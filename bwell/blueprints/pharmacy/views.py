from flask import redirect, render_template, request, session

from bwell.db import *
from bwell.forms.forms import DrugFilterForm
from bwell.helpers.authority import *
from bwell.helpers.flashes import *
from bwell.proxies import db

from . import bp


@bp.route("/")
def all():
    if "pharmacy-items" not in session:
        items = db_get_pharmacy_items(db)
    else:
        items = session["pharmacy-items"]

    return render_template(
        "pharmacy.j2", items=items, drug_groups=db_get_drug_groups(db),
    )


@bp.post("/filter")
def items_filtered():
    form = DrugFilterForm(fields_dict=request.form.to_dict())
    if not form.is_valid:
        return redirect(request.referrer)

    session["pharmacy-items"] = db_get_pharmacy_items_filtered(
        db, **form.fields,
    )
    return redirect(request.referrer)
