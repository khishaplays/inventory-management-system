
import requests

BASE_URL = "https://world.openfoodfacts.org"
HEADERS = {
    "User-Agent": "KhishaInventoryLab/1.0 (educational project)"
}


def normalize_product(product):
    """Convert Open Food Facts data into inventory fields."""
    return {
        "product_name": product.get("product_name") or "Unknown Product",
        "brands": product.get("brands") or "",
        "barcode": str(product.get("code") or ""),
        "ingredients_text": product.get("ingredients_text") or ""
    }


def get_product_by_barcode(barcode):
    """Fetch a product using its barcode."""
    url = f"{BASE_URL}/api/v2/product/{barcode}.json"

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        if data.get("status") != 1:
            return None

        product = data.get("product")

        if not isinstance(product, dict):
            return None

        return normalize_product(product)

    except (requests.RequestException, ValueError) as error:
        raise RuntimeError(
            f"Open Food Facts request failed: {error}"
        ) from error


def search_products_by_name(name, limit=5):
    """Search Open Food Facts by product name."""
    url = f"{BASE_URL}/cgi/search.pl"

    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": limit
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers=HEADERS,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        return [
            normalize_product(product)
            for product in data.get("products", [])
            if isinstance(product, dict)
        ]

    except (requests.RequestException, ValueError) as error:
        raise RuntimeError(
            f"Open Food Facts request failed: {error}"
        ) from error
