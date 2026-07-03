def test_create_product(client, auth_headers):
    r = client.post("/products", json={
        "name": "Indomie",
        "sku": "STK-FD-0001",
        "price": 500,
        "current_stock": 100,
        "min_stock_level": 20
    }, headers=auth_headers)
    assert r.status_code == 201
    assert r.json()["sku"] == "STK-FD-0001"


def test_list_products(client, auth_headers):
    client.post("/products", json={
        "name": "Indomie",
        "sku": "STK-FD-0001",
        "price": 500,
        "current_stock": 100,
        "min_stock_level": 20
    }, headers=auth_headers)
    r = client.get("/products", headers=auth_headers)
    assert len(r.json()) == 1