from http import HTTPStatus

from flask.testing import FlaskClient


def test_root(client: FlaskClient):
    response = client.get("/")
    assert response.status_code == HTTPStatus(200)
    assert '<h1> Welcome to BWell! </h1>' in response.text
