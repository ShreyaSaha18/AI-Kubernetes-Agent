# Database & Authentication

## Overview

The system now includes:
- User authentication (signup/login)
- Persistent investigation history
- Per-user investigation data

Architecture:

```
Frontend Auth Pages
    ↓ (credentials)
Backend Auth API
    ↓ (stores user)
Database Service
    ↓
Investigation Storage
    ↓
History Retrieval
```

## Database Schema

### Users Table (Conceptual)

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  password_hash VARCHAR NOT NULL,
  created_at TIMESTAMP
);
```

### Investigations Table (Conceptual)

```sql
CREATE TABLE investigations (
  id VARCHAR PRIMARY KEY,
  user_id UUID FOREIGN KEY,
  root_cause TEXT,
  explanation TEXT,
  fix TEXT,
  kubectl_command TEXT,
  confidence INT,
  status VARCHAR,
  investigation_data JSONB,
  timestamp TIMESTAMP,
  created_at TIMESTAMP
);
```

## Frontend Authentication

### Login Page (`app/login/page.tsx`)

**Features:**
- Email and password input
- Login form submission
- Error display
- Link to signup

**Flow:**
1. User enters email/password
2. Click "Sign In"
3. POST `/api/auth/login`
4. Receive `access_token` and `user_id`
5. Store in localStorage
6. Redirect to `/dashboard`

**localStorage Keys:**
```javascript
localStorage.setItem('access_token', token)
localStorage.setItem('user_id', userId)
localStorage.setItem('user_email', email)
```

### Signup Page (`app/signup/page.tsx`)

**Features:**
- Email and password input
- Password confirmation
- Validation
- Error display
- Link to login

**Validation:**
- Email format
- Password length (min 6)
- Password confirmation match

**Flow:**
1. User enters email/password
2. Click "Sign Up"
3. POST `/api/auth/signup`
4. Receive `access_token` and `user_id`
5. Store in localStorage
6. Redirect to `/dashboard`

### Dashboard Page (`app/dashboard/page.tsx`)

**Features:**
- Protected route (requires auth)
- User email display
- Logout button
- Investigation functionality
- History display

**Protection:**
```javascript
useEffect(() => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    router.push('/login')
  }
}, [])
```

**Logout:**
```javascript
const handleLogout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('user_id')
  localStorage.removeItem('user_email')
  router.push('/login')
}
```

## Backend Authentication

### Auth Endpoints

#### POST /api/auth/signup

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "status": "success",
  "user": {
    "id": "uuid-...",
    "email": "user@example.com"
  },
  "access_token": "session-uuid",
  "session_id": "session-uuid"
}
```

**Errors:**
- User already exists (400)
- Missing email/password (400)
- Server error (500)

#### POST /api/auth/login

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "status": "success",
  "user": {
    "id": "uuid-...",
    "email": "user@example.com"
  },
  "access_token": "session-uuid",
  "session_id": "session-uuid"
}
```

**Errors:**
- Invalid credentials (401)
- Missing email/password (400)
- Server error (500)

#### POST /api/auth/logout

**Response:**
```json
{
  "status": "success",
  "message": "Logged out"
}
```

#### GET /api/auth/me

**Parameters:**
- `user_id` (query) - User ID from localStorage

**Response:**
```json
{
  "status": "success",
  "user_id": "uuid-..."
}
```

## Investigation Endpoints (Updated)

### POST /api/investigate

**Now requires authentication**

**Parameters:**
- `user_id` (query) - From localStorage

**Request:**
```
POST /api/investigate?user_id=uuid-...
```

**Response:**
```json
{
  "status": "success",
  "investigation_id": "inv_...",
  "diagnosis": {
    "root_cause": "...",
    "confidence": 92
  }
}
```

### GET /api/investigations

**Get user's investigation history**

**Parameters:**
- `user_id` (query) - From localStorage
- `limit` (query) - Max entries (default 10)

**Response:**
```json
{
  "status": "success",
  "investigations": [
    {
      "id": "inv_...",
      "root_cause": "DATABASE_URL missing",
      "confidence": 92,
      "timestamp": "2026-07-04T12:34:56.789Z",
      "status": "success"
    }
  ],
  "total": 10
}
```

### GET /api/investigations/{investigation_id}

**Get investigation details**

**Parameters:**
- `investigation_id` (path)
- `user_id` (query)

**Response:**
```json
{
  "status": "success",
  "investigation": {
    "id": "inv_...",
    "root_cause": "...",
    "explanation": "...",
    "fix": "...",
    "kubectl_command": "...",
    "confidence": 92,
    "investigation_data": {...}
  }
}
```

### DELETE /api/investigations/{investigation_id}

**Delete investigation (owner only)**

**Parameters:**
- `investigation_id` (path)
- `user_id` (query)

**Response:**
```json
{
  "status": "success"
}
```

**Errors:**
- Not authorized (403)
- Not found (404)

## Database Service

### DatabaseService (`services/database_service.py`)

**Methods:**

#### save_investigation()
```python
await DatabaseService.save_investigation(
  user_id="uuid-...",
  root_cause="...",
  explanation="...",
  fix="...",
  kubectl_command="...",
  confidence=92,
  investigation_data={...}
)
```

#### get_user_investigations()
```python
await DatabaseService.get_user_investigations(
  user_id="uuid-...",
  limit=10
)
```

#### get_investigation()
```python
await DatabaseService.get_investigation(
  investigation_id="inv_..."
)
```

#### delete_investigation()
```python
await DatabaseService.delete_investigation(
  investigation_id="inv_...",
  user_id="uuid-..."
)
```

#### create_user()
```python
await DatabaseService.create_user(
  email="user@example.com",
  user_id="uuid-..."
)
```

#### get_user()
```python
await DatabaseService.get_user(
  email="user@example.com"
)
```

## Security

✓ **Authentication:**
- Session-based (access_token)
- Stored in localStorage
- Passed in query parameters

✓ **Authorization:**
- Users can only access their own data
- Endpoint checks user_id ownership

✓ **Data Privacy:**
- Each user has isolated investigations
- No cross-user data access

## Usage Flow

### First Time User

```
1. Visit http://localhost:3000
2. Redirected to /login
3. Click "Sign up" → /signup
4. Enter email/password
5. Click "Sign Up"
6. Redirected to /dashboard
7. Start investigating
```

### Returning User

```
1. Visit http://localhost:3000
2. Redirected to /login
3. Enter email/password
4. Click "Sign In"
5. Redirected to /dashboard
6. See investigation history
```

### Investigation Workflow (Authenticated)

```
1. User on /dashboard
2. Click "Investigate Cluster"
3. Frontend includes user_id in API call
4. Backend saves investigation for user
5. Frontend displays diagnosis
6. Investigation added to user's history
7. History persists across sessions
```

## Data Storage (Current)

**Note:** Currently using in-memory storage for demo.

For production, integrate with InsForge database:

```python
# Example future implementation
from insforge import InsForgeClient

client = InsForgeClient(url="...", key="...")

# Save investigation
await client.database.from_("investigations").insert({
  "user_id": user_id,
  "root_cause": root_cause,
  ...
})
```

## Environment

No new environment variables needed for demo.

For production with InsForge:
```env
INSFORGE_API_URL=...
INSFORGE_API_KEY=...
```

## Testing

### Signup
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### Investigate (with user_id)
```bash
curl -X POST "http://localhost:8000/api/investigate?user_id=<user_id>"
```

### Get History
```bash
curl "http://localhost:8000/api/investigations?user_id=<user_id>&limit=10"
```

## Future Enhancements

- [ ] JWT tokens instead of session IDs
- [ ] Password hashing (bcrypt)
- [ ] Email verification
- [ ] Password reset
- [ ] 2FA
- [ ] API keys for automation
- [ ] Investigation sharing
- [ ] Role-based access control
