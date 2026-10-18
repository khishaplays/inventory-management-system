
from unittest.mock import Mock

import pytest
import requests

import app as inventory_app
import external_api


SAMPLE_PRODUCT = {
    "product_name": "Nutella",
    "brands": "Nutella, Ferrero",
    "barcode": "3017620422003",
    "ingredients_text": "Sugar, hazelnuts, cocoa"
}


# =========================================================
# TEST OPEN FOOD FACTS API FUNCTIONS
# =========================================================

def test_barcode_lookup_success(monkeypatch):
    fake_response = Mock()
    fake_response.raise_for_status.return_value = None
    fake_response.json.return_value = {
        "status": 1,
        "product": {
            "code": "3017620422003",
            "product_name": "Nutella",
            "brands": "Nutella, Ferrero",
            "ingredients_text": "Sugar, hazelnuts, cocoa"
        }
    }

    monkeypatch.setattr(
        external_api.requests,
        "get",
        lambda *args, **kwargs: fake_response
    )

    product = external_api.get_product_by_barcode(
        "3017620422003"
    )

    assert product == SAMPLE_PRODUCT


def test_barcode_lookup_not_found(monkeypatch):
    fake_response = Mock()
    fake_response.raise_for_status.return_value = None
    fake_response.json.return_value = {
        "status": 0,
        "product": {}
    }

    monkeypatch.setattr(
        external_api.requests,
        "get",
        lambda *args, **kwargs: fake_response
    )

    result = external_api.get_product_by_barcode("000000")

    assert result is None


def test_barcode_lookup_network_failure(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.ConnectionError("Connection failed")

    monkeypatch.setattr(
        external_api.requests,
        "get",
        fake_get
    )

    with pytest.raises(RuntimeError):
        external_api.get_product_by_barcode("3017620422003")


def test_product_name_search(monkeypatch):
    fake_response = Mock()
    fake_response.raise_for_status.return_value = None
    fake_response.json.return_value = {
        "products": [
            {
                "code": "3017620422003",
                "product_name": "Nutella",
                "brands": "Nutella, Ferrero",
                "ingredients_text": "Sugar, hazelnuts, cocoa"
            }
        ]
    }

    monkeypatch.setattr(
        external_api.requests,
        "get",
        lambda *args, **kwargs: fake_response
    )

    products = external_api.search_products_by_name("Nutella")

    assert len(products) == 1
    assert products[0]["product_name"] == "Nutella"


# =========================================================
# TEST FLASK EXTERNAL API ENDPOINTS
# =========================================================

def test_external_barcode_endpoint(client, monkeypatch):
    monkeypatch.setattr(
        inventory_app,
        "get_product_by_barcode",
        lambda barcode: SAMPLE_PRODUCT.copy()
    )

    response = client.get(
        "/external/products/3017620422003"
    )

    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Nutella"


def test_external_barcode_not_found(client, monkeypatch):
    monkeypatch.setattr(
        inventory_app,
        "get_product_by_barcode",
        lambda barcode: None
    )

    response = client.get("/external/products/000000")

    assert response.status_code == 404


def test_external_search_endpoint(client, monkeypatch):
    monkeypatch.setattr(
        inventory_app,
        "search_products_by_name",
        lambda name: [SAMPLE_PRODUCT.copy()]
    )

    response = client.get("/external/search?name=Nutella")

    assert response.status_code == 200
    assert response.get_json()["count"] == 1


def test_external_search_missing_name(client):
    response = client.get("/external/search")

    assert response.status_code == 400


def test_external_service_failure(client, monkeypatch):
    def failed_lookup(barcode):
        raise RuntimeError("External service unavailable")

    monkeypatch.setattr(
        inventory_app,
        "get_product_by_barcode",
        failed_lookup
    )

    response = client.get(
        "/external/products/3017620422003"
    )

    assert response.status_code == 502


# =========================================================
# TEST IMPORTING EXTERNAL PRODUCTS
# =========================================================

def test_import_external_product(client, monkeypatch):
    monkeypatch.setattr(
        inventory_app,
        "get_product_by_barcode",
        lambda barcode: SAMPLE_PRODUCT.copy()
    )

    response = client.post(
        "/inventory/import/3017620422003",
        json={
            "price": 650,
            "quantity": 25
        }
    )

    assert response.status_code == 201

    product = response.get_json()

    assert product["product_name"] == "Nutella"
    assert product["price"] == 650.0
    assert product["quantity"] == 25

    saved = client.get(f"/inventory/{product['id']}")

    assert saved.status_code == 200
    assert saved.get_json()["barcode"] == "3017620422003"


def test_import_missing_product(client, monkeypatch):
    monkeypatch.setattr(
        inventory_app,
        "get_product_by_barcode",
        lambda barcode: None
    )

    response = client.post(
        "/inventory/import/000000",
        json={"price": 100, "quantity": 5}
    )

    assert response.status_code == 404


def test_import_invalid_quantity(client, monkeypatch):
    monkeypatch.setattr(
        inventory_app,
        "get_product_by_barcode",
        lambda barcode: SAMPLE_PRODUCT.copy()
    )

    response = client.post(
        "/inventory/import/3017620422003",
        json={"price": 650, "quantity": -5}
    )

    assert response.status_code == 400


def test_import_external_service_failure(client, monkeypatch):
    def failed_lookup(barcode):
        raise RuntimeError("External service unavailable")

    monkeypatch.setattr(
        inventory_app,
        "get_product_by_barcode",
        failed_lookup
    )

    response = client.post(
        "/inventory/import/3017620422003",
        json={"price": 650, "quantity": 25}
    )

    assert response.status_code == 502
