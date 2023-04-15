from flask import Blueprint


bp = Blueprint(
    "drug",
    __name__,
    url_prefix="/drug",
    static_folder="static",
    template_folder="templates",
)
