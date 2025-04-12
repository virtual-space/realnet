# API Authentication Guide

This guide provides detailed instructions for implementing user authentication via the RealNet API using username and password credentials.

## Overview

The RealNet platform supports authentication via username and password through its API. This document outlines the necessary steps to implement this authentication method in your application.

## Authentication Flow

The authentication flow for username and password authentication is as follows:

1. Client sends credentials (username and password) to the authentication endpoint
2. Server validates the credentials against the database
3. If valid, server generates an OAuth2 token
4. Client stores the token and uses it for subsequent API requests

## Implementation Steps

### 1. Understand the Authentication Endpoints

The RealNet API provides the following endpoints for authentication:

- `/<org_name>/signin` - Web-based login form (HTML response)
- `/<org_name>/login` - API-based login endpoint (JSON response)
- `/oauth/token` - OAuth2 token endpoint

For API-based authentication, you'll primarily use the `/<org_name>/login` endpoint.

### 2. Obtain Client Credentials

Before authenticating users, you need to have:

1. Organization name (tenant identifier)
2. Client ID (provided when the client application was registered)

These values are required for the authentication request.

### 3. Implement the Authentication Request

#### Request Format

```http
POST /<org_name>/login
Content-Type: application/json

{
  "client_id": "<your_client_id>",
  "username": "<user_username>",
  "password": "<user_password>"
}
```

Alternatively, you can use form data:

```http
POST /<org_name>/login
Content-Type: application/x-www-form-urlencoded

client_id=<your_client_id>&username=<user_username>&password=<user_password>
```

#### Response Format

A successful authentication will return an OAuth2 token response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "def502...",
  "scope": ""
}
```

### 4. Use the Token for API Requests

After obtaining the token, include it in the Authorization header for subsequent API requests:

```http
GET /api/resource
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 5. Handle Token Expiration

The access token has an expiration time (typically 1 hour). When it expires, you can use the refresh token to obtain a new access token without requiring the user to log in again.

```http
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token&refresh_token=def502...&client_id=<your_client_id>
```

## Code Examples

### Authentication Request (JavaScript)

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
    throw new Error('Authentication failed');
  }
  
  return await response.json();
}
```

### Using the Token (JavaScript)

```javascript
async function fetchProtectedResource(url, token) {
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${token.access_token}`
    }
  });
  
  return await response.json();
}
```

### Refreshing the Token (JavaScript)

```javascript
async function refreshToken(refreshToken, clientId) {
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
    throw new Error('Token refresh failed');
  }
  
  return await response.json();
}
```

## Error Handling

The API returns standard HTTP status codes to indicate success or failure:

- 200 OK: Authentication successful
- 400 Bad Request: Invalid request format
- 401 Unauthorized: Invalid credentials
- 404 Not Found: Organization or client not found

Error responses include a JSON body with details:

```json
{
  "isError": true,
  "message": "Failure",
  "statusCode": 401,
  "data": "Invalid username or password"
}
```

## Security Considerations

1. **Always use HTTPS**: Ensure all authentication requests are made over HTTPS to protect credentials.
2. **Store tokens securely**: Store access and refresh tokens securely, preferably in memory or secure storage.
3. **Implement token expiration handling**: Be prepared to handle token expiration and refresh tokens appropriately.
4. **Validate user input**: Always validate and sanitize user input before sending it to the authentication endpoint.
5. **Implement rate limiting**: Consider implementing rate limiting on the client side to prevent brute force attacks.

## Troubleshooting

### Common Issues

1. **"Invalid username or password"**: Verify the credentials are correct and the user exists in the specified organization.
2. **"Client not found"**: Verify the client ID is correct and associated with the specified organization.
3. **"Tenant not found"**: Verify the organization name is correct.

### Debugging Tips

1. Check the network request in your browser's developer tools to ensure the request format is correct.
2. Verify that all required parameters are included in the request.
3. Check for any CORS issues if making requests from a browser.

## Additional Resources

- [OAuth 2.0 Specification](https://oauth.net/2/)
- [JWT Introduction](https://jwt.io/introduction)
- [RealNet API Documentation](https://docs.realnet.example)

## Support

For additional support, contact the RealNet support team at support@realnet.example.