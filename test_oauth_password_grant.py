import requests
import json
import base64

# Configuration
BASE_URL = "http://localhost:5000"  # Change this if your server is running on a different host/port
ORG_NAME = "realnet"
CLIENT_ID = "pfEQs7GRIUn4W1AES2NQgIpt"  # Updated with actual client ID from database
CLIENT_SECRET = "qE0BXrTPeHm0Mc3Vx8JgXAEvlaJqmcfU04wkjkMPayvWwS6p"  # Updated with actual client secret from database
USERNAME = "realnet"
PASSWORD = "realnet"

# Test the global /oauth/token endpoint with password grant
def test_global_oauth_token_endpoint():
    print("Testing global OAuth token endpoint with password grant...")
    
    url = f"{BASE_URL}/oauth/token"
    
    # Prepare the request payload - without client credentials
    payload = {
        "grant_type": "password",
        "username": USERNAME,
        "password": PASSWORD
    }
    
    # Prepare HTTP Basic Authentication header
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    # Make the request with Basic Auth
    response = requests.post(url, data=payload, headers=headers)
    
    # Print the response
    print(f"Status code: {response.status_code}")
    try:
        if response.content:
            json_response = response.json()
            print(f"Response: {json.dumps(json_response, indent=2)}")
        else:
            print("Response: No content")
    except json.JSONDecodeError:
        print(f"Response (not JSON): {response.text}")
    
    return response.status_code == 200

# Test the organization-specific /<org_name>/oauth/token endpoint with password grant
def test_org_oauth_token_endpoint():
    print(f"Testing organization-specific /{ORG_NAME}/oauth/token endpoint with password grant...")
    
    url = f"{BASE_URL}/{ORG_NAME}/oauth/token"
    
    # Prepare the request payload - without client credentials
    payload = {
        "grant_type": "password",
        "username": USERNAME,
        "password": PASSWORD
    }
    
    # Prepare HTTP Basic Authentication header
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    # Make the request with Basic Auth
    response = requests.post(url, data=payload, headers=headers)
    
    # Print the response
    print(f"Status code: {response.status_code}")
    try:
        if response.content:
            json_response = response.json()
            print(f"Response: {json.dumps(json_response, indent=2)}")
        else:
            print("Response: No content")
    except json.JSONDecodeError:
        print(f"Response (not JSON): {response.text}")
    
    return response.status_code == 200

# Test the /realnet/login endpoint with password grant
def test_login_endpoint():
    print("\nTesting /realnet/login endpoint with password grant...")
    
    url = f"{BASE_URL}/{ORG_NAME}/login"
    # Prepare the request payload - without client credentials
    payload = {
        "grant_type": "password",
        "username": USERNAME,
        "password": PASSWORD
    }
    
    # Prepare HTTP Basic Authentication header
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/json'
    }
    
    # Make the request with Basic Auth
    response = requests.post(url, json=payload, headers=headers)
    
    # Print the response
    print(f"Status code: {response.status_code}")
    try:
        if response.content:
            json_response = response.json()
            print(f"Response: {json.dumps(json_response, indent=2)}")
        else:
            print("Response: No content")
    except json.JSONDecodeError:
        print(f"Response (not JSON): {response.text}")
    
    
    return response.status_code == 200

if __name__ == "__main__":
    print("OAuth Authentication Test Script")
    print("===============================")
    
    # Test all endpoints
    global_oauth_token_success = test_global_oauth_token_endpoint()
    org_oauth_token_success = test_org_oauth_token_endpoint()
    login_success = test_login_endpoint()
    
    print("\nSummary:")
    print(f"- Global OAuth token endpoint (/oauth/token): {'SUCCESS' if global_oauth_token_success else 'FAILED'}")
    print(f"- Org-specific OAuth token endpoint (/{ORG_NAME}/oauth/token): {'SUCCESS' if org_oauth_token_success else 'FAILED'}")
    print(f"- Login endpoint (/{ORG_NAME}/login): {'SUCCESS' if login_success else 'FAILED'}")
    
    if global_oauth_token_success or org_oauth_token_success:
        if org_oauth_token_success:
            print(f"\nRecommendation: Use the /{ORG_NAME}/oauth/token endpoint for OAuth password grant authentication")
        else:
            print("\nRecommendation: Use the /oauth/token endpoint for OAuth password grant authentication")