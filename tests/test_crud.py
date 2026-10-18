
import pytest


def test_get_all_inventory(client):
    response = client.get("/inventory")

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)
    assert len(response.get_json()) >= 2


def test_get_single_item(client):
    response = client.get("/inventory/1")

    assert response.status_code == 200
    assert response.get_json()["id"] == 1
    assert response.get_json()["product_name"] == "Organic Almond Milk"


def test_get_missing_item(client):
    response = client.get("/inventory/9999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Item not found"


def test_create_item(client):
    product = {
        "product_name": "Chocolate Cookies",
        "brands": "Demo Brand",
        "price": 250,
        "quantity": 12
    }

    response = client.post("/inventory", json=product)

    assert response.status_code == 201
    assert response.get_json()["product_name"] == "Chocolate Cookies"
    assert response.get_json()["quantity"] == 12


def test_create_missing_required_field(client):
    response = client.post(
        "/inventory",
        json={"product_name": "Incomplete Product"}
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


@pytest.mark.parametrize("price", [-10, "invalid", True])
def test_reject_invalid_price(client, price):
    response = client.post(
        "/inventory",
        json={
            "product_name": "Invalid Product",
            "price": price,
            "quantity": 5
        }
    )

    assert response.status_code == 400


def test_reject_negative_quantity(client):
    response = client.post(
        "/inventory",
        json={
            "product_name": "Invalid Stock",
            "price": 100,
            "quantity": -2
        }
    )

    assert response.status_code == 400


def test_update_item(client):
    response = client.patch(
        "/inventory/1",
        json={"price": 400, "quantity": 8}
    )

    assert response.status_code == 200
    assert response.get_json()["price"] == 400
    assert response.get_json()["quantity"] == 8


def test_partial_update_preserves_other_fields(client):
    response = client.patch(
        "/inventory/1",
        json={"price": 500}
    )

    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Organic Almond Milk"
    assert response.get_json()["quantity"] == 20


def test_update_missing_item(client):
    response = client.patch(
        "/inventory/9999",
        json={"price": 300}
    )

    assert response.status_code == 404


def test_delete_item(client):
    response = client.delete("/inventory/2")

    assert response.status_code == 204
    assert client.get("/inventory/2").status_code == 404


def test_delete_missing_item(client):
    response = client.delete("/inventory/9999")

    assert response.status_code == 404


def test_invalid_json_body(client):
    response = client.post(
        "/inventory",
        data="not-json",
        content_type="application/json"
    )

    assert response.status_code == 400
