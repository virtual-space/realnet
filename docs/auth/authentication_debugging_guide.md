# Authentication Debugging Guide

This guide provides detailed instructions for diagnosing and resolving common authentication issues in the RealNet API.

## Potential Authentication Issues

After analyzing the authentication system, I've identified several potential sources of authentication problems:

### 1. Token Expiration and Refresh Flow

**Symptoms:**
- Users are unexpectedly logged out
- API requests suddenly start returning 401 errors after working previously
- Authentication works initially but fails after some time

**Diagnosis:**
Add logging to track token lifecycle:

```python
# In auth.py, modify the RefreshTokenGrant class
class RefreshTokenGrant(grants.RefreshTokenGrant):
    def authenticate_refresh_token(self, refresh_token):
        token = db.query(Token).filter_by(refresh_token=refresh_token).first()
        if token:
            logging.info(f"Refresh token found for user {token.user_id}, expires at {token.expires_at}")
            if token.is_refresh_token_active():
                return token
            else:
                logging.warning(f"Refresh token for user {token.user_id} has expired")
        else:
            logging.warning(f"Refresh token not found in database")
        return None
```

**Resolution:**
- Ensure clients are properly storing refresh tokens
- Implement token refresh logic on the client side
- Consider extending token lifetimes if appropriate for your use case

### 2. Authentication Error Handling

**Symptoms:**
- Generic error messages that don't help with troubleshooting
- Missing information in error responses
- Inconsistent error formats across endpoints

**Diagnosis:**
Add more detailed logging to authentication endpoints:

```python
# In router.py, modify the login function
@router_bp.route('/<org_name>/signin', methods=['GET', 'POST'])
def login(org_name):
    contextProvider = current_app.config['REALNET_CONTEXT_PROVIDER']
    if request.method == 'POST':
        org = contextProvider.get_org_by_name(org_name)
        if not org:
            logging.warning(f"Login attempt for non-existent org: {org_name}")
            # Rest of the code...
        
        username = request.form.get('username')
        if not username:
            logging.warning(f"Login attempt with missing username for org: {org_name}")
            # Rest of the code...
            
        password = request.form.get('password')
        if not password:
            logging.warning(f"Login attempt with missing password for org: {org_name} and user: {username}")
            # Rest of the code...
            
        account = contextProvider.check_password(org.id, username, password)
        if not account:
            logging.warning(f"Failed login attempt for org: {org_name} and user: {username}")
            # Rest of the code...
```

**Resolution:**
- Standardize error response formats across all authentication endpoints
- Provide more specific error messages without exposing sensitive information
- Implement comprehensive logging for authentication failures

## Validating Authentication Flow

To ensure the authentication system is working correctly, add the following logging statements to key points in the authentication flow:

### 1. Login Request Validation

```python
# In router.py, at the beginning of the tenant_login function
@router_bp.route('/<id>/login', defaults={'name': None}, methods=['GET', 'POST'])
@router_bp.route('/<id>/login/<name>', methods=['GET', 'POST'])
def tenant_login(id, name):
    logging.info(f"Login request received for tenant: {id}, auth method: {name}")
    logging.debug(f"Request method: {request.method}, content type: {request.content_type}")
    if request.is_json:
        logging.debug(f"JSON payload: {request.json}")
    elif request.form:
        logging.debug(f"Form data: {request.form}")
    # Rest of the function...
```

### 2. Token Generation

```python
# In auth.py, add logging to the save_token function
def save_token(token, request):
    logging.info(f"Generating token for client: {request.client.client_id}, user: {request.user.id}")
    # Original save_token implementation...
    logging.info(f"Token generated successfully, expires in: {token.get('expires_in')} seconds")
    return token
```

### 3. Token Validation

```python
# In auth.py, add logging to the bearer token validator
class BearerTokenValidator(OAuth2TokenValidator):
    def authenticate_token(self, token_string):
        token = db.query(Token).filter_by(access_token=token_string).first()
        if token:
            logging.debug(f"Token found for validation: {token.id}")
            if token.is_access_token_active():
                logging.debug(f"Token is active, user: {token.user_id}")
                return token
            logging.warning(f"Token {token.id} has expired")
        else:
            logging.warning(f"Token not found in database")
        return None
```

## Common Authentication Issues and Solutions

### Issue 1: "Invalid username or password" errors

**Possible causes:**
- User doesn't exist in the specified organization
- Password is incorrect
- Username case sensitivity issues

**Solution:**
1. Verify the user exists in the organization database
2. Check if the password hashing algorithm matches what's stored
3. Ensure username comparison is case-sensitive or case-insensitive as intended

### Issue 2: "Client not found" errors

**Possible causes:**
- Client ID is incorrect
- Client is not associated with the specified organization
- Client has been deleted or disabled

**Solution:**
1. Verify the client ID is correct
2. Check if the client is properly associated with the organization
3. Ensure the client is active and enabled

### Issue 3: Token validation failures

**Possible causes:**
- Token has expired
- Token has been revoked
- Token was issued for a different client

**Solution:**
1. Implement proper token refresh logic
2. Check if tokens are being properly stored in the database
3. Verify token validation logic is correct

## Advanced Debugging Techniques

### Database Inspection

Check the token and authorization_code tables directly:

```sql
-- Check active tokens
SELECT id, user_id, client_id, expires_at, revoked 
FROM token 
WHERE revoked = false AND expires_at > NOW();

-- Check recent authorization codes
SELECT id, account_id, client_id, expires_at, code 
FROM authorization_code 
WHERE expires_at > NOW() 
ORDER BY id DESC LIMIT 10;
```

### Network Traffic Analysis

Use tools like Wireshark or browser developer tools to inspect the authentication requests and responses:

1. Look for proper HTTPS encryption
2. Verify correct headers are being sent
3. Check response status codes and payloads

### Client-Side Debugging

Add detailed logging to client-side authentication code:

```javascript
async function authenticate(orgName, username, password, clientId) {
  console.log(`Attempting authentication for user ${username} in org ${orgName}`);
  try {
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
    
    console.log(`Authentication response status: ${response.status}`);
    
    if (!response.ok) {
      const errorData = await response.json();
      console.error('Authentication error:', errorData);
      throw new Error(`Authentication failed: ${errorData.data || 'Unknown error'}`);
    }
    
    const tokenData = await response.json();
    console.log('Authentication successful, token expires in:', tokenData.expires_in);
    return tokenData;
  } catch (error) {
    console.error('Authentication request failed:', error);
    throw error;
  }
}
```

## Security Considerations During Debugging

1. **Never log sensitive information** such as passwords, tokens, or personal data
2. **Redact sensitive information** in error messages and logs
3. **Use secure channels** for sharing debugging information
4. **Limit detailed logging** to development and staging environments
5. **Rotate credentials** after debugging sessions

## Conclusion

By implementing these logging and debugging strategies, you can identify and resolve authentication issues more efficiently. Remember to remove or disable verbose logging in production environments to maintain security and performance.