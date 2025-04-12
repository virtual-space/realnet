# User Authentication Implementation Guide

This comprehensive guide provides detailed instructions for implementing user authentication via the RealNet API using username and password credentials. It includes implementation steps, code examples, best practices, and troubleshooting tips.

## Table of Contents

1. [Authentication System Overview](#authentication-system-overview)
2. [Implementation Steps](#implementation-steps)
3. [API Endpoints Reference](#api-endpoints-reference)
4. [Code Examples](#code-examples)
5. [Security Best Practices](#security-best-practices)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Topics](#advanced-topics)

## Authentication System Overview

The RealNet platform uses a robust authentication system based on OAuth 2.0 with support for multiple authentication methods:

- Username/password authentication
- OAuth2 authentication with external providers
- Token-based authentication for API access

This guide focuses on implementing username/password authentication for API access.

### Authentication Flow

1. Client application collects username and password from the user
2. Client sends credentials to the authentication endpoint
3. Server validates credentials against the database
4. If valid, server generates an OAuth2 token
5. Client stores the token and uses it for subsequent API requests
6. When the token expires, client uses refresh token to obtain a new access token

## Implementation Steps

### 1. Prerequisites

Before implementing authentication, ensure you have:

- Organization name (tenant identifier)
- Client ID (provided when the client application was registered)
- API endpoint URL

### 2. Collect User Credentials

Create a secure form or input method to collect:

- Username
- Password

Ensure the form implements basic validation and security measures:

```html
<form id="login-form">
  <div>
    <label for="username">Username:</label>
    <input type="text" id="username" name="username" required>
  </div>
  <div>
    <label for="password">Password:</label>
    <input type="password" id="password" name="password" required>
  </div>
  <button type="submit">Login</button>
</form>
```

### 3. Send Authentication Request

When the user submits their credentials, send an authentication request to the API:

```javascript
async function authenticate(orgName, username, password, clientId) {
  const response = await fetch(`/${orgName}/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      client_id: clientId,
      username: username,
      password: password
    })
  });
  
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.data || 'Authentication failed');
  }
  
  return await response.json();
}
```

### 4. Store Authentication Tokens

When authentication is successful, you'll receive a response containing:

- `access_token`: Used for authenticating API requests
- `refresh_token`: Used to obtain a new access token when the current one expires
- `expires_in`: Number of seconds until the access token expires
- `token_type`: Type of token (typically "Bearer")

Store these securely:

```javascript
function storeAuthTokens(tokenData) {
  // Calculate expiration time
  const expiresAt = Date.now() + (tokenData.expires_in * 1000);
  
  // Store tokens securely
  // Note: In production, use more secure storage methods
  localStorage.setItem('access_token', tokenData.access_token);
  localStorage.setItem('refresh_token', tokenData.refresh_token);
  localStorage.setItem('token_expires_at', expiresAt.toString());
}
```

### 5. Use Tokens for API Requests

Include the access token in the Authorization header for all API requests:

```javascript
async function fetchProtectedResource(url) {
  const accessToken = localStorage.getItem('access_token');
  
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  
  if (response.status === 401) {
    // Token might be expired, try to refresh
    await refreshAuthToken();
    // Retry the request with new token
    return fetchProtectedResource(url);
  }
  
  return await response.json();
}
```

### 6. Implement Token Refresh

When the access token expires, use the refresh token to obtain a new one:

```javascript
async function refreshAuthToken() {
  const refreshToken = localStorage.getItem('refresh_token');
  const clientId = 'YOUR_CLIENT_ID'; // Store this securely
  
  const response = await fetch('/oauth/token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({
      'grant_type': 'refresh_token',
      'refresh_token': refreshToken,
      'client_id': clientId
    })
  });
  
  if (!response.ok) {
    // Refresh failed, user needs to log in again
    redirectToLogin();
    throw new Error('Token refresh failed');
  }
  
  const tokenData = await response.json();
  storeAuthTokens(tokenData);
  return tokenData;
}
```

### 7. Implement Logout

When the user logs out, revoke the tokens and clear local storage:

```javascript
async function logout() {
  const accessToken = localStorage.getItem('access_token');
  
  // Optionally notify the server to revoke the token
  try {
    await fetch('/logout', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
  } catch (error) {
    console.error('Error during logout:', error);
  }
  
  // Clear local storage
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('token_expires_at');
  
  // Redirect to login page
  window.location.href = '/login';
}
```

## API Endpoints Reference

### Authentication Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/<org_name>/login` | POST | Authenticate with username and password |
| `/oauth/token` | POST | Get a new access token using a refresh token |
| `/logout` | POST | Revoke the current token and end the session |

### Authentication Request Parameters

#### Login Endpoint (`/<org_name>/login`)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | string | Yes | The client application ID |
| `username` | string | Yes | The user's username |
| `password` | string | Yes | The user's password |

#### Token Endpoint (`/oauth/token`)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `grant_type` | string | Yes | Must be "refresh_token" |
| `refresh_token` | string | Yes | The refresh token received during authentication |
| `client_id` | string | Yes | The client application ID |

### Response Formats

#### Successful Authentication

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "def502...",
  "scope": ""
}
```

#### Authentication Error

```json
{
  "isError": true,
  "message": "Failure",
  "statusCode": 401,
  "data": "Invalid username or password"
}
```

## Code Examples

### Complete Authentication Implementation (JavaScript)

```javascript
class AuthService {
  constructor(apiBaseUrl, orgName, clientId) {
    this.apiBaseUrl = apiBaseUrl;
    this.orgName = orgName;
    this.clientId = clientId;
  }
  
  async login(username, password) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/${this.orgName}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          client_id: this.clientId,
          username: username,
          password: password
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.data || 'Authentication failed');
      }
      
      const tokenData = await response.json();
      this._storeTokens(tokenData);
      return tokenData;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }
  
  async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }
    
    try {
      const response = await fetch(`${this.apiBaseUrl}/oauth/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
          'grant_type': 'refresh_token',
          'refresh_token': refreshToken,
          'client_id': this.clientId
        })
      });
      
      if (!response.ok) {
        throw new Error('Token refresh failed');
      }
      
      const tokenData = await response.json();
      this._storeTokens(tokenData);
      return tokenData;
    } catch (error) {
      console.error('Token refresh error:', error);
      this.logout();
      throw error;
    }
  }
  
  async logout() {
    const accessToken = localStorage.getItem('access_token');
    
    try {
      await fetch(`${this.apiBaseUrl}/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this._clearTokens();
    }
  }
  
  async fetchWithAuth(url, options = {}) {
    if (!this.isAuthenticated()) {
      throw new Error('User is not authenticated');
    }
    
    // Check if token needs refresh
    if (this._isTokenExpired()) {
      await this.refreshToken();
    }
    
    const accessToken = localStorage.getItem('access_token');
    const headers = options.headers || {};
    
    const response = await fetch(url, {
      ...options,
      headers: {
        ...headers,
        'Authorization': `Bearer ${accessToken}`
      }
    });
    
    if (response.status === 401) {
      // Token might be invalid, try to refresh once
      try {
        await this.refreshToken();
        // Retry the request with new token
        return this.fetchWithAuth(url, options);
      } catch (error) {
        // If refresh fails, clear tokens and throw error
        this._clearTokens();
        throw new Error('Authentication failed, please log in again');
      }
    }
    
    return response;
  }
  
  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  }
  
  _storeTokens(tokenData) {
    const expiresAt = Date.now() + (tokenData.expires_in * 1000);
    
    localStorage.setItem('access_token', tokenData.access_token);
    localStorage.setItem('refresh_token', tokenData.refresh_token);
    localStorage.setItem('token_expires_at', expiresAt.toString());
  }
  
  _clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('token_expires_at');
  }
  
  _isTokenExpired() {
    const expiresAt = parseInt(localStorage.getItem('token_expires_at'), 10);
    // Add a buffer of 60 seconds to refresh before expiration
    return Date.now() > (expiresAt - 60000);
  }
}

// Usage example
const authService = new AuthService('https://api.example.com', 'myorg', 'client123');

// Login form handler
document.getElementById('login-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  
  try {
    await authService.login(username, password);
    window.location.href = '/dashboard';
  } catch (error) {
    document.getElementById('error-message').textContent = error.message;
  }
});
```

### Python Client Example

```python
import requests
import time
import json

class RealNetAuthClient:
    def __init__(self, api_base_url, org_name, client_id):
        self.api_base_url = api_base_url
        self.org_name = org_name
        self.client_id = client_id
        self.tokens = None
        self.token_expiry = 0
    
    def login(self, username, password):
        """Authenticate with username and password"""
        url = f"{self.api_base_url}/{self.org_name}/login"
        payload = {
            "client_id": self.client_id,
            "username": username,
            "password": password
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code != 200:
            error_data = response.json()
            raise Exception(f"Authentication failed: {error_data.get('data', 'Unknown error')}")
        
        self.tokens = response.json()
        self.token_expiry = time.time() + self.tokens["expires_in"]
        return self.tokens
    
    def refresh_token(self):
        """Refresh the access token using the refresh token"""
        if not self.tokens or not self.tokens.get("refresh_token"):
            raise Exception("No refresh token available, please login again")
        
        url = f"{self.api_base_url}/oauth/token"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.tokens["refresh_token"],
            "client_id": self.client_id
        }
        
        response = requests.post(url, data=payload)
        
        if response.status_code != 200:
            # Clear tokens and raise exception
            self.tokens = None
            self.token_expiry = 0
            raise Exception("Token refresh failed, please login again")
        
        self.tokens = response.json()
        self.token_expiry = time.time() + self.tokens["expires_in"]
        return self.tokens
    
    def request(self, method, endpoint, data=None, params=None):
        """Make an authenticated request to the API"""
        if not self.tokens:
            raise Exception("Not authenticated, please login first")
        
        # Check if token needs refresh (with 60-second buffer)
        if time.time() > (self.token_expiry - 60):
            self.refresh_token()
        
        url = f"{self.api_base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.tokens['access_token']}"
        }
        
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data if data else None,
            params=params if params else None
        )
        
        if response.status_code == 401:
            # Try to refresh token and retry once
            try:
                self.refresh_token()
                # Retry the request with new token
                headers["Authorization"] = f"Bearer {self.tokens['access_token']}"
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data if data else None,
                    params=params if params else None
                )
            except Exception:
                raise Exception("Authentication failed, please login again")
        
        return response
    
    def logout(self):
        """Logout and invalidate the current token"""
        if not self.tokens:
            return
        
        try:
            self.request("POST", "/logout")
        except Exception:
            pass  # Ignore errors during logout
        finally:
            self.tokens = None
            self.token_expiry = 0

# Usage example
client = RealNetAuthClient("https://api.example.com", "myorg", "client123")

try:
    # Login
    client.login("username", "password")
    
    # Make authenticated requests
    response = client.request("GET", "/api/resource")
    data = response.json()
    print(data)
    
    # Logout when done
    client.logout()
except Exception as e:
    print(f"Error: {str(e)}")
```

## Security Best Practices

### 1. Secure Token Storage

- **Browser**: Use secure storage mechanisms:
  - For web apps: HttpOnly cookies with Secure and SameSite flags
  - For SPAs: Memory storage or secure browser storage with encryption
- **Mobile**: Use secure storage options:
  - iOS: Keychain
  - Android: EncryptedSharedPreferences or Keystore

### 2. HTTPS Everywhere

- Always use HTTPS for all API requests
- Implement certificate pinning for mobile apps
- Set the Secure flag on cookies

### 3. Token Lifecycle Management

- Implement proper token refresh logic
- Handle token expiration gracefully
- Revoke tokens on logout
- Use short-lived access tokens (1 hour or less)

### 4. Input Validation

- Validate all user inputs before sending to the API
- Implement client-side validation for immediate feedback
- Rely on server-side validation for security

### 5. Error Handling

- Implement proper error handling for authentication failures
- Don't expose sensitive information in error messages
- Log authentication failures for security monitoring

### 6. Rate Limiting

- Implement client-side throttling for authentication attempts
- Handle rate limiting responses from the server gracefully

## Troubleshooting

### Common Issues and Solutions

#### 1. Authentication Fails with "Invalid username or password"

**Possible causes:**
- Incorrect credentials
- User doesn't exist in the specified organization
- Case sensitivity issues with username

**Solutions:**
- Verify username and password are correct
- Check if the user exists in the organization
- Ensure proper case is used for username

#### 2. Token Refresh Fails

**Possible causes:**
- Refresh token has expired
- Refresh token has been revoked
- Client ID is incorrect

**Solutions:**
- Redirect user to login page to obtain new tokens
- Implement proper error handling for refresh failures
- Verify client ID is correct

#### 3. API Requests Return 401 Unauthorized

**Possible causes:**
- Access token has expired
- Access token is invalid
- Token is not properly included in the request

**Solutions:**
- Check if token is expired and refresh if needed
- Verify token is properly included in the Authorization header
- Ensure token format is correct: `Bearer {token}`

### Debugging Tips

1. **Enable verbose logging** during development to track authentication flow
2. **Inspect network requests** to verify correct headers and payloads
3. **Check token expiration times** to ensure they're being handled correctly
4. **Validate token format** to ensure it's being properly transmitted

## Advanced Topics

### 1. Multi-factor Authentication

While the basic authentication flow uses username and password, you can enhance security by implementing multi-factor authentication:

1. Perform initial authentication with username and password
2. Request a second factor (e.g., OTP code)
3. Verify the second factor before issuing tokens

### 2. Single Sign-On (SSO)

For enterprise applications, consider implementing SSO with external identity providers:

1. Redirect users to the identity provider for authentication
2. Process the authentication response
3. Exchange the authorization code for tokens

### 3. Token Security Enhancements

Consider these enhancements for token security:

1. **Token binding**: Bind tokens to specific devices or browsers
2. **Sliding expiration**: Extend token lifetime based on activity
3. **Scope-based tokens**: Limit token permissions based on required access

### 4. Monitoring and Analytics

Implement authentication monitoring for security:

1. Log authentication attempts (successes and failures)
2. Track token usage patterns
3. Set up alerts for suspicious activities (multiple failures, unusual locations)

## Conclusion

Implementing secure user authentication is critical for protecting your API and user data. By following this guide, you can create a robust authentication system that follows industry best practices and provides a good user experience.

Remember to regularly review and update your authentication implementation as security standards evolve and new threats emerge.