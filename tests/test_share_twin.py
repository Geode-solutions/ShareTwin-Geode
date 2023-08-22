import os
import base64

from opengeodeweb_back import geode_objects

geode_objects_list = geode_objects.objects_list()

# ID = os.environ.get("ID")
base_route = f"/share_twin"


def test_allowed_files(client):
    response = client.get(f"{base_route}/allowed_files")
    assert response.status_code == 200
    extensions = response.json["extensions"]
    assert type(extensions) is list
    for extension in extensions:
        assert type(extension) == str


def test_allowed_objects(client):
    route = f"{base_route}/allowed_objects"

    # Normal test with filename 'corbi.og_brep'
    response = client.post(route, data={"filename": "corbi.og_brep"})
    assert response.status_code == 200
    allowed_objects = response.json["allowed_objects"]
    assert type(allowed_objects) is list
    assert "BRep" in allowed_objects

    # Normal test with filename .vtu
    response = client.post(route, data={"filename": "toto.vtu"})
    assert response.status_code == 200
    allowed_objects = response.json["allowed_objects"]
    list_objects = ["HybridSolid3D", "PolyhedralSolid3D", "TetrahedralSolid3D"]
    for geode_object in list_objects:
        assert geode_object in allowed_objects

    # Test with stupid filename
    response = client.post(route, data={"filename": "toto.tutu"})
    assert response.status_code == 200
    allowed_objects = response.json["allowed_objects"]
    assert type(allowed_objects) is list
    assert not allowed_objects

    # Test without filename
    response = client.post(route)
    assert response.status_code == 400
    description = response.json["description"]
    assert description == "No filename sent"


def test_geode_object_allowed_files(client):
    route = f"{base_route}/geode_object_allowed_files"

    # Normal test with geode_object
    response = client.post(route, data={"geode_object": "BRep"})
    assert response.status_code == 200
    allowed_objects = response.json["allowed_objects"]
    assert type(allowed_objects) is list
    assert "BRep" in allowed_objects

    # Normal test with filename .vtu
    response = client.post(route, data={"filename": "toto.vtu"})
    assert response.status_code == 200
    allowed_objects = response.json["allowed_objects"]
    list_objects = ["HybridSolid3D", "PolyhedralSolid3D", "TetrahedralSolid3D"]
    for geode_object in list_objects:
        assert geode_object in allowed_objects

    # Test with stupid filename
    response = client.post(route, data={"filename": "toto.tutu"})
    assert response.status_code == 200
    allowed_objects = response.json["allowed_objects"]
    assert type(allowed_objects) is list
    assert not allowed_objects

    # Test without filename
    response = client.post(route)
    assert response.status_code == 400
    description = response.json["description"]
    assert description == "No filename sent"


def test_geographic_coordinate_systems(client):
    route = f"{base_route}/geographic_coordinate_systems"

    # Normal test with geode_object 'BRep'
    response = client.get(route, data={"geode_object": "BRep"})
    assert response.status_code == 200
    crs_list = response.json["crs_list"]
    assert type(crs_list) is list
    for crs in crs_list:
        assert type(crs) is dict

    # Test without geode_object
    response = client.get(route)
    assert response.status_code == 400
    description = response.json["description"]
    assert description == "No geode_object sent"
