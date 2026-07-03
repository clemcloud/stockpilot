import pytest


@pytest.fixture
def product(client, auth_headers):
    r = client.post("/products", json={
        "name": "Indomie",
        "sku": "STK-FD-0001",
        "price": 500,
        "current_stock": 50,
        "min_stock_level": 10
    }, headers=auth_headers)
    return r.json()


def test_process_sale(client, product):
    r = client.post("/sales", json={
        "payment_method": "CASH",
        "items": [{"product_id": product["id"], "quantity": 5}]
    })
    assert r.status_code == 201
    assert "receipt_number" in r.json()


def test_insufficient_stock(client, product):
    r = client.post("/sales", json={
        "payment_method": "CASH",
        "items": [{"product_id": product["id"], "quantity": 999}]
    })
    assert r.status_code == 400