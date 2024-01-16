from http import HTTPStatus

from flask.testing import FlaskClient


class TestLogin:
    def test_401(self, client: FlaskClient):
        with client:
            response = client.post(
                "/auth/login",
                data={"username": "flask"},
            )
            assert response.status_code == HTTPStatus(200)
