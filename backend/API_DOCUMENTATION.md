# FlashCase API Documentation

## Overview

The FlashCase API is a versioned REST API providing authentication, deck/card management, study sessions with spaced repetition, and AI-powered features for legal flashcard creation.

**Base URL**: `/api/v1`

**Authentication**: JWT Bearer Token (except for public endpoints)

**Interactive Documentation**: 
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Authentication

All endpoints except `/auth/register` and `/auth/login` require authentication using JWT tokens.

### Register a New User

Create a new user account.

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password123"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "is_active": true,
  "created_at": "2025-10-21T12:00:00",
  "updated_at": "2025-10-21T12:00:00"
}
```

**Validation Rules**:
- Email must be valid email format
- Username must be 3-50 characters
- Password must be at least 8 characters
- Email and username must be unique

### Login

Authenticate and receive a JWT token.

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=username&password=password123
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Token Expiration**: 30 minutes (configurable)

### Get Current User

Get information about the currently authenticated user.

```http
GET /api/v1/auth/me
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "is_active": true,
  "created_at": "2025-10-21T12:00:00",
  "updated_at": "2025-10-21T12:00:00"
}
```

## Decks

Manage flashcard decks.

### List All Decks

```http
GET /api/v1/decks/
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "name": "Constitutional Law",
    "description": "Study materials for Con Law",
    "is_public": false,
    "created_at": "2025-10-21T12:00:00",
    "updated_at": "2025-10-21T12:00:00"
  }
]
```

### Get Specific Deck

```http
GET /api/v1/decks/{deck_id}
Authorization: Bearer {token}
```

**Response** (200 OK): Same as deck object above

### Create New Deck

```http
POST /api/v1/decks/
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Constitutional Law",
  "description": "Study materials for Con Law",
  "is_public": false
}
```

**Response** (201 Created): Created deck object

**Validation Rules**:
- Name: 1-200 characters (required)
- Description: 0-1000 characters (optional)
- is_public: boolean (default: false)

### Update Deck

```http
PUT /api/v1/decks/{deck_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Constitutional Law - Updated",
  "description": "Updated description",
  "is_public": true
}
```

**Response** (200 OK): Updated deck object

**Note**: All fields are optional. Only provided fields will be updated.

### Delete Deck

```http
DELETE /api/v1/decks/{deck_id}
Authorization: Bearer {token}
```

**Response** (204 No Content)

## Cards

Manage flashcards within decks.

### List Cards

```http
GET /api/v1/cards/?deck_id={deck_id}
Authorization: Bearer {token}
```

**Query Parameters**:
- `deck_id` (optional): Filter cards by deck

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "deck_id": 1,
    "front": "What is judicial review?",
    "back": "The power of courts to review laws...",
    "created_at": "2025-10-21T12:00:00",
    "updated_at": "2025-10-21T12:00:00"
  }
]
```

### Get Specific Card

```http
GET /api/v1/cards/{card_id}
Authorization: Bearer {token}
```

**Response** (200 OK): Card object

### Create New Card

```http
POST /api/v1/cards/
Authorization: Bearer {token}
Content-Type: application/json

{
  "deck_id": 1,
  "front": "What is judicial review?",
  "back": "The power of courts to review laws and determine their constitutionality"
}
```

**Response** (201 Created): Created card object

**Validation Rules**:
- deck_id: Must exist (required)
- front: 1-2000 characters (required)
- back: 1-5000 characters (required)

### Update Card

```http
PUT /api/v1/cards/{card_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "front": "Updated question?",
  "back": "Updated answer"
}
```

**Response** (200 OK): Updated card object

**Note**: All fields are optional. Only provided fields will be updated.

### Delete Card

```http
DELETE /api/v1/cards/{card_id}
Authorization: Bearer {token}
```

**Response** (204 No Content)

## Study Sessions

Study cards using the spaced repetition system (SM-2 algorithm).

### Get Study Session

Get cards due for review in a specific deck.

```http
GET /api/v1/study/session/{deck_id}?limit=20
Authorization: Bearer {token}
```

**Query Parameters**:
- `limit` (optional): Maximum cards to return (default: 20)

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "deck_id": 1,
    "front": "What is judicial review?",
    "back": "The power of courts...",
    "ease_factor": 2.5,
    "interval": 0,
    "repetitions": 0,
    "due_date": "2025-10-21T12:00:00"
  }
]
```

**Algorithm**:
- Returns cards where due_date <= now
- Includes new cards never studied
- Orders by due_date (oldest first)
- Limits to specified count

### Review Card

Submit a review for a card and update study progress.

```http
POST /api/v1/study/review/{card_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "quality": 5
}
```

**Request Body**:
- `quality`: Rating 0-5
  - 0: Complete blackout
  - 1: Incorrect, but familiar
  - 2: Incorrect, but easy to recall
  - 3: Correct, but difficult
  - 4: Correct, with hesitation
  - 5: Perfect recall

**Response** (200 OK):
```json
{
  "card_id": 1,
  "quality": 5,
  "new_ease_factor": 2.6,
  "new_interval": 1,
  "new_repetitions": 1,
  "next_due_date": "2025-10-22T12:00:00"
}
```

**SM-2 Algorithm**:
- First repetition: 1 day
- Second repetition: 6 days
- Subsequent: interval * ease_factor
- Quality < 3 resets progress

## AI Endpoints

AI-powered features for flashcard creation and study assistance.

### Chat with AI Assistant

Conversational AI with CourtListener case law integration.

```http
POST /api/v1/ai/chat
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "Explain Miranda v. Arizona"}
  ],
  "stream": true,
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**Response**: Server-Sent Events (SSE) stream or JSON

**Parameters**:
- `messages`: Array of message objects (required)
- `stream`: Enable streaming (default: true)
- `temperature`: 0.0-2.0 (default: 0.7)
- `max_tokens`: 1-4096 (default: 2000)

### Rewrite Flashcard

Improve flashcard quality using AI.

```http
POST /api/v1/ai/rewrite-card
Content-Type: application/json

{
  "front": "What is Miranda?",
  "back": "A case about rights",
  "instruction": "Make more specific and add citations"
}
```

**Response**: SSE stream with improvements

**Parameters**:
- `front`: Current front text (required)
- `back`: Current back text (required)
- `instruction`: Optional rewrite instruction

### Autocomplete Card

AI-powered suggestions for card creation.

```http
POST /api/v1/ai/autocomplete-card
Content-Type: application/json

{
  "partial_text": "What are the elements of",
  "card_type": "front"
}
```

**Response**: SSE stream with completion suggestions

**Parameters**:
- `partial_text`: Partial text (required)
- `card_type`: "front" or "back" (required)

### AI Health Check

```http
GET /api/v1/ai/health
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "grok_configured": true,
  "courtlistener_configured": true,
  "model": "grok-beta",
  "rate_limiting_enabled": true
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity
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

### 500 Internal Server Error
```json
{
  "detail": "An error occurred while processing your request"
}
```

## Rate Limiting

Rate limits are applied to prevent abuse:
- Per minute: 10 requests
- Per hour: 100 requests

When rate limit is exceeded:
```json
{
  "detail": "Rate limit exceeded"
}
```

**Response Headers**:
- `X-RateLimit-Limit`: Rate limit cap
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Time when limit resets

## Best Practices

1. **Authentication**: Always store JWT tokens securely (e.g., httpOnly cookies)
2. **Token Refresh**: Implement token refresh before expiration
3. **Pagination**: Use limit parameters for large result sets
4. **Error Handling**: Handle all error status codes appropriately
5. **Streaming**: Use streaming for AI endpoints to improve UX
6. **Rate Limits**: Implement exponential backoff when rate limited

## Configuration

Environment variables for API configuration:

```bash
# Database
DATABASE_URL=sqlite:///./flashcase.db

# Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI/Grok
GROK_API_KEY=your_api_key
GROK_API_BASE_URL=https://api.x.ai/v1
GROK_MODEL=grok-beta

# CourtListener
COURTLISTENER_API_KEY=your_api_key
COURTLISTENER_API_BASE_URL=https://www.courtlistener.com/api/rest/v3

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_PER_HOUR=100

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

## SDK Examples

### Python

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    data={"username": "user", "password": "pass"}
)
token = response.json()["access_token"]

# Create deck
headers = {"Authorization": f"Bearer {token}"}
deck = requests.post(
    "http://localhost:8000/api/v1/decks/",
    headers=headers,
    json={"name": "My Deck"}
).json()

# Get study session
cards = requests.get(
    f"http://localhost:8000/api/v1/study/session/{deck['id']}",
    headers=headers
).json()
```

### JavaScript

```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/x-www-form-urlencoded'},
  body: 'username=user&password=pass'
});
const { access_token } = await loginResponse.json();

// Create deck
const deckResponse = await fetch('http://localhost:8000/api/v1/decks/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({name: 'My Deck'})
});
const deck = await deckResponse.json();

// Get study session
const cardsResponse = await fetch(
  `http://localhost:8000/api/v1/study/session/${deck.id}`,
  {headers: {'Authorization': `Bearer ${access_token}`}}
);
const cards = await cardsResponse.json();
```

## Testing

Run the test suite:

```bash
cd backend
pytest tests/ -v
```

**Test Coverage**:
- Authentication: 15 tests
- Protected endpoints: 18 tests
- Schema validation: 3 tests
- SRS algorithm: 15 tests
- AI endpoints: 9 tests

**Total**: 60 tests passing

## Version History

### v1 (Current)
- JWT authentication
- Complete CRUD for decks and cards
- Spaced repetition study system (SM-2)
- AI-powered features (chat, rewrite, autocomplete)
- Pydantic schema validation
- Rate limiting

---

**Last Updated**: October 21, 2025
**API Version**: 1
**Status**: Production Ready

## Content Moderation & Reporting

### Overview

FlashCase includes automated content moderation and user reporting features to maintain a safe learning environment.

**Features**:
- Automated profanity filtering on all user-generated content
- User reporting system for inappropriate content
- Admin review and management of reports

**See also**: [CONTENT_MODERATION.md](./CONTENT_MODERATION.md) for detailed documentation.

### Create Report

Submit a report for inappropriate content.

```http
POST /api/v1/reports/
Authorization: Bearer {token}
Content-Type: application/json

{
  "report_type": "deck",
  "content_id": 123,
  "reason": "inappropriate",
  "description": "This deck contains offensive content"
}
```

**Request Body**:
- `report_type` (required): "deck" or "card"
- `content_id` (required): ID of the content being reported
- `reason` (required): "inappropriate", "spam", "copyright", "misleading", or "other"
- `description` (optional): Additional details (max 500 characters)

**Response** (201 Created):
```json
{
  "id": 1,
  "reporter_id": 42,
  "report_type": "deck",
  "content_id": 123,
  "reason": "inappropriate",
  "description": "This deck contains offensive content",
  "status": "pending",
  "reviewed_by": null,
  "admin_notes": null,
  "created_at": "2025-10-21T12:00:00",
  "updated_at": "2025-10-21T12:00:00"
}
```

### Get My Reports

Retrieve reports submitted by the current user.

```http
GET /api/v1/reports/my-reports
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "reporter_id": 42,
    "report_type": "deck",
    "content_id": 123,
    "reason": "inappropriate",
    "description": "This deck contains offensive content",
    "status": "pending",
    "reviewed_by": null,
    "admin_notes": null,
    "created_at": "2025-10-21T12:00:00",
    "updated_at": "2025-10-21T12:00:00"
  }
]
```

### List All Reports (Admin Only)

List all reports with optional filtering.

```http
GET /api/v1/reports/?status_filter=pending&report_type=deck
Authorization: Bearer {admin_token}
```

**Query Parameters**:
- `status_filter` (optional): Filter by status ("pending", "reviewed", "resolved", "dismissed")
- `report_type` (optional): Filter by type ("deck", "card")

**Response** (200 OK): Array of report objects
**Error** (403 Forbidden): If user is not an admin

### Get Report Details (Admin Only)

Get details of a specific report.

```http
GET /api/v1/reports/{report_id}
Authorization: Bearer {admin_token}
```

**Response** (200 OK): Report object
**Error** (403 Forbidden): If user is not an admin
**Error** (404 Not Found): If report doesn't exist

### Update Report Status (Admin Only)

Update report status and add admin notes.

```http
PUT /api/v1/reports/{report_id}
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "status": "resolved",
  "admin_notes": "Content removed and user warned"
}
```

**Request Body**:
- `status` (required): New status ("pending", "reviewed", "resolved", "dismissed")
- `admin_notes` (optional): Admin notes (max 1000 characters)

**Response** (200 OK): Updated report object
**Error** (403 Forbidden): If user is not an admin

### Delete Report (Admin Only)

Delete a report.

```http
DELETE /api/v1/reports/{report_id}
Authorization: Bearer {admin_token}
```

**Response** (204 No Content): Success
**Error** (403 Forbidden): If user is not an admin
**Error** (404 Not Found): If report doesn't exist

### Content Moderation

All content creation and update endpoints automatically validate content for inappropriate language:

**Protected Endpoints**:
- `POST /api/v1/decks/` - Create deck
- `PUT /api/v1/decks/{deck_id}` - Update deck
- `POST /api/v1/cards/` - Create card
- `PUT /api/v1/cards/{card_id}` - Update card

**Validation**:
Content is checked for profanity in:
- Deck names and descriptions
- Card front and back text

**Error Response** (400 Bad Request):
```json
{
  "detail": "Deck name: Content contains inappropriate language"
}
```

### Legal & AI Disclaimers

All frontend pages display appropriate disclaimers:

**Legal Disclaimer** (All pages):
> ⚖️ Not Legal Advice: FlashCase is an educational tool designed to help law students study. The content provided through this platform does not constitute legal advice and should not be relied upon for legal decisions. Always consult with a qualified attorney for specific legal matters.

**AI Disclaimer** (Create page):
> 🤖 AI-Generated Content: This platform uses artificial intelligence to assist with content generation. AI-generated content may contain errors, inaccuracies, or outdated information. Always verify important information with authoritative sources and use AI features as a study aid, not as a definitive legal resource.

---

**Last Updated**: October 21, 2025
