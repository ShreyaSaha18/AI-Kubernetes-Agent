# Integration, Testing & Deployment

## End-to-End Flow

### Complete User Journey

```
1. User visits http://localhost:3000
        ↓ (redirects if not logged in)
2. Login/Signup
        ↓
3. Dashboard loads
        ↓
4. Clusters loaded from kubeconfig
        ↓
5. User selects cluster (dropdown)
        ↓
6. Click "Investigate Cluster"
        ↓
7. Backend switches to selected cluster
        ↓
8. Kubernetes investigation starts
   - Check Pods
   - Read Logs
   - Analyze Events
   - Inspect Deployments
   - Check Networking
        ↓
9. AI reasoning triggered
        ↓
10. Root cause generated
        ↓
11. Suggested fix returned
        ↓
12. Investigation saved to database
        ↓
13. UI displays diagnosis
        ↓
14. History updates
```

## Cluster Selection

### Backend API

#### GET /api/clusters/list

Get all clusters from kubeconfig.

**Response:**
```json
{
  "status": "success",
  "clusters": [
    {
      "name": "minikube",
      "server": "https://127.0.0.1:32768",
      "certificate_authority": "/home/user/.minikube/ca.crt"
    },
    {
      "name": "docker-desktop",
      "server": "https://127.0.0.1:6443",
      "certificate_authority": "/home/user/.docker/ca.crt"
    }
  ]
}
```

#### POST /api/clusters/switch

Switch to a different cluster.

**Request:**
```
POST /api/clusters/switch?cluster_name=docker-desktop
```

**Response:**
```json
{
  "status": "success",
  "message": "Switched to context: docker-desktop"
}
```

### Frontend

**Cluster Selector:**
- Dropdown in header
- Shows all available clusters
- Click to switch cluster
- Investigation runs against selected cluster

## Error Handling

### Scenario 1: No kubeconfig

**Error Message:**
```
No kubeconfig found. Check KUBECONFIG env var or ~/.kube/config
```

**Fix:**
- Set KUBECONFIG environment variable
- Or create ~/.kube/config
- Copy kubeconfig from cluster admin

### Scenario 2: kubectl not found

**Error Message:**
```
kubectl is not installed or not in PATH
```

**Fix:**
- Install kubectl
- Add to system PATH
- Verify: `kubectl version`

### Scenario 3: No cluster access

**Error Message:**
```
Unable to connect to Kubernetes cluster
```

**Possible causes:**
- Cluster is down
- Network unreachable
- Invalid kubeconfig
- Insufficient permissions

**Fix:**
- Verify cluster is running
- Check network connectivity
- Update kubeconfig
- Run: `kubectl auth can-i list pods`

### Scenario 4: OpenRouter API error

**Error Message:**
```
OpenRouter API error: 401 Unauthorized
```

**Fix:**
- Verify OPENROUTER_API_KEY is set
- Check API key is valid
- Verify API key has permission

### Scenario 5: No unhealthy resources

**Response:**
```json
{
  "root_cause": "No issues detected",
  "explanation": "Cluster appears to be healthy",
  "fix": "No action needed",
  "confidence": 100
}
```

## Testing Real Kubernetes Failures

### Test Scenario 1: CrashLoopBackOff

**Setup:**
```bash
# Create deployment with missing env var
kubectl create deployment crash-test --image=nginx
kubectl set env deployment/crash-test MISSING_VAR=true

# Create pod that immediately crashes
kubectl run crash-pod --image=busybox -- /bin/sh -c 'exit 1'
```

**Expected Diagnosis:**
```
Root Cause: Pod in CrashLoopBackOff state
Explanation: Container is crashing due to missing configuration or startup failure
Fix: Check logs to identify startup issue, fix configuration, redeploy
kubectl command: kubectl logs <pod-name> to view error details
Confidence: 90%+
```

### Test Scenario 2: ImagePullBackOff

**Setup:**
```bash
# Deploy with invalid image
kubectl create deployment image-test --image=nonexistent-image:latest
```

**Expected Diagnosis:**
```
Root Cause: Image pull failed
Explanation: Registry does not have the specified image or access is denied
Fix: Verify image name and tag, check registry credentials
kubectl command: kubectl describe pod <pod-name> for pull error details
Confidence: 95%+
```

### Test Scenario 3: OOMKilled

**Setup:**
```bash
# Deploy with low memory limit
kubectl run oom-test --image=busybox --limits=memory=1Mi
```

**Expected Diagnosis:**
```
Root Cause: Container killed due to memory limit
Explanation: Application consumed more memory than the limit
Fix: Increase memory limit or optimize application memory usage
kubectl command: kubectl edit deployment oom-test
Confidence: 92%+
```

### Test Scenario 4: Service Selector Mismatch

**Setup:**
```bash
# Create service with non-matching selector
kubectl create service clusterip svc-test --tcp=80:8080
kubectl label pod <pod-name> app=wrong-label
```

**Expected Diagnosis:**
```
Root Cause: Service has no matching pods
Explanation: Service selector does not match any pod labels
Fix: Update service selector or pod labels to match
kubectl command: kubectl label pod <pod-name> app=service-test
Confidence: 94%+
```

## Integration Testing Checklist

### Frontend
- [ ] Login page works
- [ ] Signup page works
- [ ] Cluster dropdown loads clusters
- [ ] Cluster selection works
- [ ] Investigation button triggers investigation
- [ ] Progress updates in real-time
- [ ] Diagnosis displays correctly
- [ ] History shows previous investigations
- [ ] Logout clears session

### Backend
- [ ] Auth endpoints working
- [ ] Cluster listing working
- [ ] Cluster switching working
- [ ] Investigation API working
- [ ] Database saves investigations
- [ ] History retrieval working
- [ ] Error handling working
- [ ] Logging working

### Kubernetes Integration
- [ ] kubectl found
- [ ] Kubeconfig readable
- [ ] Can connect to cluster
- [ ] Can list pods
- [ ] Can read logs
- [ ] Can read events
- [ ] Can describe deployments
- [ ] Can list services

### AI Integration
- [ ] OpenRouter API key valid
- [ ] Can connect to OpenRouter
- [ ] AI generates diagnosis
- [ ] Root cause identified
- [ ] Confidence score calculated

## Testing Script

### Quick Integration Test

**1. Start services:**
```bash
cd ai-kubernetes-agent
docker compose up --build
```

**2. Create test failure:**
```bash
kubectl create deployment test-crash --image=busybox -- /bin/sh -c 'exit 1'
```

**3. Open frontend:**
```
http://localhost:3000
```

**4. Login:**
- Email: test@example.com
- Password: password123

**5. Select cluster:**
- Choose your cluster from dropdown

**6. Investigate:**
- Click "Investigate Cluster"
- Watch progress
- See diagnosis

**7. Verify:**
- Root cause shown
- Suggested fix shown
- Confidence score shown
- Investigation saved

## Deployment

### Local Deployment (Current)

```bash
docker compose up --build
```

Access:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Health: http://localhost:8000/health

### Production Deployment

**Requirements:**
- Kubernetes cluster
- InsForge backend (for database)
- OpenRouter API key
- Docker registry (for images)

**Steps:**
1. Build images
2. Push to registry
3. Update Kubernetes manifests
4. Deploy to cluster
5. Configure DNS
6. Set environment variables
7. Enable HTTPS
8. Monitor logs

**Example Kubernetes deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-kubernetes-agent
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: backend
        image: registry/ai-kubernetes-agent:latest
        env:
        - name: OPENROUTER_API_KEY
          valueFrom:
            secretKeyRef:
              name: openrouter
              key: api-key
      - name: frontend
        image: registry/ai-kubernetes-agent-frontend:latest
```

## Monitoring

### Logs

**Backend logs:**
```bash
docker compose logs -f backend
```

**Frontend logs:**
```bash
docker compose logs -f frontend
```

**Combined logs:**
```bash
docker compose logs -f
```

### Health Checks

**Backend health:**
```bash
curl http://localhost:8000/health
```

**Frontend health:**
```bash
curl http://localhost:3000
```

### Metrics

Monitor:
- Investigation success rate
- AI confidence scores
- API response times
- Error frequency
- User adoption

## Performance

### Typical Investigation Time

- Pod inspection: 1-2s
- Log collection: 2-3s
- Event analysis: 1-2s
- Deployment inspection: 1s
- Network inspection: 1s
- AI reasoning: 5-15s
- **Total: 15-45 seconds**

### Optimization Tips

1. **Cache kubeconfig** - Load once, reuse
2. **Parallel inspection** - Run checks simultaneously
3. **Limit log lines** - Don't fetch entire logs
4. **Use smaller model** - Faster but less accurate
5. **Connection pooling** - Reuse HTTP connections

## Troubleshooting

### Investigation takes too long

**Possible causes:**
- Large cluster with many resources
- Slow network connection
- OpenRouter service slow

**Solutions:**
- Reduce log line limit
- Use faster model
- Check network speed

### AI returns generic diagnosis

**Possible causes:**
- OpenRouter model outdated
- Poor cluster data quality
- Missing error keywords in logs

**Solutions:**
- Use better model (gpt-4)
- Improve log filtering
- Add more error keywords

### kubectl not working

**Possible causes:**
- kubectl not installed
- Not in PATH
- No kubeconfig

**Solutions:**
```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Verify
kubectl version
```

## Next Steps

- [ ] Deploy to Kubernetes cluster
- [ ] Set up monitoring/alerting
- [ ] Add authentication (OAuth)
- [ ] Add investigation scheduling
- [ ] Add remediation automation
- [ ] Add Slack integration
- [ ] Add metrics dashboard
