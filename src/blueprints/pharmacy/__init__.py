from flask import Blueprint


bp = Blueprint(
    "pharmacy",
    __name__,
    url_prefix="/pharmacy",
    template_folder="templates",
    static_folder="static",
)
