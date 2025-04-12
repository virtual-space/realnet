import requests
import json
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Configuration
BASE_URL = "http://localhost:5000"
ORG_NAME = "realnet"
CLIENT_ID = "pfEQs7GRIUn4W1AES2NQgIpt"  # Correct client_id from database
CLIENT_SECRET = "qE0BXrTPeHm0Mc3Vx8JgXAEvlaJqmcfU04wkjkMPayvWwS6p"
USERNAME = "realnet"
PASSWORD = "realnet"

def test_org_oauth_token_endpoint():
    print(f"Testing /{ORG_NAME}/oauth/token endpoint with client_id={CLIENT_ID}...")
    
    url = f"{BASE_URL}/{ORG_NAME}/oauth/token"
    
    # Prepare the request payload
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
    
    # Log the request details
    print(f"Request URL: {url}")
    print(f"Request headers: {headers}")
    print(f"Request payload: {payload}")
    
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

if __name__ == "__main__":
    print("OAuth Authentication Test Script - Specific Client")
    print("================================================")
    
    # Test the endpoint
    success = test_org_oauth_token_endpoint()
    
    print("\nSummary:")
    print(f"- Org-specific OAuth token endpoint with client_id={CLIENT_ID}: {'SUCCESS' if success else 'FAILED'}")