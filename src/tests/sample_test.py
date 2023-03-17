import pytest
from ..app import create_app

from werkzeug.test import Client


@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True
    })

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_request_example(client: Client):
    response = client.get("/")
    assert b"<h1>Welcome to Bwell!</h1>" in response.data
