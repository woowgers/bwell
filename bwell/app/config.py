import os

from dotenv import load_dotenv

load_dotenv("../../.env")


SECRET_KEY = os.environ.get("SECRET_KEY")

DATABASE = {
    key: os.environ.get(environ, default)
    for key, environ, default in (
        ('host', 'POSTGRES_HOST', 'localhost'),
        ('port', 'POSTGRES_PORT', 5432),
        ('database', 'POSTGRES_DB', 'bwell'),
        ('user', 'POSTGRES_USER', 'bwell'),
        ('password', 'POSTGRES_PASSWORD', 'qwe!@#3((!#$))'),
    )
}
