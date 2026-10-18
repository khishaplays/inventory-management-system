
from unittest.mock import Mock

import pytest
import requests

import cli


SAMPLE_PRODUCT = {
    "id": 3,
    "product_name": "Nutella",
    "brands": "Ferrero",
    "barcode": "3017620422003",
    "ingredients_text": "Sugar, hazelnuts, cocoa",
    "price": 650.0,
    "quantity": 25
}


def test_api_request_success(monkeypatch):
    response = Mock()
    response.status_code = 200
    response.ok = True
    response.json.return_value = [SAMPLE_PRODUCT]

    monkeypatch.setattr(
        cli.requests, "request",
        lambda *args, **kwargs: response
    )

    result = cli.api_request("GET", "/inventory")

    assert result == [SAMPLE_PRODUCT]


def test_api_request_delete_success(monkeypatch):
    response = Mock()
    response.status_code = 204

    monkeypatch.setattr(
        cli.requests, "request",
        lambda *args, **kwargs: response
    )

    assert cli.api_request("DELETE", "/inventory/3") is True


def test_api_request_error(monkeypatch, capsys):
    response = Mock()
    response.status_code = 404
    response.ok = False
    response.json.return_value = {
        "error": "Item not found"
    }

    monkeypatch.setattr(
        cli.requests, "request",
        lambda *args, **kwargs: response
    )

    result = cli.api_request("GET", "/inventory/999")

    assert result is None
    assert "Item not found" in capsys.readouterr().out


def test_api_request_connection_error(monkeypatch, capsys):
    def fail(*args, **kwargs):
        raise requests.ConnectionError("Server unavailable")

    monkeypatch.setattr(cli.requests, "request", fail)

    assert cli.api_request("GET", "/inventory") is None
    assert "Cannot connect" in capsys.readouterr().out


def test_view_inventory(monkeypatch, capsys):
    monkeypatch.setattr(
        cli, "api_request",
        lambda method, endpoint, **kwargs: [SAMPLE_PRODUCT]
    )

    cli.view_inventory()

    output = capsys.readouterr().out

    assert "Total products: 1" in output
    assert "Nutella" in output


def test_view_empty_inventory(monkeypatch, capsys):
    monkeypatch.setattr(
        cli, "api_request",
        lambda method, endpoint, **kwargs: []
    )

    cli.view_inventory()

    assert "Inventory is empty" in capsys.readouterr().out


def test_add_product(monkeypatch, capsys):
    answers = iter([
        "Kenyan Coffee",
        "Kenyan Brand",
        "123456789",
        "Coffee beans",
        "850",
        "12"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": next(answers)
    )

    captured = {}

    def fake_request(method, endpoint, **kwargs):
        captured["method"] = method
        captured["endpoint"] = endpoint
        captured["payload"] = kwargs["json"]
        return {**kwargs["json"], "id": 4}

    monkeypatch.setattr(cli, "api_request", fake_request)

    cli.add_product()

    assert captured["method"] == "POST"
    assert captured["endpoint"] == "/inventory"
    assert captured["payload"]["price"] == 850
    assert captured["payload"]["quantity"] == 12
    assert "successfully" in capsys.readouterr().out


def test_update_product(monkeypatch):
    answers = iter(["3", "2", "30"])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": next(answers)
    )

    calls = []

    def fake_request(method, endpoint, **kwargs):
        calls.append((method, endpoint, kwargs))

        if method == "GET":
            return SAMPLE_PRODUCT.copy()

        return {**SAMPLE_PRODUCT, **kwargs["json"]}

    monkeypatch.setattr(cli, "api_request", fake_request)

    cli.update_product()

    assert calls[-1][0] == "PATCH"
    assert calls[-1][1] == "/inventory/3"
    assert calls[-1][2]["json"] == {"quantity": 30}


def test_delete_product(monkeypatch, capsys):
    answers = iter(["3", "yes"])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": next(answers)
    )

    calls = []

    def fake_request(method, endpoint, **kwargs):
        calls.append(method)

        if method == "GET":
            return SAMPLE_PRODUCT.copy()

        return True

    monkeypatch.setattr(cli, "api_request", fake_request)

    cli.delete_product()

    assert calls == ["GET", "DELETE"]
    assert "deleted successfully" in capsys.readouterr().out


def test_delete_cancelled(monkeypatch):
    answers = iter(["3", "no"])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": next(answers)
    )

    calls = []

    def fake_request(method, endpoint, **kwargs):
        calls.append(method)
        return SAMPLE_PRODUCT.copy()

    monkeypatch.setattr(cli, "api_request", fake_request)

    cli.delete_product()

    assert calls == ["GET"]


def test_search_by_barcode(monkeypatch, capsys):
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": "3017620422003"
    )

    monkeypatch.setattr(
        cli, "api_request",
        lambda method, endpoint, **kwargs: SAMPLE_PRODUCT.copy()
    )

    cli.search_by_barcode()

    assert "Nutella" in capsys.readouterr().out


def test_search_by_name(monkeypatch, capsys):
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": "Nutella"
    )

    monkeypatch.setattr(
        cli, "api_request",
        lambda method, endpoint, **kwargs: {
            "count": 1,
            "products": [SAMPLE_PRODUCT.copy()]
        }
    )

    cli.search_by_name()

    assert "Found 1 products" in capsys.readouterr().out


def test_import_product(monkeypatch, capsys):
    answers = iter([
        "3017620422003",
        "yes",
        "650",
        "25"
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": next(answers)
    )

    calls = []

    def fake_request(method, endpoint, **kwargs):
        calls.append((method, endpoint, kwargs))
        return SAMPLE_PRODUCT.copy()

    monkeypatch.setattr(cli, "api_request", fake_request)

    cli.import_product()

    assert calls[0][0] == "GET"
    assert calls[1][0] == "POST"
    assert calls[1][1] == "/inventory/import/3017620422003"
    assert calls[1][2]["json"] == {
        "price": 650.0,
        "quantity": 25
    }

    assert "imported successfully" in capsys.readouterr().out


def test_read_integer_retries_invalid_input(monkeypatch):
    answers = iter(["abc", "-5", "10"])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": next(answers)
    )

    assert cli.read_integer("Quantity: ") == 10


def test_read_price_retries_invalid_input(monkeypatch):
    answers = iter(["invalid", "-10", "250.50"])

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": next(answers)
    )

    assert cli.read_price("Price: ") == 250.50


def test_main_exit(monkeypatch, capsys):
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": "0"
    )

    cli.main()

    assert "Thank you" in capsys.readouterr().out
