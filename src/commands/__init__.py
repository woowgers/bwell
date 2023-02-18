from flask import current_app
import click

from glob import glob

import shutil
import shlex
import os
import random
import string
from sqlalchemy.engine import create_engine
from sqlalchemy_utils import create_database, database_exists
from sqlalchemy import text


def gen_secret_key():
    return "".join(
        random.choices(string.ascii_letters + string.punctuation + string.digits, k=32)
    )


@click.command("init-instance", help="Initailize application instance folder")
def init_instance():
    environ = {}
    src_config_py_path = os.path.join(os.path.dirname(__file__), "config.py")
    dest_config_py_path = os.path.join(current_app.instance_path, "config.py")
    dotenv_path = os.path.join(current_app.instance_path, ".env")

    if not os.path.exists(current_app.instance_path):
        try:
            os.makedirs(current_app.instance_path)
        except OSError as error:
            click.echo(f"Failed to create instance folder: {error}.")

    if not os.path.exists(dest_config_py_path):
        try:
            shutil.copy(src_config_py_path, dest_config_py_path)
        except Exception as error:
            click.echo(f"Failed to copy `config.py` to instance folder: {error}")

    environ["BWELL_SECRET_KEY"] = shlex.quote(
        click.prompt(
            "Secret key (skip to generate randomly)",
            hide_input=True,
            default=gen_secret_key(),
            show_default=False,
            type=str,
        )
    )
    environ["BWELL_DB_HOST"] = shlex.quote(
        click.prompt("Database host", default="localhost", type=str)
    )
    environ["BWELL_DB_PORT"] = click.prompt("Database port", default=3306, type=int)
    environ["BWELL_DB_SCHEMA"] = shlex.quote(click.prompt("Datbase schema", type=str))
    environ["BWELL_DB_USER"] = shlex.quote(click.prompt("Database user", type=str))
    environ["BWELL_DB_PASSWORD"] = click.prompt(
        f"{environ['BWELL_DB_USER']} password", hide_input=True
    )

    with current_app.open_instance_resource(dotenv_path, "w") as dotenv:
        dotenv.write(
            "\n".join(map(lambda item: f"{item[0]}={item[1]}", environ.items()))
        )


@click.command("init-db", help="Initialize database from SQL source directory")
@click.argument("schema-directory", default="schema")
def init_db(schema_directory):
    db_config = current_app.config["DATABASE"]
    host = db_config["host"]
    port = db_config["port"]
    schema = db_config["database"]
    user = db_config["user"]
    password = db_config["password"]
    engine = create_engine(
        f"mysql+mysqldb://{user}:{password}@{host}:{port}/{schema}", pool_timeout=280
    )

    if not os.path.exists(schema_directory):
        schema_directory = os.path.join(current_app.root_path, schema_directory)

    paths = tuple(
        map(
            lambda f: os.path.join(schema_directory, f),
            sorted(glob("*.sql", root_dir=schema_directory)),
        )
    )
    if len(paths) == 0:
        click.echo(click.style(f"No sql files found in {schema_directory}", fg="red"))
        exit(1)

    if not database_exists(engine.url):
        click.echo(click.style(f"Database {schema} does not exist. Creating databse...", fg="yellow"))
        create_database(engine.url)

    click.echo(
        click.style(f"Executing SQL sources in following sequence:", fg="yellow")
    )
    for path in paths:
        click.echo(f"\t{path}")

    with engine.connect() as con:
        for path in paths:
            with current_app.open_resource(path) as f:
                code = f.read().decode("utf8")
            click.echo(click.style(f"Executing {path}...", fg="yellow"))
            try:
                con.execute(text(code))
            except Exception as error:
                click.echo(
                    click.style(f"Failed to execute {path}:", fg="red") + f"\n{error}"
                )
                exit(1)
        con.commit()
