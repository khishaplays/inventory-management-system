
import requests

BASE_URL = "http://127.0.0.1:5000"
TIMEOUT = 15


def api_request(method, endpoint, **kwargs):
    """Send a request to the Flask API."""
    try:
        response = requests.request(
            method,
            f"{BASE_URL}{endpoint}",
            timeout=TIMEOUT,
            **kwargs
        )

        if response.status_code == 204:
            return True

        data = response.json()

        if not response.ok:
            print(f"\nError: {data.get('error', 'Request failed')}")
            return None

        return data

    except requests.ConnectionError:
        print("\nCannot connect to Flask. Is the server running?")
    except requests.Timeout:
        print("\nRequest timed out.")
    except requests.RequestException as error:
        print(f"\nRequest failed: {error}")
    except ValueError:
        print("\nThe server returned an invalid response.")

    return None


def display_product(product):
    """Display product details."""
    print("-" * 45)
    print(f"ID:          {product.get('id', 'External')}")
    print(f"Name:        {product.get('product_name', 'Unknown')}")
    print(f"Brand:       {product.get('brands', '')}")
    print(f"Barcode:     {product.get('barcode', '')}")
    print(f"Ingredients: {product.get('ingredients_text', '')}")

    if "price" in product:
        print(f"Price:       KSh {product['price']:.2f}")

    if "quantity" in product:
        print(f"Stock:       {product['quantity']}")

    print("-" * 45)


def read_integer(prompt, minimum=0):
    """Read a valid integer."""
    while True:
        try:
            value = int(input(prompt).strip())

            if value < minimum:
                print(f"Enter a number of at least {minimum}.")
                continue

            return value

        except ValueError:
            print("Please enter a valid whole number.")


def read_price(prompt):
    """Read a valid non-negative price."""
    while True:
        try:
            value = float(input(prompt).strip())

            if value < 0 or not value < float("inf"):
                print("Enter a valid non-negative price.")
                continue

            return value

        except ValueError:
            print("Please enter a valid price.")


def view_inventory():
    products = api_request("GET", "/inventory")

    if products is None:
        return

    if not products:
        print("\nInventory is empty.")
        return

    print(f"\nTotal products: {len(products)}")

    for product in products:
        display_product(product)


def view_product():
    item_id = read_integer("Enter product ID: ", minimum=1)

    product = api_request("GET", f"/inventory/{item_id}")

    if product is not None:
        display_product(product)


def add_product():
    print("\n--- Add New Product ---")

    name = input("Product name: ").strip()

    if not name:
        print("Product name cannot be empty.")
        return

    brand = input("Brand: ").strip()
    barcode = input("Barcode (optional): ").strip()
    ingredients = input("Ingredients (optional): ").strip()

    price = read_price("Price (KSh): ")
    quantity = read_integer("Quantity: ")

    product = {
        "product_name": name,
        "brands": brand,
        "barcode": barcode,
        "ingredients_text": ingredients,
        "price": price,
        "quantity": quantity
    }

    result = api_request("POST", "/inventory", json=product)

    if result is not None:
        print("\nProduct added successfully!")
        display_product(result)


def update_product():
    print("\n--- Update Product ---")

    item_id = read_integer("Product ID: ", minimum=1)

    existing = api_request("GET", f"/inventory/{item_id}")

    if existing is None:
        return

    display_product(existing)

    print("1. Update price")
    print("2. Update quantity")
    print("3. Update product name")
    print("4. Update brand")

    choice = input("Choose field: ").strip()

    if choice == "1":
        changes = {"price": read_price("New price: ")}

    elif choice == "2":
        changes = {"quantity": read_integer("New quantity: ")}

    elif choice == "3":
        name = input("New product name: ").strip()

        if not name:
            print("Product name cannot be empty.")
            return

        changes = {"product_name": name}

    elif choice == "4":
        changes = {"brands": input("New brand: ").strip()}

    else:
        print("Invalid selection.")
        return

    result = api_request(
        "PATCH",
        f"/inventory/{item_id}",
        json=changes
    )

    if result is not None:
        print("\nProduct updated successfully!")
        display_product(result)


def delete_product():
    print("\n--- Delete Product ---")

    item_id = read_integer("Product ID: ", minimum=1)

    product = api_request("GET", f"/inventory/{item_id}")

    if product is None:
        return

    display_product(product)

    confirmation = input(
        "Are you sure you want to delete this product? (yes/no): "
    ).strip().lower()

    if confirmation != "yes":
        print("Deletion cancelled.")
        return

    result = api_request("DELETE", f"/inventory/{item_id}")

    if result is True:
        print("\nProduct deleted successfully!")


def search_by_barcode():
    print("\n--- Search Open Food Facts by Barcode ---")

    barcode = input("Enter barcode: ").strip()

    if not barcode:
        print("Barcode cannot be empty.")
        return

    product = api_request(
        "GET",
        f"/external/products/{barcode}"
    )

    if product is not None:
        display_product(product)


def search_by_name():
    print("\n--- Search Open Food Facts by Name ---")

    name = input("Enter product name: ").strip()

    if not name:
        print("Product name cannot be empty.")
        return

    result = api_request(
        "GET",
        "/external/search",
        params={"name": name}
    )

    if result is None:
        return

    products = result.get("products", [])

    if not products:
        print("No matching products found.")
        return

    print(f"\nFound {len(products)} products:")

    for product in products:
        display_product(product)


def import_product():
    print("\n--- Import Product from Open Food Facts ---")

    barcode = input("Enter product barcode: ").strip()

    if not barcode:
        print("Barcode cannot be empty.")
        return

    product = api_request(
        "GET",
        f"/external/products/{barcode}"
    )

    if product is None:
        return

    print("\nExternal product found:")
    display_product(product)

    confirmation = input(
        "Import this product? (yes/no): "
    ).strip().lower()

    if confirmation != "yes":
        print("Import cancelled.")
        return

    price = read_price("Your selling price (KSh): ")
    quantity = read_integer("Starting stock quantity: ")

    result = api_request(
        "POST",
        f"/inventory/import/{barcode}",
        json={
            "price": price,
            "quantity": quantity
        }
    )

    if result is not None:
        print("\nProduct imported successfully!")
        display_product(result)


def show_menu():
    print("\n" + "=" * 45)
    print("       INVENTORY MANAGEMENT SYSTEM")
    print("=" * 45)
    print("1. View all inventory")
    print("2. View product by ID")
    print("3. Add new product")
    print("4. Update product")
    print("5. Delete product")
    print("6. Search external product by barcode")
    print("7. Search external products by name")
    print("8. Import external product")
    print("0. Exit")
    print("=" * 45)


def main():
    actions = {
        "1": view_inventory,
        "2": view_product,
        "3": add_product,
        "4": update_product,
        "5": delete_product,
        "6": search_by_barcode,
        "7": search_by_name,
        "8": import_product
    }

    while True:
        show_menu()

        choice = input("Select an option: ").strip()

        if choice == "0":
            print("\nThank you for using the Inventory Management System!")
            break

        action = actions.get(choice)

        if action is None:
            print("\nInvalid option. Please try again.")
            continue

        action()


if __name__ == "__main__":
    main()
