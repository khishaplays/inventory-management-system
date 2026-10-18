
from flask import Flask, jsonify, request

app = Flask(__name__)

# Temporary in-memory inventory storage
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


def find_item(item_id):
    """Find an inventory item by its ID."""
    return next(
        (item for item in inventory if item["id"] == item_id),
        None
    )


def validate_fields(data, partial=False):
    """Validate incoming inventory data."""
    if not isinstance(data, dict):
        return "A JSON object is required."

    required_fields = ["product_name", "price", "quantity"]

    if not partial:
        for field in required_fields:
            if field not in data:
                return f"Missing required field: {field}"

    allowed_fields = {
        "product_name", "brands", "barcode",
        "ingredients_text", "price", "quantity"
    }

    for field, value in data.items():
        if field not in allowed_fields:
            return f"Unknown field: {field}"

        if field in {"product_name", "brands", "barcode", "ingredients_text"}:
            if not isinstance(value, str):
                return f"{field} must be a string."

        if field == "product_name" and not value.strip():
            return "Product name cannot be empty."

        if field == "price":
            if type(value) not in (int, float) or value < 0:
                return "Price must be a non-negative number."

        if field == "quantity":
            if type(value) is not int or value < 0:
                return "Quantity must be a non-negative integer."

    return None


@app.get("/")
def home():
    return jsonify({
        "message": "Welcome to the Inventory Management API",
        "endpoints": [
            "GET /inventory",
            "GET /inventory/<id>",
            "POST /inventory",
            "PATCH /inventory/<id>",
            "DELETE /inventory/<id>"
        ]
    }), 200


# READ: Get all inventory items
@app.get("/inventory")
def get_inventory():
    return jsonify(inventory), 200


# READ: Get one inventory item
@app.get("/inventory/<int:item_id>")
def get_item(item_id):
    item = find_item(item_id)

    if item is None:
        return jsonify({"error": "Item not found"}), 404

    return jsonify(item), 200


# CREATE: Add a new inventory item
@app.post("/inventory")
def add_item():
    global next_id

    data = request.get_json(silent=True)
    error = validate_fields(data)

    if error:
        return jsonify({"error": error}), 400

    new_item = {
        "id": next_id,
        "product_name": data["product_name"],
        "brands": data.get("brands", ""),
        "barcode": data.get("barcode", ""),
        "ingredients_text": data.get("ingredients_text", ""),
        "price": float(data["price"]),
        "quantity": data["quantity"]
    }

    inventory.append(new_item)
    next_id += 1

    return jsonify(new_item), 201


# UPDATE: Partially update an existing item
@app.patch("/inventory/<int:item_id>")
def update_item(item_id):
    item = find_item(item_id)

    if item is None:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json(silent=True)
    error = validate_fields(data, partial=True)

    if error:
        return jsonify({"error": error}), 400

    for field, value in data.items():
        item[field] = float(value) if field == "price" else value

    return jsonify(item), 200


# DELETE: Remove an inventory item
@app.delete("/inventory/<int:item_id>")
def delete_item(item_id):
    item = find_item(item_id)

    if item is None:
        return jsonify({"error": "Item not found"}), 404

    inventory.remove(item)

    return "", 204


if __name__ == "__main__":
    app.run(debug=True)
