from werkzeug.test import Client


def test_request_example(client: Client):
    response = client.get("/")
    assert b"<h1>Welcome to Bwell!</h1>" in response.data
