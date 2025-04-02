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

def test_save_api_keys(token):
    """Test saving API keys"""
    print("\nTesting save API keys...")
    headers = {"Authorization": f"Bearer {token}"}
    api_keys = {
        "openai_key": "your-openai-key",
        "gemini_key": "your-gemini-key",
        "grok_key": "your-grok-key"
    }
    response = requests.post(
        f"{BASE_URL}/api/save-api-keys",
        headers=headers,
        json=api_keys
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

def test_chat(token):
    """Test the chat endpoint"""
    print("\nTesting chat...")
    headers = {"Authorization": f"Bearer {token}"}
    message = {"message": "Hello, how are you?"}
    response = requests.post(
        f"{BASE_URL}/api/chat",
        headers=headers,
        json=message
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def main():
    print("Starting API tests...")
    
    # Test registration
    if not test_register():
        print("Registration failed. Exiting...")
        return
    
    # Test login
    token = test_login()
    if not token:
        print("Login failed. Exiting...")
        return
    
    # Test saving API keys
    test_save_api_keys(token)
    
    # Test chat
    test_chat(token)

if __name__ == "__main__":
    main() 