import requests

def run_tests():
    base_url = "http://localhost:8000"

    signup_data = {
        "username": "john_doe2",
        "email": "john2@example.com",
        "password": "securepass1234",
        "full_name": "John Doe2"
    }
    response = requests.post(f"{base_url}/auth/signup", json=signup_data)
    print("Signup Response:", response.json())

    login_data = {
        "username": "john_doe",
        "password": "securepass123"
    }
    auth_response = requests.post(f"{base_url}/auth/login", json=login_data)
    token = auth_response.json()["access_token"]
    print("Login Token:", token)

    headers = {"Authorization": f"Bearer {token}"}

    book_data = {
        "title": "Python Programming",
        "author": "John Smith",
        "isbn": "978-0123456789",
        "category": "Programming",
        "total_copies": 5
    }
    requests.post(f"{base_url}/books", json=book_data, headers=headers)

    search_response = requests.get(f"{base_url}/books?category=Programming&available=true")
    print("Search Result:", search_response.json())

    borrow_data = {"book_id": 2, "user_id": 2}
    borrow_response = requests.post(f"{base_url}/loans", json=borrow_data, headers=headers)
    print("Borrow Response:", borrow_response.json())

    loans_response = requests.get(f"{base_url}/users/me/loans", headers=headers)
    print("My Loans:", loans_response.json())

if __name__ == "__main__":
    run_tests()
