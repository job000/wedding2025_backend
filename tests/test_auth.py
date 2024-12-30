def test_register(client):
    response = client.post('/auth/register', json={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 201
    assert response.json["message"] == "User created successfully"

def test_login(client):
    client.post('/auth/register', json={
        "username": "testuser",
        "password": "testpassword"
    })
    response = client.post('/auth/login', json={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json
