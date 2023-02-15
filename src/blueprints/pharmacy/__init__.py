from flask import Blueprint, render_template, redirect, url_for, flash

from helpers.flashes import *
from helpers.authority import *
from db import *
from proxies import db, user


bp = Blueprint(
    "pharmacy",
    __name__,
    url_prefix="/pharmacy",
    template_folder="templates",
    static_folder="static",
)


@bp.route("/")
@admin_rights_required
def read():
    items = db_get_pharmacy_items(db)
    if len(items) == 0 and user and user.is_admin:
        flash(
            "There are no drugs currently. You should probably make some vendor-to-pharmacy orders.",
            category="info",
        )
    else:
        flash("Welcome to this spectacular page!", category="success")
    return render_template("pharmacy.j2", items=items)


@bp.route("/soyba")
@admin_rights_required
def soyba():
    items = db_get_pharmacy_items(db)
    if len(items) == 0:
        flash(
            "There are no drugs currently. You should probably make some vendor-to-pharmacy orders.",
            category="info",
        )
    return render_template("pharmacy.j2", items=items)
