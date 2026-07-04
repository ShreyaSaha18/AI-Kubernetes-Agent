# Kubernetes Investigation Layer

## Overview

The Kubernetes Investigation Layer is a evidence-gathering system that behaves like a **junior DevOps engineer** collecting debugging information before AI reasoning begins.

It does NOT implement AI reasoning, only evidence collection.

## Architecture

```
FastAPI Endpoint (/investigate)
    ↓
Investigation Service (Orchestrator)
    ├── Pod Inspector
    ├── Logs Collector
    ├── Events Analyzer
    ├── Deployment Inspector
    └── Network Inspector
    ↓
Kubectl Executor (subprocess wrapper)
    ↓
Structured JSON Response
```

## Components

### 1. Kubectl Executor (`kubernetes/kubectl_executor.py`)

Safe wrapper for kubectl commands.

**Features:**
- Subprocess execution with timeout (30s)
- Error handling and logging
- Structured output format
- Commands supported:
  - `kubectl get pods -A`
  - `kubectl get events -A`
  - `kubectl logs <pod>`
  - `kubectl describe deployment <name>`
  - `kubectl get services -A`
  - `kubectl get deployments -A`

**Example:**
```python
result = KubectlExecutor.execute(["kubectl", "get", "pods", "-A", "-o", "json"])
```

### 2. Pod Inspector (`kubernetes/pod_inspector.py`)

Checks pod status and detects unhealthy pods.

**Detects:**
- CrashLoopBackOff
- ImagePullBackOff
- Pending
- Error
- OOMKilled
- ContainerCreating (stuck)
- Unknown
- Terminating

**Output:**
```json
{
  "healthy": false,
  "total_pods": 15,
  "problematic_pods": [
    {
      "name": "payment-service",
      "namespace": "default",
      "status": "CrashLoopBackOff",
      "container": "payment-app"
    }
  ]
}
```

### 3. Logs Collector (`kubernetes/logs_collector.py`)

Fetches logs from failed pods.

**Features:**
- Collects logs only from problematic pods
- Filters for error keywords
- Limits output (50 lines max)
- Error keywords:
  - error, exception, failed, fatal, panic, crash
  - connection refused, timeout, cannot find, not found
  - missing, permission denied, unauthorized, invalid

**Output:**
```json
{
  "total_logs_collected": 2,
  "logs": [
    {
      "pod": "payment-service",
      "namespace": "default",
      "status": "CrashLoopBackOff",
      "logs": [
        "[ERROR] Connection refused to database",
        "[ERROR] Failed to start payment service"
      ]
    }
  ]
}
```

### 4. Events Analyzer (`kubernetes/events_analyzer.py`)

Analyzes Kubernetes events for issues.

**Detects:**
- FailedScheduling
- BackOff
- FailedMount
- FailedPull
- ErrImagePull
- Unhealthy
- FailedCreatePodSandbox
- FailedAttachVolume
- FailedDetachVolume
- FailedDelete
- NodeNotReady
- Evicted

**Output:**
```json
{
  "total_events": 50,
  "issues_found": [
    {
      "reason": "FailedScheduling",
      "message": "0/3 nodes are available",
      "type": "Warning",
      "object_kind": "Pod",
      "object_name": "auth-service",
      "namespace": "default",
      "count": 5
    }
  ]
}
```

### 5. Deployment Inspector (`kubernetes/deployment_inspector.py`)

Inspects deployments for rollout issues.

**Checks:**
- Available vs desired replicas
- Unavailable replicas
- Rollout conditions
- Ready replicas

**Output:**
```json
{
  "total_deployments": 8,
  "unhealthy_deployments": [
    {
      "name": "payment-service",
      "namespace": "default",
      "desired_replicas": 3,
      "ready_replicas": 1,
      "available_replicas": 1,
      "updated_replicas": 3,
      "conditions": [
        {
          "type": "Progressing",
          "status": "False",
          "reason": "ProgressDeadlineExceeded"
        }
      ]
    }
  ]
}
```

### 6. Network Inspector (`kubernetes/network_inspector.py`)

Inspects services and networking.

**Checks:**
- Service selectors
- Endpoint assignments
- LoadBalancer status

**Output:**
```json
{
  "total_services": 10,
  "services_with_issues": [
    {
      "name": "api-service",
      "namespace": "default",
      "type": "LoadBalancer",
      "selector": {},
      "issue": "No selector defined"
    }
  ]
}
```

### 7. Investigation Service (`services/investigation_service.py`)

Orchestrates all inspectors and combines results.

**Flow:**
1. Pod Inspector
2. Logs Collector
3. Events Analyzer
4. Deployment Inspector
5. Network Inspector

**Returns:**
```json
{
  "status": "success",
  "timestamp": "2026-07-04T12:34:56",
  "investigation": {
    "pods": {...},
    "logs": {...},
    "events": {...},
    "deployments": {...},
    "network": {...}
  }
}
```

## API Endpoints

### POST /api/investigate

Run complete Kubernetes investigation.

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
  }
}
```

### GET /api/investigate/status

Check investigation layer health.

**Response:**
```json
{
  "status": "ready",
  "service": "kubernetes-investigation-layer"
}
```

## Usage Examples

### Python

```python
from services.investigation_service import InvestigationService

result = await InvestigationService.run_investigation()
print(result)
```

### cURL

```bash
curl -X POST http://localhost:8000/api/investigate
```

### Python Requests

```python
import requests

response = requests.post("http://localhost:8000/api/investigate")
investigation = response.json()
```

## Error Handling

All components handle errors gracefully:
- Missing kubectl → Returns error message
- Connection timeouts → 30-second timeout with error
- Parse errors → Returns error in response
- Command failures → Captures stderr

Example error response:
```json
{
  "status": "error",
  "timestamp": "2026-07-04T12:34:56Z",
  "error": "kubectl is not installed or not in PATH",
  "investigation": null
}
```

## Requirements

- kubectl installed and in PATH
- Access to Kubernetes cluster
- Proper kubeconfig configuration
- Python 3.12+

## Logging

All components use `loguru` for structured logging.

Logs show:
- Operation start/completion
- Error details
- Investigation statistics

Example:
```
INFO | kubernetes.pod_inspector:inspect:45 - Pod inspection complete: 2 issues found
```

## Next Steps

1. ✓ Kubernetes Investigation Layer complete
2. → Implement AI reasoning with OpenRouter
3. → Add root cause analysis
4. → Generate fix recommendations
5. → Connect frontend to investigation endpoint

## Notes

- **No Kubernetes Python SDK** - Uses kubectl subprocess only
- **No AI reasoning** - Only evidence collection
- **Modular design** - Each inspector is independent
- **Async ready** - Service supports async operations
- **Error resilient** - Graceful degradation on failures
- **Production-ready** - Proper logging and error handling
