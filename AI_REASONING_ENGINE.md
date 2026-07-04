# AI Reasoning Engine

## Overview

The AI Reasoning Engine makes the system intelligent. It behaves like a **Senior Kubernetes SRE** analyzing cluster issues.

It consumes the Kubernetes investigation payload and generates:
- Root cause analysis
- Suggested fixes
- kubectl commands
- Prevention recommendations
- Confidence score

## Architecture

```
Investigation Data (Pods, Logs, Events, etc.)
    ↓
Prompt Builder (Structured prompt creation)
    ↓
LLM Client (OpenRouter API)
    ↓
Root Cause Analyzer (Parse & validate response)
    ↓
Kubernetes Agent (Orchestrator)
    ↓
Diagnosis
```

## Components

### 1. LLM Client (`ai/llm_client.py`)

Handles OpenRouter API communication.

**Features:**
- Async HTTPX client
- API key from InsForge (`OPENROUTER_API_KEY`)
- Model selection (`OPENROUTER_MODEL`)
- Timeout handling (60 seconds)
- Error handling and logging
- No secret exposure

**Configuration:**
```env
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openai/gpt-4-turbo
```

**Example:**
```python
client = LLMClient()
result = await client.generate(messages, temperature=0.7)
```

### 2. Prompt Builder (`ai/prompt_builder.py`)

Creates structured prompts for consistent AI reasoning.

**System Prompt:**
```
Senior Kubernetes SRE with 10+ years of experience.

Responsibilities:
- Correlate pod status, logs, events, deployment state
- Identify root causes, not just symptoms
- Provide practical, actionable fixes
- Include specific kubectl commands
- Suggest prevention measures
- Rate confidence level
```

**Example Input:**
```json
{
  "pods": {
    "problematic_pods": [
      {
        "name": "payment-service",
        "status": "CrashLoopBackOff"
      }
    ]
  },
  "logs": {
    "logs": [
      {
        "pod": "payment-service",
        "logs": ["[ERROR] DATABASE_URL not set"]
      }
    ]
  }
}
```

**Output:**
```
[PODS] Issues found:
  - payment-service (default): CrashLoopBackOff
[LOGS] Error messages:
  From payment-service:
    [ERROR] DATABASE_URL not set
```

### 3. Root Cause Analyzer (`ai/root_cause_analyzer.py`)

Analyzes investigation data and correlates findings.

**Features:**
- Sends formatted investigation to LLM
- Parses JSON response
- Validates diagnosis structure
- Error handling for malformed responses

**Response Validation:**
```json
{
  "root_cause": "Missing environment variable",
  "explanation": "App cannot connect to database",
  "fix": "Add DATABASE_URL environment variable",
  "kubectl_command": "kubectl set env deployment/payment-service DATABASE_URL=postgres://...",
  "prevention": "Add required vars to ConfigMap and mount in deployment",
  "confidence": 92
}
```

### 4. Kubernetes Agent (`ai/kubernetes_agent.py`)

Orchestrates the entire AI reasoning flow.

**Responsibilities:**
- Check if issues exist
- Route to AI analysis
- Return healthy cluster message if no issues
- Handle analysis errors

**Example:**
```python
agent = KubernetesAgent()
diagnosis = await agent.diagnose(investigation_data)
```

## API Integration

### Endpoint: POST /api/investigate

**Complete flow:**
1. Collect Kubernetes evidence
2. Send to AI Agent
3. LLM analyzes and reasons
4. Return diagnosis with confidence

**Request:**
```http
POST /api/investigate
Content-Type: application/json
```

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
    "root_cause": "DATABASE_URL environment variable missing",
    "explanation": "The payment-service pod is failing to start because it cannot connect to the database. The DATABASE_URL environment variable is not set in the deployment.",
    "fix": "Add the DATABASE_URL environment variable to the payment-service deployment.",
    "kubectl_command": "kubectl set env deployment/payment-service -n default DATABASE_URL=postgres://db:5432/payments",
    "prevention": "Store sensitive URLs in Secrets and mount via ConfigMap or directly as env vars. Add startup probes to detect missing config early.",
    "confidence": 95
  },
  "diagnosis_status": "success"
}
```

## Error Handling

**Missing API Key:**
```json
{
  "status": "error",
  "diagnosis": null,
  "error": "OpenRouter API key not configured"
}
```

**Network Error:**
```json
{
  "status": "error",
  "diagnosis": null,
  "error": "OpenRouter connection error: ..."
}
```

**Timeout:**
```json
{
  "status": "error",
  "diagnosis": null,
  "error": "OpenRouter request timed out (60s)"
}
```

**Healthy Cluster:**
```json
{
  "status": "success",
  "diagnosis": {
    "root_cause": "No issues detected",
    "explanation": "Cluster appears to be healthy",
    "fix": "No action needed",
    "kubectl_command": "N/A",
    "prevention": "Continue monitoring",
    "confidence": 100
  },
  "diagnosis_status": "success"
}
```

## Configuration

### Environment Variables

```env
# OpenRouter API (from InsForge)
OPENROUTER_API_KEY=sk_...
OPENROUTER_MODEL=openai/gpt-4-turbo
```

### Supported Models

- `openrouter/auto` - Default (auto-selects best model)
- `openai/gpt-4-turbo` - Advanced reasoning
- `openai/gpt-3.5-turbo` - Faster, cost-effective
- `anthropic/claude-3-opus` - Strong analysis
- Any OpenRouter supported model

## Logging

All components log their operations:

```
INFO | ai.kubernetes_agent:diagnose:20 - Kubernetes Agent starting diagnosis
INFO | ai.root_cause_analyzer:analyze:30 - Starting root cause analysis
INFO | ai.llm_client:generate:45 - Sending request to OpenRouter (openai/gpt-4-turbo)
INFO | ai.llm_client:generate:65 - LLM response received successfully
INFO | ai.root_cause_analyzer:analyze:45 - Analysis complete: DATABASE_URL missing
```

## Example Workflows

### Scenario 1: Missing Environment Variable

**Investigation finds:**
- Pod: CrashLoopBackOff
- Logs: `DATABASE_URL not set`
- Events: `BackOff` restarting

**AI Diagnosis:**
```
Root Cause: Missing DATABASE_URL environment variable
Explanation: Application startup requires database connection
Fix: Add DATABASE_URL to deployment
kubectl command: kubectl set env deployment/...
Prevention: Store in ConfigMap or Secret
Confidence: 95%
```

### Scenario 2: Image Pull Failure

**Investigation finds:**
- Pod: ImagePullBackOff
- Events: `ErrImagePull` or `FailedPull`
- Logs: Image not available

**AI Diagnosis:**
```
Root Cause: Invalid or inaccessible container image
Explanation: Registry doesn't have image or auth failed
Fix: Verify image URL and registry credentials
kubectl command: kubectl describe pod... (see events)
Prevention: Use image pull secrets, scan registry
Confidence: 92%
```

### Scenario 3: Healthy Cluster

**Investigation finds:**
- All pods: Running
- No events: No warnings
- All deployments: Healthy

**AI Diagnosis:**
```
Root Cause: No issues detected
Explanation: Cluster appears to be healthy
Fix: No action needed
Prevention: Continue monitoring
Confidence: 100%
```

## Performance

- **Investigation time:** ~10-30 seconds (depends on cluster size)
- **LLM response time:** ~5-15 seconds (depends on model)
- **Total time:** ~15-45 seconds

## Security

✓ **No secret exposure:**
- API keys only read from environment
- Never logged or exposed in responses
- HTTPS communication with OpenRouter

✓ **Safe defaults:**
- Timeout prevents hanging requests
- Error handling prevents crashes
- Validation prevents malformed responses

## Next Steps

1. ✓ Kubernetes Investigation Layer
2. ✓ AI Reasoning Engine
3. → Connect frontend to diagnosis endpoint
4. → Add diagnosis history tracking
5. → Implement remediation (auto-fixes)

## Troubleshooting

### "OpenRouter API key not configured"
- Set `OPENROUTER_API_KEY` environment variable
- Get key from InsForge backend settings

### "Connection refused"
- Check internet connectivity
- Verify OpenRouter is accessible
- Check firewall rules

### "Timeout after 60s"
- OpenRouter service might be slow
- Large cluster investigation takes time
- Try again or increase timeout

### "kubectl is not installed"
- Investigation still works, returns "No issues from investigation"
- For full features, install kubectl
- Or deploy to Kubernetes cluster for testing
