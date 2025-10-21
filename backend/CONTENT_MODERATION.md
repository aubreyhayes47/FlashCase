# Content Moderation & User Reporting

## Overview

FlashCase implements comprehensive content moderation and user reporting features to maintain a safe and appropriate learning environment for law students.

## Features

### 1. Automated Profanity Filtering

**Library**: `better-profanity` v0.7.0

All user-generated content is automatically screened for inappropriate language before being saved to the database.

#### Protected Content
- Deck names
- Deck descriptions
- Card front text (questions)
- Card back text (answers)

#### How It Works
When users create or update decks/cards, the content is automatically validated:

```python
# Example validation
is_valid, error_message = validate_deck_content("Deck Name", "Description")
if not is_valid:
    raise HTTPException(status_code=400, detail=error_message)
```

If inappropriate content is detected, the request is rejected with a clear error message.

### 2. User Reporting System

Users can report inappropriate content (decks or cards) for admin review.

#### Report Types
- **Deck**: Report an entire deck
- **Card**: Report a specific flashcard

#### Report Reasons
- **Inappropriate**: Offensive or inappropriate content
- **Spam**: Spam or low-quality content
- **Copyright**: Copyright infringement
- **Misleading**: Incorrect or misleading information
- **Other**: Other issues

#### Report Statuses
- **Pending**: Newly submitted, awaiting review
- **Reviewed**: Admin has reviewed the report
- **Resolved**: Issue has been addressed
- **Dismissed**: Report was invalid or not actionable

### 3. Admin Review System

Administrators have special privileges to manage reported content:

- View all reports (with filtering by status/type)
- Review individual reports
- Update report status
- Add admin notes
- Delete reports

## API Endpoints

### Report Endpoints

#### Create Report (Authenticated Users)
```http
POST /api/v1/reports/
Content-Type: application/json
Authorization: Bearer {token}

{
  "report_type": "deck",
  "content_id": 123,
  "reason": "inappropriate",
  "description": "This deck contains offensive content"
}
```

#### Get My Reports
```http
GET /api/v1/reports/my-reports
Authorization: Bearer {token}
```

#### List All Reports (Admin Only)
```http
GET /api/v1/reports/?status_filter=pending&report_type=deck
Authorization: Bearer {admin_token}
```

#### Update Report Status (Admin Only)
```http
PUT /api/v1/reports/{report_id}
Authorization: Bearer {admin_token}

{
  "status": "resolved",
  "admin_notes": "Content removed and user warned"
}
```

#### Delete Report (Admin Only)
```http
DELETE /api/v1/reports/{report_id}
Authorization: Bearer {admin_token}
```

## Database Schema

### Report Model

```python
class Report(SQLModel, table=True):
    id: Optional[int]
    reporter_id: int  # FK to user.id
    report_type: ReportType  # "deck" or "card"
    content_id: int  # ID of deck/card
    reason: ReportReason
    description: Optional[str]
    status: ReportStatus  # "pending", "reviewed", "resolved", "dismissed"
    reviewed_by: Optional[int]  # FK to admin user.id
    admin_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
```

### User Model Enhancement

Added `is_admin` field to support admin privileges:

```python
class User(SQLModel, table=True):
    # ... existing fields ...
    is_admin: bool = Field(default=False)
```

## Admin Access

### Making a User an Admin

Admins must be created manually in the database:

```python
from app.models.user import User
from sqlmodel import Session, select

# Get user
statement = select(User).where(User.username == "admin_username")
user = session.exec(statement).first()

# Grant admin privileges
user.is_admin = True
session.add(user)
session.commit()
```

### Admin-Only Operations

The following operations require admin privileges:
- Listing all reports
- Viewing specific reports
- Updating report status
- Deleting reports

Admin access is enforced via the `get_current_admin_user` dependency:

```python
@router.get("/reports/")
async def list_reports(
    current_user: User = Depends(get_current_admin_user)
):
    # Only accessible by admins
```

## Testing

### Content Moderation Tests
Location: `tests/test_content_moderation.py`

**Test Coverage**:
- Profanity detection in deck names/descriptions
- Profanity detection in card front/back
- Content validation on create/update operations
- 18 tests passing

**Example Test**:
```python
def test_create_deck_with_profanity_in_name(client, auth_headers):
    response = client.post(
        "/api/v1/decks/",
        headers=auth_headers,
        json={"name": "Inappropriate Name", "description": "Clean"}
    )
    assert response.status_code == 400
    assert "inappropriate" in response.json()["detail"].lower()
```

### Reporting System Tests
Location: `tests/test_reports.py`

**Test Coverage**:
- Report creation by regular users
- Admin report management
- Report filtering (status, type)
- Permission enforcement
- 17 tests passing

## Best Practices

### For Regular Users
1. Report inappropriate content promptly
2. Provide detailed descriptions in reports
3. Use appropriate report reasons
4. Check your own reports via `/reports/my-reports`

### For Administrators
1. Review reports regularly
2. Add detailed admin notes
3. Take appropriate action on valid reports
4. Update report status promptly
5. Filter reports by status to prioritize pending items

### For Developers
1. Always validate content before database operations
2. Use the moderation service for all user-generated text
3. Log moderation actions for audit trails
4. Keep profanity filter updated
5. Monitor false positives

## Security Considerations

### Input Validation
- All content is validated using Pydantic models
- SQL injection prevented by ORM (SQLModel)
- XSS prevented by input validation and encoding

### Authorization
- Reports tied to authenticated users
- Admin operations require `is_admin = True`
- Cannot modify other users' content without admin privileges

### Rate Limiting
- Global rate limiting prevents abuse
- Applies to all endpoints including reports
- Default: 10 requests/minute, 100 requests/hour

## Limitations

### Current Limitations
1. **Language Support**: English-only profanity detection
2. **Context Awareness**: Basic keyword matching (may have false positives)
3. **User Blocking**: No automatic user blocking for repeat offenders
4. **Content Removal**: Manual admin review required

### Future Enhancements
- [ ] Multi-language profanity detection
- [ ] ML-based content classification
- [ ] Automated user warnings/suspensions
- [ ] Content appeal process
- [ ] Community moderation (trusted users)
- [ ] Automated content removal for severe violations
- [ ] Moderation dashboard for admins
- [ ] Report analytics and trends

## Compliance

### Educational Content Standards
- No offensive or discriminatory content
- No spam or low-quality content
- No copyright violations
- Accurate legal information encouraged

### Legal Disclaimers
All pages display appropriate disclaimers:
- **Legal Disclaimer**: Content is educational, not legal advice
- **AI Disclaimer**: AI-generated content may contain errors

These disclaimers are prominently displayed on:
- Home page footer
- Create page (both legal and AI disclaimers)
- Study page
- Discover page

## Monitoring

### Metrics to Track
- Number of reports per day/week
- Report resolution time
- Report types distribution
- False positive rate (if applicable)
- User reporting patterns

### Alerts
Consider setting up alerts for:
- Spike in reports for specific content
- Multiple reports from same user
- Unreviewed reports older than X days
- High false positive rate

## Support

For questions or issues related to content moderation:
- Check this documentation
- Review test cases in `tests/test_content_moderation.py` and `tests/test_reports.py`
- Contact system administrators
- Report technical issues via GitHub Issues

---

**Last Updated**: October 21, 2025  
**Version**: 1.0  
**Status**: Production Ready
