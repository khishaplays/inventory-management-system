
from flask import Flask, jsonify, request

from external_api import (
    get_product_by_barcode,
    search_products_by_name
)


app = Flask(__name__)


# =========================================================
# TEMPORARY INVENTORY DATABASE
# =========================================================

inventory = [
    {
        "id": 1,
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "barcode": "1234567890123",
        "ingredients_text": "Filtered water, almonds, cane sugar",
        "price": 350.0,
        "quantity": 20
    },
    {
        "id": 2,
        "product_name": "Whole Wheat Bread",
        "brands": "Healthy Bakery",
        "barcode": "9876543210987",
        "ingredients_text": "Whole wheat flour, water, yeast",
        "price": 180.0,
        "quantity": 15
    }
]

next_id = 3


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def find_item(item_id):
    """Find an inventory item by its unique ID."""
    return next(
        (item for item in inventory if item["id"] == item_id),
        None
    )


def validate_fields(data, partial=False):
    """Validate product data before adding or updating it."""

    if not isinstance(data, dict):
        return "A JSON object is required."

    required_fields = [
        "product_name",
        "price",
        "quantity"
    ]

    if not partial:
        for field in required_fields:
            if field not in data:
                return f"Missing required field: {field}"

    allowed_fields = {
        "product_name",
        "brands",
        "barcode",
        "ingredients_text",
        "price",
        "quantity"
    }

    for field, value in data.items():

        if field not in allowed_fields:
            return f"Unknown field: {field}"

        if field in {
            "product_name",
            "brands",
            "barcode",
            "ingredients_text"
        }:
            if not isinstance(value, str):
                return f"{field} must be a string."

        if field == "product_name":
            if not value.strip():
                return "Product name cannot be empty."

        if field == "price":
            if (
                type(value) not in (int, float)
                or value < 0
            ):
                return "Price must be a non-negative number."

        if field == "quantity":
            if type(value) is not int or value < 0:
                return "Quantity must be a non-negative integer."

    return None


# =========================================================
# HOME ROUTE
# =========================================================

@app.get("/")
def home():
    """Display API information and available endpoints."""

    return jsonify({
        "message": "Welcome to the Inventory Management API",
        "description": (
            "A Flask REST API for managing retail inventory "
            "with Open Food Facts integration."
        ),
        "endpoints": [
            "GET /inventory",
            "GET /inventory/<id>",
            "POST /inventory",
            "PATCH /inventory/<id>",
            "DELETE /inventory/<id>",
            "GET /external/products/<barcode>",
            "GET /external/search?name=<product_name>",
            "POST /inventory/import/<barcode>"
        ]
    }), 200


# =========================================================
# READ ALL INVENTORY ITEMS
# =========================================================

@app.get("/inventory")
def get_inventory():
    """Return all products in the inventory."""

    return jsonify(inventory), 200


# READ A SINGLE INVENTORY ITEM

@app.get("/inventory/<int:item_id>")
def get_item(item_id):
    """Return a specific product by its ID."""

    item = find_item(item_id)

    if item is None:
        return jsonify({
            "error": "Item not found"
        }), 404

    return jsonify(item), 200



@app.post("/inventory")
def add_item():
    """Add a new product to the inventory."""

    global next_id

    data = request.get_json(silent=True)

    error = validate_fields(data)

    if error:
        return jsonify({
            "error": error
        }), 400

    new_item = {
        "id": next_id,
        "product_name": data["product_name"],
        "brands": data.get("brands", ""),
        "barcode": data.get("barcode", ""),
        "ingredients_text": data.get(
            "ingredients_text", ""
        ),
        "price": float(data["price"]),
        "quantity": data["quantity"]
    }

    inventory.append(new_item)
    next_id += 1

    return jsonify(new_item), 201



@app.patch("/inventory/<int:item_id>")
def update_item(item_id):
    """Update one or more fields of an existing product."""

    item = find_item(item_id)

    if item is None:
        return jsonify({
            "error": "Item not found"
        }), 404

    data = request.get_json(silent=True)

    error = validate_fields(data, partial=True)

    if error:
        return jsonify({
            "error": error
        }), 400

    for field, value in data.items():

        if field == "price":
            item[field] = float(value)
        else:
            item[field] = value

    return jsonify(item), 200



@app.delete("/inventory/<int:item_id>")
def delete_item(item_id):
    """Delete an existing product from inventory."""

    item = find_item(item_id)

    if item is None:
        return jsonify({
            "error": "Item not found"
        }), 404

    inventory.remove(item)

    return "", 204


 
# OPEN FOOD FACTS: LOOKUP BY BARCODE
 

@app.get("/external/products/<barcode>")
def external_product_lookup(barcode):
    """Retrieve product information from Open Food Facts."""

    try:
        product = get_product_by_barcode(barcode)

        if product is None:
            return jsonify({
                "error": "External product not found"
            }), 404

        return jsonify(product), 200

    except RuntimeError as error:
        return jsonify({
            "error": str(error)
        }), 502


# OPEN FOOD FACTS: SEARCH BY PRODUCT NAME

@app.get("/external/search")
def external_product_search():
    """Search Open Food Facts using a product name."""

    name = request.args.get("name", "").strip()

    if not name:
        return jsonify({
            "error": "Product name is required"
        }), 400

    try:
        products = search_products_by_name(name)

        return jsonify({
            "count": len(products),
            "products": products
        }), 200

    except RuntimeError as error:
        return jsonify({
            "error": str(error)
        }), 502


# IMPORT EXTERNAL PRODUCT INTO INVENTORY

@app.post("/inventory/import/<barcode>")
def import_external_product(barcode):
    """
    Retrieve a product from Open Food Facts and
    save it in the local inventory.
    """

    global next_id

    data = request.get_json(silent=True)

    if data is None:
        data = {}

    if not isinstance(data, dict):
        return jsonify({
            "error": "A JSON object is required"
        }), 400

    # The retailer supplies their own price and stock.
    price = data.get("price", 0)
    quantity = data.get("quantity", 0)

    error = validate_fields(
        {
            "price": price,
            "quantity": quantity
        },
        partial=True
    )

    if error:
        return jsonify({
            "error": error
        }), 400

    try:
        product = get_product_by_barcode(barcode)

        if product is None:
            return jsonify({
                "error": "External product not found"
            }), 404

        new_item = {
            "id": next_id,
            "product_name": product["product_name"],
            "brands": product["brands"],
            "barcode": product["barcode"],
            "ingredients_text": product["ingredients_text"],
            "price": float(price),
            "quantity": quantity
        }

        inventory.append(new_item)
        next_id += 1

        return jsonify(new_item), 201

    except RuntimeError as error:
        return jsonify({
            "error": str(error)
        }), 502



if __name__ == "__main__":
    app.run(debug=True)
