from flask import current_app
import click

from glob import glob

import os
from sqlalchemy.engine import create_engine
from sqlalchemy import text


@click.command("init-db", help="Initialize database from SQL source directory")
@click.argument("schema-directory", default="schema")
def init_db(schema_directory):
    db_config = current_app.config['DATABASE']
    host = db_config['host']
    port = db_config['port']
    schema = db_config['database']
    user = db_config['user']
    password = db_config['password']
    engine = create_engine(
        f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{schema}", pool_timeout=280
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

    click.echo(
        click.style(f"Executing SQL sources in following sequence:", fg="yellow")
    )
    for path in paths:
        click.echo(f"\t{path}")

    click.echo(f"Connecting to PostgreSQL via URL: {engine.url}")
    with engine.connect() as con:
        for path in paths:
            with current_app.open_resource(path, mode='r') as f:
                code = f.read()
            click.echo(click.style(f"Executing {path}...", fg="yellow"))
            try:
                con.execute(text(code))
            except Exception as error:
                click.echo(
                    click.style(f"Failed to execute {path}:", fg="red") + f"\n{error}"
                )
                raise
        con.commit()
