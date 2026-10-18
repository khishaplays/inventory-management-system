
import pytest
import app as inventory_app


@pytest.fixture
def client():
    inventory_app.app.config["TESTING"] = True

    original_inventory = [
        item.copy() for item in inventory_app.inventory
    ]
    original_next_id = inventory_app.next_id

    with inventory_app.app.test_client() as test_client:
        yield test_client

    # Restore state after each test
    inventory_app.inventory[:] = original_inventory
    inventory_app.next_id = original_next_id
