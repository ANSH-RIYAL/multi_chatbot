import requests
import json

BASE_URL = "http://localhost:8000"

def save_api_key(service: str, api_key: str):
    """Save API key for a service"""
    print(f"\nSaving {service} API key...")
    response = requests.post(
        f"{BASE_URL}/api/service/{service}/key",
        json={"api_key": api_key}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def get_service_status():
    """Get status of all services"""
    print("\nGetting service status...")
    response = requests.get(f"{BASE_URL}/api/service/status")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_chat(message: str):
    """Test chat with all services"""
    print("\nTesting chat...")
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={"message": message}
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def main():
    print("Starting service tests...")
    
    # Save API keys for each service
    services = {
        "openai": "your-openai-key-here",
        "gemini": "your-gemini-key-here",
        "grok": "your-grok-key-here"
    }
    
    for service, api_key in services.items():
        if not save_api_key(service, api_key):
            print(f"Failed to save {service} API key. Continuing...")
    
    # Check service status
    get_service_status()
    
    # Test chat
    test_chat("Hello! How are you today?")

if __name__ == "__main__":
    main() 