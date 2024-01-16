from flask import Blueprint


bp = Blueprint(
    "cart",
    __name__,
    url_prefix="/cart",
    template_folder="templates",
    static_folder="static",
)
