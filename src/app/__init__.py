from flask import Flask, render_template

from db import *
from helpers import *
from commands import init_db
from db.models import UserType
from proxies import close_db_proxy, user


def app_register_blueprints(app: Flask) -> None:
    from blueprints.account import bp as account_bp
    from blueprints.auth import bp as auth_bp
    from blueprints.cart import bp as cart_bp
    from blueprints.drug import bp as drug_bp
    from blueprints.manufacturer import bp as manufacturer_bp
    from blueprints.order import bp as order_bp
    from blueprints.pharmacy import bp as pharmacy_bp
    from blueprints.vendors import bp as vendors_bp

    app.register_blueprint(account_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(drug_bp)
    app.register_blueprint(manufacturer_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(pharmacy_bp)
    app.register_blueprint(vendors_bp)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_pyfile("config.py")
    app.jinja_env.globals.update(
        user=user, UserType=UserType, apostrophe_appended=apostrophe_appended
    )
    app.cli.add_command(init_db)

    app_register_blueprints(app)

    app.teardown_appcontext(close_db_proxy)

    @app.get("/")
    def read():  # pyright: ignore
        return render_template("index.j2")

    return app
