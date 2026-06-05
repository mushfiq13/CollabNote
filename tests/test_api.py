import requests

BASE_URL = "http://localhost:80"

# Create a user
response = requests.post(
    f"{BASE_URL}/auth/signup",
    json={"email": "charlie@example.com", "username": "charlie", "password": "password123"}
)
print(f"CREATE: {response.status_code}")
print(response.json())

# Login
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "charlie", "password": "password123", "grant_type": "password"}
)
print(f"LOGIN: {response.status_code}")
print(response.json())

access_token = response.json().get("access_token")
token_type = response.json().get("token_type")
headers = {"Authorization": f"{token_type} {access_token}"} if access_token else {}

# Get profile
response = requests.get(f'{BASE_URL}/profile', headers=headers)
print(response.json())
user_id = response.json()["id"]

# Read all users
response = requests.get(f'{BASE_URL}/users', headers=headers)
print(f"\nREAD ALL: {response.status_code}")
print(response.json())

# Read single user
response = requests.get(f'{BASE_URL}/users/{user_id}', headers=headers)
print(f"\nREAD ONE: {response.status_code}")
print(response.json())

# UPDATE user
response = requests.put(
    f"{BASE_URL}/users/{user_id}",
    json={"email": "charlie.new@example.com"},
    headers=headers
)
print(f"\nUPDATE: {response.status_code}")
print(response.json())

# DELETE user
response = requests.delete(f"{BASE_URL}/users/{user_id}", headers=headers)
print(f"\nDELETE: {response.status_code}")
