# Dashboard & API Integration

## Overview

The Dashboard provides a professional UI for investigating Kubernetes clusters. It integrates with the FastAPI backend to deliver real-time investigation results and AI-powered diagnosis.

## Architecture

```
Frontend (Next.js + React)
    ↓
Axios HTTP Client
    ↓
FastAPI Backend
    ↓
Investigation + AI Reasoning
    ↓
Diagnosis Response
    ↓
Dashboard Display + History Storage
```

## Frontend Components

### 1. Main Dashboard (`app/page.tsx`)

**Features:**
- Investigation button
- Real-time progress display
- Diagnosis display
- Investigation history (localStorage)
- Error handling
- Loading states

**State Management:**
- `isInvestigating` - Investigation in progress
- `diagnosis` - Current diagnosis result
- `history` - Recent investigations (localStorage)
- `error` - Error messages
- `progress` - Investigation progress steps

### 2. Header Section

Displays:
- Application title: "AI Kubernetes Agent"
- Tagline: "Intelligent cluster troubleshooting"

### 3. Investigation Section

**Button:**
```
[ Investigate Cluster ]
```

**Progress Display:**
Shows real-time steps:
```
✓ Checking Pods
✓ Reading Logs
✓ Analyzing Events
✓ Inspecting Deployments
✓ Checking Networking
✓ AI Reasoning
✓ Root Cause Found
```

**Error Display:**
Shows any investigation errors with red styling.

### 4. Diagnosis Section

Displays when diagnosis is received:

**Root Cause (Card 1)**
- Large, bold text
- Primary finding

**Confidence (Card 2)**
- Percentage display
- Progress bar visualization
- 0-100% scale

**Explanation**
- Detailed description
- Context about the issue

**Suggested Fix**
- Actionable recommendation
- Beginner-friendly language

**kubectl Command**
- Terminal-style display
- Copy-able command

### 5. Investigation History

**Display:**
- Last 10 investigations (localStorage)
- Timestamp
- Root cause
- Confidence score

**Example:**
```
ImagePullBackOff
2026-07-04 12:34:56  |  88% Confidence

CrashLoopBackOff
2026-07-04 12:20:15  |  95% Confidence

OOMKilled
2026-07-04 11:45:32  |  92% Confidence
```

## API Integration

### Endpoint: POST /api/investigate

**Request:**
```http
POST http://localhost:8000/api/investigate
Content-Type: application/json
```

No request body required.

**Response:**
```json
{
  "status": "success",
  "timestamp": "2026-07-04T12:34:56.789Z",
  "investigation": {
    "pods": {...},
    "logs": {...},
    "events": {...},
    "deployments": {...},
    "network": {...}
  },
  "diagnosis": {
    "root_cause": "DATABASE_URL missing",
    "explanation": "Application cannot connect to database...",
    "fix": "Add DATABASE_URL environment variable...",
    "kubectl_command": "kubectl set env deployment/payment-service DATABASE_URL=...",
    "prevention": "Store in ConfigMap or Secret...",
    "confidence": 92
  },
  "diagnosis_status": "success"
}
```

## Frontend → Backend Flow

### Step 1: User Clicks Button

```javascript
handleInvestigate()
```

- Set `isInvestigating = true`
- Clear previous diagnosis
- Clear error
- Reset progress

### Step 2: Show Progress

```javascript
updateProgress('Checking Pods')
updateProgress('Reading Logs')
// ... etc
```

Progress steps are shown immediately (optimistic UI).

### Step 3: Call API

```javascript
const response = await axios.post(
  `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/investigate`
)
```

**Error Handling:**
- Catch exceptions
- Display error message
- Show "Error: ..." in progress
- Keep UI responsive

### Step 4: Receive Diagnosis

```javascript
setDiagnosis(response.data.diagnosis)
addToHistory(response.data.diagnosis)
```

- Display diagnosis cards
- Add to investigation history
- Save to localStorage

### Step 5: Update UI

- Progress shows "Root Cause Found"
- Diagnosis section displays
- History section updates
- Investigation complete

## Data Storage

### localStorage Key

```
"investigation_history"
```

**Structure:**
```json
[
  {
    "timestamp": "2026-07-04T12:34:56.789Z",
    "root_cause": "DATABASE_URL missing",
    "confidence": 92
  },
  ...
]
```

**Limits:**
- Max 10 entries
- Persists in browser
- Clears on browser data clear

## Environment Configuration

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### Backend (.env)

```env
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openrouter/auto
```

## Error Scenarios

### 1. API Unreachable

**Frontend Error:**
```
Connection refused or network error
```

**Display:**
```
Error
Connection failed. Check if backend is running.
```

### 2. No OpenRouter Key

**Backend Response:**
```json
{
  "status": "error",
  "error": "OpenRouter API key not configured"
}
```

**Frontend Display:**
```
Error
OpenRouter API key not configured
```

### 3. kubectl Not Installed

**Backend Response:**
```json
{
  "status": "success",
  "diagnosis": {
    "root_cause": "No issues detected",
    "confidence": 0
  }
}
```

**Frontend Display:**
Normal diagnosis flow (investigation had no data).

### 4. Request Timeout

**Frontend Error:**
```
Timeout exceeded
```

**Display:**
```
Error
Request timed out after 60 seconds
```

## UI Design

### Colors

- **Background:** `slate-950` / `slate-900` (dark)
- **Cards:** `slate-800` with `slate-700` borders
- **Text:** `white` / `slate-200` (light)
- **Accent:** `blue-600` (button) / `green-400` (success)
- **Error:** `red-600` / `red-900`

### Typography

- **Header:** 30px, bold, white
- **Section Title:** 24px, bold, white
- **Card Title:** 14px, uppercase, slate-400
- **Card Value:** 18px, bold, white
- **Body Text:** 16px, slate-200

### Spacing

- **Container:** Max 1440px (max-w-6xl)
- **Padding:** 32px (8)
- **Gap:** 24px (6)
- **Border Radius:** 8px (lg)

## Performance

- **Initial Load:** < 1 second
- **Investigation Time:** 15-45 seconds (depends on cluster)
- **UI Responsiveness:** Instant feedback on button click
- **localStorage Size:** < 10KB

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (responsive)

## Testing

### Manual Testing

1. **Start Backend:**
```bash
docker compose up
```

2. **Open Frontend:**
```
http://localhost:3000
```

3. **Click Button:**
```
[ Investigate Cluster ]
```

4. **Observe:**
- Progress updates in real-time
- Diagnosis displays when ready
- History updates

### Test Scenarios

**No Issues:**
```
Root Cause: No issues detected
Confidence: 100%
```

**With Issues:**
```
Root Cause: DATABASE_URL missing
Confidence: 92%
```

**API Error:**
```
Error: Connection failed
```

## Security

✓ **No secrets exposed:**
- API key only used on backend
- Frontend only knows base URL
- No sensitive data in localStorage

✓ **CORS configured:**
- Backend allows all origins
- Production: Restrict to domain

✓ **Input validation:**
- Backend validates all data
- Frontend assumes valid backend

## Future Enhancements

1. Authentication (InsForge SDK)
2. Persistent history (database)
3. Real-time updates (WebSocket)
4. Export diagnosis (PDF/JSON)
5. Comparison between investigations
6. Alert rules
7. Scheduled investigations

## Troubleshooting

### "Cannot GET /"

- Frontend not running
- Run: `npm run dev` in frontend folder

### "Connection refused"

- Backend not running
- Run: `docker compose up` in project root

### "No diagnosis received"

- Backend error
- Check backend logs: `docker compose logs backend`

### History not persisting

- Browser localStorage disabled
- Private/incognito mode
- Clear browser data

## Documentation

See also:
- `KUBERNETES_INVESTIGATION_LAYER.md` - Backend investigation
- `AI_REASONING_ENGINE.md` - AI reasoning details
- `README.md` - Full project documentation
