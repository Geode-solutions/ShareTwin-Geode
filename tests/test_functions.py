import os

ID = os.environ.get("ID")


def test_root(client):
    response = client.get("/healthcheck")
    assert response.status_code == 200


def test_createbackend(client):
    response = client.post("/sharetwin/createbackend")
    assert response.status_code == 200
    ID = response.json["ID"]
    assert ID == "123456"


def test_ping(client):
    response = client.post("/ping")
    assert response.status_code == 200


def test_delete_all_files(client):
    response = client.delete("/delete_all_files")
    assert response.status_code == 204
