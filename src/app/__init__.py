import importlib
from pathlib import Path

from flask import Flask, render_template
import click

import os
import pkgutil

from db import *
from helpers import *
from commands import init_db, init_instance
from db.models import UserType
from proxies import close_db_proxy, user


ROOT_DIR = Path(__file__).parent.parent


def app_register_blueprints(app: Flask, blueprints_dir: str | Path) -> None:
    try:
        blueprints_module_name = os.path.basename(blueprints_dir)
        for _, module_name, is_package in pkgutil.iter_modules((blueprints_dir,)):
            if not is_package:
                continue
            full_module_name = f"{blueprints_module_name}.{module_name}"
            bp_module = __import__(full_module_name, fromlist=module_name)
            bp = getattr(bp_module, "bp")
            if bp:
                click.echo(
                    click.style(
                        f'Registering blueprint "{bp_module.__name__}"...', fg="yellow"
                    )
                )
                app.register_blueprint(bp)
            else:
                click.echo(
                    click.style(
                        f'Not found object "bp" in module {full_module_name}', fg="red"
                    )
                )

    except Exception as error:
        click.echo(
            click.style(
                "Failed to register blueprints:" + f"\n{error}", fg="red", bold=True
            )
        )
        return


def create_app() -> Flask:
    app = Flask(
        __name__,
    )
    app.config.from_pyfile(ROOT_DIR / 'app/config.py')
    app.jinja_env.globals.update(
        user=user, UserType=UserType, apostrophe_appended=apostrophe_appended
    )
    app.cli.add_command(init_instance)
    app.cli.add_command(init_db)

    app_register_blueprints(app, ROOT_DIR / "blueprints")

    app.teardown_appcontext(close_db_proxy)

    @app.get("/")
    def read():  # pyright: ignore
        return render_template("index.j2")

    return app
