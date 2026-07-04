# Quick Start Guide

## Prerequisites

- Docker & Docker Compose
- OpenRouter API Key (from InsForge)
- Git (optional)

## Setup (5 minutes)

### 1. Get OpenRouter API Key

From your InsForge account:
1. Go to backend settings
2. Copy `OPENROUTER_API_KEY`
3. Copy `OPENROUTER_MODEL` (optional, defaults to `openrouter/auto`)

### 2. Configure Environment

In `backend/.env`:
```env
OPENROUTER_API_KEY=sk_...
OPENROUTER_MODEL=openrouter/auto
```

In `frontend/.env.local`:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 3. Start Services

```bash
cd ai-kubernetes-agent
docker compose up --build
```

Wait for services to start:
```
✓ Backend ready on port 8000
✓ Frontend ready on port 3000
```

## Usage

### 1. Open Dashboard

Go to: http://localhost:3000

You'll see:
```
AI Kubernetes Agent

[ Investigate Cluster ]

System Status: Ready
```

### 2. Click Investigate

Click the button to start investigation.

### 3. Watch Progress

Real-time progress:
```
✓ Checking Pods
✓ Reading Logs
✓ Analyzing Events
✓ Inspecting Deployments
✓ Checking Networking
✓ AI Reasoning
✓ Root Cause Found
```

### 4. View Diagnosis

When investigation completes:

**Root Cause**
```
DATABASE_URL missing
```

**Explanation**
```
Application cannot connect to database...
```

**Suggested Fix**
```
Add DATABASE_URL environment variable...
```

**kubectl Command**
```
kubectl set env deployment/... DATABASE_URL=...
```

**Confidence**
```
92%
```

### 5. Check History

Previous investigations are saved at bottom:
```
Recent Investigations

ImagePullBackOff
2026-07-04 12:34:56  |  88%

CrashLoopBackOff
2026-07-04 12:20:15  |  95%
```

## Testing Without Kubernetes

The system works even without kubectl installed:

```json
{
  "root_cause": "No issues detected",
  "confidence": 100
}
```

To test with real data, deploy to a Kubernetes cluster and configure kubeconfig.

## API Direct Testing

Test backend directly:

### PowerShell
```powershell
Invoke-WebRequest -Uri http://localhost:8000/api/investigate -Method POST
```

### PowerShell (Pretty Print)
```powershell
$result = Invoke-WebRequest -Uri http://localhost:8000/api/investigate -Method POST
$result.Content | ConvertFrom-Json | ConvertTo-Json
```

## Troubleshooting

### "Connection refused"

Backend not running.

```bash
docker compose up
```

### "Cannot find module 'axios'"

Frontend dependencies missing.

```bash
cd frontend
npm install
```

### "OPENROUTER_API_KEY not configured"

Set environment variable.

```env
OPENROUTER_API_KEY=sk_...
```

### Investigation shows "No issues"

kubectl not installed (expected for local testing).

To enable, install kubectl and configure kubeconfig.

## Architecture Overview

```
Frontend (Next.js)
  ↓ HTTP
Backend (FastAPI)
  ↓
Kubernetes Investigation
  ↓ kubectl
Cluster
  ↓
LLM (OpenRouter)
  ↓
AI Analysis
  ↓ JSON
Dashboard Display
```

## Project Structure

```
ai-kubernetes-agent/
├── backend/               # FastAPI backend
│   ├── kubernetes/       # Investigation layer
│   ├── ai/              # AI reasoning
│   ├── api/             # API endpoints
│   └── main.py
├── frontend/             # Next.js frontend
│   ├── app/            # Dashboard
│   └── public/
├── docker-compose.yml
└── README.md
```

## Next Steps

### Now You Can:
✓ Investigate Kubernetes clusters
✓ Get AI-powered diagnosis
✓ View suggested fixes
✓ Track investigation history

### To Add:
- [ ] User authentication
- [ ] Persistent history (database)
- [ ] Real-time updates (WebSocket)
- [ ] PDF export
- [ ] Scheduled investigations
- [ ] Slack notifications

## Documentation

- `README.md` - Full project docs
- `KUBERNETES_INVESTIGATION_LAYER.md` - Investigation details
- `AI_REASONING_ENGINE.md` - AI reasoning details
- `DASHBOARD_AND_API.md` - Frontend/API integration

## Support

If issues occur:

1. Check logs: `docker compose logs`
2. Restart: `docker compose down` then `docker compose up`
3. Rebuild: `docker compose up --build`

## That's It!

You now have a fully functional AI-powered Kubernetes troubleshooting system.

Start investigating! 🚀
