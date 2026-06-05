import requests

BASE_URL = "http://localhost:80"


def test_create_user():
    response = requests.post(
        f"{BASE_URL}/auth/signup",
        json={"email": "charlie@example.com", "username": "charlie", "password": "password123"}
    )

    assert response.status_code in [200, 201, 400]


def test_login():
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "charlie", "password": "password123", "grant_type": "password"}
    )

    assert response.status_code == 200

    data = response.json()
    access_token = data.get("access_token")
    token_type = data.get("token_type")

    global headers
    headers = {"Authorization": f"{token_type} {access_token}"} if access_token else {}


def test_profile():
    response = requests.get(f"{BASE_URL}/profile", headers=headers)

    assert response.status_code == 200

    global user_id
    user_id = response.json()["id"]


def test_read_all_users():
    response = requests.get(f"{BASE_URL}/users", headers=headers)
    assert response.status_code == 200


def test_read_single_user():
    response = requests.get(f"{BASE_URL}/users/{user_id}", headers=headers)
    assert response.status_code == 200


def test_update_user():
    response = requests.put(
        f"{BASE_URL}/users/{user_id}",
        json={"email": "charlie.new@example.com"},
        headers=headers
    )
    assert response.status_code == 200


def test_delete_user():
    response = requests.delete(f"{BASE_URL}/users/{user_id}", headers=headers)
    assert response.status_code in [200, 401]
