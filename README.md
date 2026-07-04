# AI Kubernetes Troubleshooting Agent

An on-demand AI troubleshooting system for Kubernetes clusters. This agent helps diagnose issues, identify root causes, and suggest fixes using AI reasoning.

## Architecture

```
Frontend (Next.js)
    ↓
FastAPI Backend (Orchestrator)
    ↓
Kubernetes Investigation Layer
    ↓
AI Kubernetes Agent
    ↓
LLM Reasoning (OpenRouter via InsForge)
    ↓
Root Cause + Suggested Fix
    ↓
Frontend Diagnosis
```

## Project Structure

```
ai-kubernetes-agent/
├── backend/
│   ├── api/                 # API endpoints
│   ├── core/               # Configuration and core utilities
│   ├── kubernetes/         # Kubernetes investigation layer
│   ├── ai/                 # AI reasoning layer
│   ├── models/             # Data models and schemas
│   ├── services/           # Business logic services
│   ├── main.py             # FastAPI app entry point
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile          # Backend container
│   └── .env                # Backend environment variables
├── frontend/
│   ├── app/                # Next.js app directory
│   ├── components/         # React components
│   ├── services/           # API services
│   ├── hooks/              # Custom React hooks
│   ├── types/              # TypeScript types
│   ├── package.json        # Node dependencies
│   ├── Dockerfile          # Frontend container
│   ├── next.config.js      # Next.js configuration
│   ├── tsconfig.json       # TypeScript configuration
│   ├── tailwind.config.ts  # Tailwind CSS configuration
│   └── .env.local          # Frontend environment variables
├── docs/                   # Documentation
├── prompts/                # AI prompts
├── docker-compose.yml      # Docker Compose configuration
└── README.md               # This file
```

## Tech Stack

### Backend
- **FastAPI** - Modern async web framework
- **Python 3.12+** - Programming language
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **Loguru** - Logging
- **HTTPX** - Async HTTP client

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS 3.4** - Utility-first CSS
- **React Query** - Server state management
- **Axios** - HTTP client

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Local orchestration

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Or: Python 3.12+ and Node.js 18+

### Option 1: Docker Compose (Recommended)

```bash
# Navigate to project root
cd ai-kubernetes-agent

# Build and start services
docker compose up --build
```

Access:
- Frontend: http://localhost:3000
- Backend Health: http://localhost:8000/health
- Backend Root: http://localhost:8000

### Option 2: Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

## Environment Variables

### Backend (.env)

```env
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=your_model_here
KUBECONFIG_PATH=/path/to/kubeconfig
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## API Endpoints

### Health Check

```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "ai-kubernetes-agent"
}
```

### Root

```
GET /
```

Response:
```json
{
  "message": "AI Kubernetes Agent API"
}
```

## Frontend Features

- Clean, professional UI
- Status indicator
- Investigate Cluster button
- Responsive design with Tailwind CSS

## Development

### Backend Development

The backend is structured for modular development:

- `kubernetes/`: Add cluster inspection logic
- `ai/`: Add AI reasoning and analysis
- `services/`: Add business logic
- `api/`: Add API endpoints
- `models/`: Add data schemas

### Frontend Development

The frontend uses Next.js App Router:

- `components/`: Create reusable React components
- `services/`: Add API client functions
- `hooks/`: Create custom hooks
- `types/`: Define TypeScript interfaces

## Testing

Health check endpoint:
```bash
curl http://localhost:8000/health
```

## Deployment

### Docker Build

```bash
# Backend
docker build -t ai-kubernetes-agent-backend ./backend

# Frontend
docker build -t ai-kubernetes-agent-frontend ./frontend
```

### Production

Configure environment variables and update docker-compose.yml for production settings.

## Troubleshooting

### Port Already in Use

Change ports in docker-compose.yml:
- Backend: Change 8000:8000 to 8001:8000
- Frontend: Change 3000:3000 to 3001:3000

### Module Not Found Errors

**Backend:**
```bash
pip install -r requirements.txt
```

**Frontend:**
```bash
npm install
```

### Connection Refused

Ensure both services are running:
```bash
docker compose ps
```

## Future Features

- Kubernetes cluster inspection
- AI-powered diagnostics
- Root cause analysis
- Fix recommendations
- Real-time monitoring
- Authentication

## Notes

- This is a foundation setup - placeholder implementations provided
- Do not implement Kubernetes logic until architecture is finalized
- Use Tailwind CSS 3.4 (do not upgrade to v4)
- All code follows production-style patterns

## License

MIT
