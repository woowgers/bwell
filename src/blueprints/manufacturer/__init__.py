from flask import Blueprint


bp = Blueprint(
    "manufacturer",
    __name__,
    url_prefix="/manufacturer",
    static_folder="static",
    template_folder="templates",
)
