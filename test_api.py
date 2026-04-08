import requests

BASE_URL = "http://127.0.0.1:8000"

# Create a user
response = requests.post(
    f"{BASE_URL}/users",
    json={"email": "charlie@example.com", "username": "charlie"}
)
print(f"CREATE: {response.status_code}")
print(response.json())

user_id = response.json()["id"]

# Read all users
response = requests.get(f'{BASE_URL}/users')
print(f"\nREAD ALL: {response.status_code}")
print(response.json())

# Read single user
response = requests.get(f'{BASE_URL}/users/{user_id}')
print(f"\nREAD ONE: {response.status_code}")
print(response.json())

# UPDATE user
response = requests.put(
    f"{BASE_URL}/users/{user_id}",
    json={"email": "charlie.new@example.com"}
)
print(f"\nUPDATE: {response.status_code}")
print(response.json())

# DELETE user
response = requests.delete(f"{BASE_URL}/users/{user_id}")
print(f"\nDELETE: {response.status_code}")
