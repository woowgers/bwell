from db import *
from helpers import *
from commands import init_db
from db.models import UserType
from proxies import close_db_proxy, user

from flask import Flask, render_template


def app_register_blueprints(app: Flask) -> None:
    from blueprints.account import bp as account_bp
    from blueprints.auth import bp as auth_bp

    app.register_blueprint(account_bp)
    app.register_blueprint(auth_bp)


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
