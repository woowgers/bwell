from flask import Flask, redirect, render_template, url_for

from bwell.app.helpers import app_get_endpoints
from bwell.commands import init_db
from bwell.db import *
from bwell.db.models import UserType
from bwell.helpers import *
from bwell.proxies import close_db_proxy, user


def app_register_blueprints(app: Flask) -> None:
    from bwell.blueprints.account import bp as account_bp
    from bwell.blueprints.auth import bp as auth_bp
    from bwell.blueprints.cart import bp as cart_bp
    from bwell.blueprints.drug import bp as drug_bp
    from bwell.blueprints.manufacturer import bp as manufacturer_bp
    from bwell.blueprints.order import bp as order_bp
    from bwell.blueprints.pharmacy import bp as pharmacy_bp
    from bwell.blueprints.vendor import bp as vendor_bp

    app.register_blueprint(account_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(drug_bp)
    app.register_blueprint(manufacturer_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(pharmacy_bp)
    app.register_blueprint(vendor_bp)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_pyfile("config.py")
    app.jinja_env.globals.update(
        user=user,
        UserType=UserType,
        apostrophe_appended=apostrophe_appended,
    )
    app.cli.add_command(init_db)

    app_register_blueprints(app)

    app.teardown_appcontext(close_db_proxy)

    @app.get("/")
    def read():
        return render_template("index.j2")

    @app.get("/site_map")
    def site_map():
        endpoints = app_get_endpoints(app)
        return render_template(
            "site-map.j2",
            endpoints=endpoints,
        )

    return app
