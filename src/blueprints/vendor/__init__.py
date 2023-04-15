from flask import Blueprint


bp = Blueprint(
    "vendor",
    __name__,
    url_prefix="/vendor",
    static_folder="static",
    template_folder="templates",
)
