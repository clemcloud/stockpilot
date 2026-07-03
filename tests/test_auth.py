def test_login_success(client):
    client.post("/users", json={
        "username": "manager",
        "email": "manager@test.com",
        "password": "password123"
    })
    # CHANGED: Use data= instead of json= for form parameters
    r = client.post("/auth/login", data={
        "username": "manager",
        "password": "password123"
    })
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_wrong_password(client):
    client.post("/users", json={
        "username": "manager",
        "email": "manager@test.com",
        "password": "password123"
    })
    # CHANGED: Use data= instead of json= for form parameters
    r = client.post("/auth/login", data={
        "username": "manager",
        "password": "wrongpassword"
    })
    assert r.status_code == 401