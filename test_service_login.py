import requests
import json

BASE_URL = "http://localhost:8000"

def test_register():
    """Test the registration endpoint"""
    print("\nTesting registration...")
    user_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    response = requests.post(
        f"{BASE_URL}/api/register",
        json=user_data
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_login():
    """Test the login endpoint"""
    print("\nTesting login...")
    response = requests.post(
        f"{BASE_URL}/api/login",
        params={
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json().get("access_token")

def test_service_login(token, service):
    """Test service-specific login"""
    print(f"\nTesting {service} login...")
    headers = {"Authorization": f"Bearer {token}"}
    login_data = {
        "email": f"test_{service}@example.com",
        "password": f"{service}_password",
        "api_key": f"test_{service}_key"
    }
    response = requests.post(
        f"{BASE_URL}/api/service/{service}/login",
        headers=headers,
        json=login_data
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_service_verify(token, service):
    """Test service-specific credential verification"""
    print(f"\nTesting {service} credential verification...")
    headers = {"Authorization": f"Bearer {token}"}
    login_data = {
        "email": f"test_{service}@example.com",
        "password": f"{service}_password"
    }
    response = requests.post(
        f"{BASE_URL}/api/service/{service}/verify",
        headers=headers,
        json=login_data
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_service_status(token, service):
    """Test service-specific status check"""
    print(f"\nTesting {service} status...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/service/{service}/status",
        headers=headers
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def main():
    print("Starting service login tests...")
    
    # Test registration
    if not test_register():
        print("Registration failed. Exiting...")
        return
    
    # Test login
    token = test_login()
    if not token:
        print("Login failed. Exiting...")
        return
    
    # Test each service
    services = ["openai", "gemini", "grok"]
    for service in services:
        # Test service login
        if not test_service_login(token, service):
            print(f"{service} login failed. Continuing with next service...")
            continue
        
        # Test service verification
        test_service_verify(token, service)
        
        # Test service status
        test_service_status(token, service)

if __name__ == "__main__":
    main() 