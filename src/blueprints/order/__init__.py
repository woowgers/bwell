from flask import Blueprint


bp = Blueprint(
    "order",
    __name__,
    url_prefix="/order",
    static_folder="static",
    template_folder="templates",
)
