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
    from blueprints.drugs import bp as drugs_bp
    from blueprints.manufacturers import bp as manufacturers_bp
    from blueprints.orders import bp as orders_bp
    from blueprints.pharmacy import bp as pharmacy_bp
    from blueprints.vendors import bp as vendors_bp

    app.register_blueprint(account_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(drugs_bp)
    app.register_blueprint(manufacturers_bp)
    app.register_blueprint(orders_bp)
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
