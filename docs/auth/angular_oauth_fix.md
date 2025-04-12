# Angular OAuth Authentication Fix

## Issue Description

The RealNet API authentication is failing with the error:

```
{"error": "invalid_client"}
```

This occurs for several reasons:
1. Using the client name instead of the actual client ID for authentication
2. The OAuth 2.0 specification requires a `grant_type` parameter in token requests
3. Using the wrong endpoint for password grant authentication
4. The client authentication method is not being used correctly

## Required Fix
Four changes are needed:

1. Use the correct client ID (`pfEQs7GRIUn4W1AES2NQgIpt`) instead of the client name (`realnet_cli`)
   - This is critical because the authentication process validates using the client ID, not the name
2. Use the correct OAuth token endpoint: `/<org_name>/oauth/token` instead of `/<org_name>/login`
   - The organization name must be included in the path (e.g., `/realnet/oauth/token`)
   - This ensures proper organization context for authentication
3. Include the `grant_type` parameter with the value `password` when using username/password authentication
4. Use HTTP Basic Authentication for the client credentials instead of including them in the request body

## Implementation Steps

1. Locate your authentication service (likely in a file like `auth.service.ts` or similar)

2. Find the login method that makes the HTTP request to the authentication endpoint

3. Update the endpoint and add the `grant_type: 'password'` parameter:

```typescript
// Before (problematic implementation)
login(username: string, password: string): Observable<any> {
  return this.http.post('/realnet/login', {
    client_id: 'realnet_cli',  // INCORRECT: Using client name instead of client ID
    username: username,
    password: password
    // Missing grant_type parameter
  });
}

// After
login(username: string, password: string, orgName: string = 'realnet'): Observable<any> {
  // Create the request body with only user credentials and grant type
  const body = {
    username: username,
    password: password,
    grant_type: 'password'
  };
  
  // Create HTTP Basic Auth header with client credentials
  const clientId = 'pfEQs7GRIUn4W1AES2NQgIpt';  // CORRECT: Using actual client ID, not the client name
  const clientSecret = 'qE0BXrTPeHm0Mc3Vx8JgXAEvlaJqmcfU04wkjkMPayvWwS6p';  // Use the actual client secret
  
  // Create the Authorization header
  const authHeader = 'Basic ' + btoa(clientId + ':' + clientSecret);
  
  // Set headers for the request
  const httpOptions = {
    headers: new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded',
      'Authorization': authHeader
    })
  };
  
  // Convert the body to x-www-form-urlencoded format
  const formData = new URLSearchParams();
  for (const key in body) {
    formData.set(key, body[key]);
  }
  
  // Make the request to the organization-specific OAuth token endpoint
  return this.http.post(`/${orgName}/oauth/token`, formData.toString(), httpOptions);
}
```

4. Alternative implementation using HttpParams:

```typescript
// Alternative implementation using HttpParams
login(username: string, password: string, orgName: string = 'realnet'): Observable<any> {
  // Create the request body with only user credentials and grant type
  const params = new HttpParams()
    .set('username', username)
    .set('password', password)
    .set('grant_type', 'password');
  
  // Create HTTP Basic Auth header with client credentials
  const clientId = 'pfEQs7GRIUn4W1AES2NQgIpt';  // CORRECT: Using actual client ID, not the client name
  const clientSecret = 'qE0BXrTPeHm0Mc3Vx8JgXAEvlaJqmcfU04wkjkMPayvWwS6p';  // Use the actual client secret
  
  // Create the Authorization header
  const authHeader = 'Basic ' + btoa(clientId + ':' + clientSecret);
  
  // Make the request to the organization-specific OAuth token endpoint
  return this.http.post(`/${orgName}/oauth/token`, params.toString(), {
    headers: new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded',
      'Authorization': authHeader
    })
  });
}
```

## Why Client ID vs Client Name Matters

In the RealNet authentication system:

1. Each client has both a name (e.g., `realnet_cli`) and a client ID (e.g., `pfEQs7GRIUn4W1AES2NQgIpt`)
2. The OAuth server authenticates clients using their client ID, not their name
3. Using the client name instead of the client ID in the Authorization header will result in an "invalid_client" error
4. You can verify the correct client ID using the `query_client_info.py` script in the project root

## Testing

After making this change, test the login functionality to ensure it works correctly. The server should now return a valid OAuth token response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "def502...",
  "scope": ""
}
```

## Additional Information

- The OAuth 2.0 specification mandates the `grant_type` parameter for token requests
- The RealNet API supports multiple grant types, but for username/password authentication, use `password`
- The organization-specific `/<org_name>/oauth/token` endpoint is the recommended OAuth 2.0 token endpoint that properly handles all grant types and ensures proper organization context
- The client is configured to use "client_secret_basic" authentication method, which requires HTTP Basic Authentication
- If you're implementing token refresh, use `grant_type: 'refresh_token'` for those requests with the `/<org_name>/oauth/token` endpoint
- Always include the organization name in the path to ensure proper authentication context
- The client must be registered with the specified organization for authentication to succeed

## References

- [OAuth 2.0 Resource Owner Password Credentials Grant](https://oauth.net/2/grant-types/password/)
- [RealNet API Authentication Guide](../auth/api_authentication_guide.md)