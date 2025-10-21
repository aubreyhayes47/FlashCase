# FlashCase Security Documentation

**Version**: 1.0  
**Last Updated**: October 21, 2025  
**Status**: Active

## Overview

This document describes the security measures implemented in FlashCase to protect user data, prevent abuse, and maintain a safe learning environment.

## Security Features

### 1. Authentication & Authorization

#### JWT-Based Authentication
- **Token Generation**: Uses python-jose for JWT creation
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Token Expiration**: 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Token Format**: Bearer token in Authorization header
- **Secure Storage**: Tokens should be stored in httpOnly cookies (frontend implementation recommended)

#### Password Security
- **Hashing Algorithm**: Bcrypt via passlib
- **Automatic Salting**: Each password gets unique salt
- **No Plain Text**: Passwords never stored in plain text
- **Rounds**: Default bcrypt rounds (12)
- **Validation**: Minimum 8 characters required

#### Protected Endpoints
- All endpoints except `/auth/register` and `/auth/login` require authentication
- JWT token validated on every protected request
- User context available via dependency injection
- Invalid tokens return 401 Unauthorized

**Implementation Example:**
```python
from app.core.auth import get_current_user

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"user": current_user.username}
```

### 2. Content Moderation

#### Automated Profanity Filtering
- **Library**: better-profanity v0.7.0
- **Scope**: All user-generated content
  - Deck names and descriptions
  - Card front and back text
- **Validation Point**: On create and update operations
- **Response**: 400 Bad Request with clear error message

**Protected Content:**
- Deck name
- Deck description
- Card front text
- Card back text

**Error Response:**
```json
{
  "detail": "Deck name: Content contains inappropriate language"
}
```

#### User Reporting System
Users can report inappropriate content for manual review:

**Report Types:**
- Deck reports
- Card reports

**Report Reasons:**
- inappropriate
- spam
- copyright
- misleading
- other

**Report Statuses:**
- pending (initial state)
- reviewed (under admin review)
- resolved (action taken)
- dismissed (no action needed)

**Privacy**: Users can only view their own reports

#### Admin Moderation
- Admin-only endpoints for report management
- Filter reports by status and type
- Update report status with admin notes
- Track which admin reviewed each report
- Audit trail maintained

### 3. Rate Limiting

#### General API Rate Limits
- **Per Minute**: 10 requests
- **Per Hour**: 100 requests
- **Scope**: Per IP address
- **Library**: slowapi

#### AI-Specific Rate Limits
More restrictive to control costs:
- **Per Minute**: 5 requests
- **Per Hour**: 50 requests
- **Scope**: Per authenticated user

#### Rate Limit Response
When exceeded, returns 429 Too Many Requests:
```json
{
  "detail": "Rate limit exceeded"
}
```

**Headers Included:**
- `X-RateLimit-Limit`: Rate limit cap
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp

### 4. Input Validation

#### Pydantic Schemas
All API inputs validated using Pydantic models:

**Validation Rules:**
- Email format validation
- String length constraints
- Required vs optional fields
- Type checking
- Custom validators

**Validation Errors:**
Returns 422 Unprocessable Entity with detailed error information:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

#### SQL Injection Protection
- **ORM Used**: SQLModel (SQLAlchemy-based)
- **Parameterized Queries**: All queries use parameter binding
- **No Raw SQL**: Direct SQL execution avoided
- **Input Sanitization**: Automatic via ORM

### 5. CORS Configuration

#### Development Settings
```python
CORS_ORIGINS=["http://localhost:3000"]
```

#### Production Settings
Must explicitly list allowed origins:
```python
CORS_ORIGINS=["https://flashcase.com", "https://app.flashcase.com"]
```

**Enabled Methods**: All (`["*"]`)  
**Enabled Headers**: All (`["*"]`)  
**Credentials**: Enabled (`allow_credentials=True`)

⚠️ **Security Note**: Never use `["*"]` for origins in production!

### 6. Token Usage & Cost Control

#### AI API Token Tracking
- Real-time token counting for all AI requests
- Per-user usage statistics
- Configurable alert thresholds
- Usage endpoint: `GET /api/v1/ai/usage`

#### Token Limits Per Endpoint
- **Chat**: 2000 tokens max
- **Rewrite**: 1000 tokens max
- **Autocomplete**: 500 tokens max

#### Cost Control Measures
- Rate limiting prevents abuse
- Token limits prevent runaway costs
- Usage alerts notify of high usage
- Per-user tracking enables accountability

### 7. Secure Configuration

#### Environment Variables
Sensitive configuration stored in environment variables:

**Never Commit:**
- `SECRET_KEY` - JWT signing key
- `GROK_API_KEY` - AI API key
- `COURTLISTENER_API_KEY` - Legal API key
- `DATABASE_URL` - Database connection string (if contains credentials)

**Configuration Files:**
- `.env` - Local development (git-ignored)
- `.env.example` - Template (committed)
- Platform environment variables for production

#### Secret Key Generation
```bash
# Generate secure random key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

⚠️ **Critical**: Change `SECRET_KEY` from default in production!

### 8. Database Security

#### Connection Security
- Connection pooling (production)
- SSL/TLS for remote databases (PostgreSQL)
- Minimal privileges for application user

#### Data Protection
- Password hashing (bcrypt)
- No sensitive data in logs
- Foreign key constraints enforced
- Proper indexing for performance

#### Backup & Recovery
- Regular database backups recommended
- Point-in-time recovery capability
- Backup encryption for production

## Security Best Practices

### For Developers

1. **Never Commit Secrets**
   - Use `.gitignore` for `.env` files
   - Review commits before pushing
   - Use environment variables

2. **Validate All Input**
   - Use Pydantic schemas
   - Check length constraints
   - Sanitize user content

3. **Use Protected Routes**
   - Require authentication where appropriate
   - Check user ownership of resources
   - Implement proper authorization

4. **Handle Errors Securely**
   - Don't expose internal errors to users
   - Log errors server-side
   - Return generic error messages

5. **Keep Dependencies Updated**
   - Regularly update packages
   - Review security advisories
   - Test updates before deploying

### For Deployment

1. **Use HTTPS**
   - Never use HTTP in production
   - Use valid SSL certificates
   - Configure HSTS headers

2. **Secure Environment**
   - Use production-grade secret management
   - Restrict database access
   - Use firewalls and security groups

3. **Enable Monitoring**
   - Log security events
   - Monitor for suspicious activity
   - Set up alerts for anomalies

4. **Regular Security Audits**
   - Review access logs
   - Check for vulnerabilities
   - Update security practices

## Compliance & Privacy

### Data Collection
- Email addresses (for authentication)
- Usernames (public identifier)
- Study progress (for SRS algorithm)
- Content reports (for moderation)

### Data Usage
- Authentication and authorization
- Personalized study experience
- Content moderation
- Service improvement

### Data Retention
- User accounts: Retained until deletion
- Study logs: Retained for algorithm
- Reports: Retained for audit trail

### User Rights
- Access their own data
- Delete their account
- Export their data (planned)

### GDPR Considerations
- Right to access (GET /auth/me)
- Right to deletion (account deletion)
- Data minimization (collect only necessary data)
- Purpose limitation (use data only as specified)

## Security Incident Response

### If You Discover a Vulnerability

1. **Do Not** disclose publicly
2. **Do Not** exploit the vulnerability
3. **Do** report via GitHub Security Advisory
4. **Do** include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Process

1. **Acknowledgment**: Within 48 hours
2. **Assessment**: Within 5 business days
3. **Fix Development**: Based on severity
4. **Disclosure**: After fix is deployed
5. **Credit**: Reporter credited (if desired)

## Security Testing

### Current Test Coverage
- **Authentication**: 15 tests
- **Protected Endpoints**: 28 tests
- **Content Moderation**: 18 tests
- **Input Validation**: Covered in integration tests

### Testing Recommendations
- Run tests before deployment
- Test authentication flows
- Verify rate limiting
- Check input validation
- Test error handling

## Known Security Considerations

### Current Limitations

1. **Admin Role Management**: Basic admin flag
   - No role-based access control (RBAC)
   - Single admin privilege level
   - Consider implementing RBAC for granular permissions

2. **Session Management**: No session invalidation
   - Tokens valid until expiration
   - No logout/revocation mechanism
   - Consider implementing token blacklist

3. **Rate Limiting**: IP-based
   - Can be bypassed with proxies
   - Consider user-based rate limiting
   - Add IP reputation checking

4. **Content Validation**: Basic profanity filter
   - May have false positives/negatives
   - Consider ML-based moderation
   - Add context-aware filtering

### Future Security Enhancements

1. **Multi-Factor Authentication (MFA)**
   - TOTP support
   - SMS verification
   - Backup codes

2. **OAuth Integration**
   - Google OAuth
   - GitHub OAuth
   - Microsoft OAuth

3. **Advanced Rate Limiting**
   - Adaptive rate limiting
   - IP reputation
   - Behavioral analysis

4. **Enhanced Monitoring**
   - Security event logging
   - Anomaly detection
   - Real-time alerts

5. **Penetration Testing**
   - Regular security audits
   - Automated vulnerability scanning
   - Third-party assessments

## Resources

### Internal Documentation
- [API Documentation](../backend/API_DOCUMENTATION.md)
- [Content Moderation](../backend/CONTENT_MODERATION.md)
- [Cost Control](../backend/COST_CONTROL.md)

### External Resources
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/14/faq/security.html)

## Contact

For security concerns:
- Open a [GitHub Security Advisory](https://github.com/aubreyhayes47/FlashCase/security/advisories)
- For general questions: Open a GitHub Issue

---

**Last Updated**: October 21, 2025  
**Version**: 1.0  
**Status**: Active
