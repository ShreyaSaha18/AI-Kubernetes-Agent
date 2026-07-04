# Kubernetes Test Scenarios

Create intentional Kubernetes failures to test the AI Agent's diagnostic capabilities.

---

## Scenario 1: CrashLoopBackOff (Missing Environment Variable)

```bash
# Create a deployment that crashes immediately
kubectl create deployment crash-test --image=busybox --replicas=1

# Force it to fail by running a command that exits
kubectl set env deployment/crash-test FAIL_START=true

# Add a command that exits with error
kubectl patch deployment crash-test -p '{"spec":{"template":{"spec":{"containers":[{"name":"busybox","command":["/bin/sh","-c","exit 1"]}]}}}}'

# Verify it's crashing
kubectl get pods
kubectl logs -l app=crash-test --tail=20
```

**Expected Diagnosis:**
- Root Cause: Pod in CrashLoopBackOff
- Explanation: Container exits immediately on startup
- Fix: Check logs, fix startup command, redeploy

---

## Scenario 2: ImagePullBackOff (Invalid Image)

```bash
# Create deployment with non-existent image
kubectl create deployment image-fail --image=nonexistent-image:v999 --replicas=1

# Verify it's stuck pulling
kubectl get pods
kubectl describe pod -l app=image-fail
```

**Expected Diagnosis:**
- Root Cause: Image pull failed
- Explanation: Registry doesn't have the specified image
- Fix: Verify image name and tag, check registry credentials

---

## Scenario 3: OOMKilled (Out of Memory)

```bash
# Create pod with very low memory limit
kubectl run oom-test \
  --image=busybox \
  --limits=memory=1Mi \
  --requests=memory=1Mi \
  -- /bin/sh -c 'stress --vm 1 --vm-bytes 10M --verbose'
```

**Expected Diagnosis:**
- Root Cause: Container killed due to memory limit
- Explanation: Application exceeded memory limit
- Fix: Increase memory limit or optimize app

---

## Scenario 4: Service Selector Mismatch

```bash
# Create a service
kubectl create service clusterip test-service --tcp=80:8080

# Create a pod with different labels
kubectl run test-pod --image=nginx --labels=wrong-label=true

# Verify no endpoints
kubectl get endpoints test-service
kubectl describe svc test-service
```

**Expected Diagnosis:**
- Root Cause: Service has no matching pods
- Explanation: Service selector doesn't match any pod labels
- Fix: Update pod labels or service selector

---

## Scenario 5: Pending Pods (Insufficient Resources)

```bash
# Create pod with huge resource requirements
kubectl run pending-test \
  --image=nginx \
  --requests=cpu=1000,memory=1000Gi
```

**Expected Diagnosis:**
- Root Cause: Pod pending, unable to schedule
- Explanation: Insufficient cluster resources
- Fix: Add nodes or reduce resource requirements

---

## Scenario 6: CreateContainerConfigError (Invalid Environment)

```bash
# Create pod with invalid environment variable (bad reference)
kubectl run config-error \
  --image=nginx \
  --env=VALID_VAR=value \
  --env=INVALID_VAR= \
  -- /bin/sh -c 'env'
```

**Expected Diagnosis:**
- Root Cause: Container config error
- Explanation: Invalid environment or configuration
- Fix: Verify pod spec and environment variables

---

## Scenario 7: Healthy Cluster (No Issues)

```bash
# Create a healthy deployment
kubectl create deployment healthy-app --image=nginx --replicas=3

# Verify it's running
kubectl get deployment healthy-app
kubectl get pods -l app=healthy-app
```

**Expected Diagnosis:**
- Root Cause: No issues detected
- Explanation: Cluster appears healthy
- Fix: No action needed
- Confidence: 100%

---

## Complete Test Script

Run all scenarios at once:

```bash
#!/bin/bash

echo "🧪 Setting up Kubernetes test scenarios..."

# Clean up previous tests
kubectl delete deployment crash-test image-fail --ignore-not-found
kubectl delete pod oom-test pending-test config-error --ignore-not-found
kubectl delete service test-service --ignore-not-found

# Scenario 1: CrashLoopBackOff
echo "1️⃣  Creating CrashLoopBackOff scenario..."
kubectl run crash-test --image=busybox -- /bin/sh -c 'exit 1'

# Scenario 2: ImagePullBackOff
echo "2️⃣  Creating ImagePullBackOff scenario..."
kubectl create deployment image-fail --image=nonexistent-image:v999 --replicas=1

# Scenario 3: OOMKilled (optional, needs stress tool)
echo "3️⃣  Creating OOMKilled scenario..."
# kubectl run oom-test --image=progrium/stress --limits=memory=1Mi -- stress --vm 1 --vm-bytes 10M

# Scenario 4: Service Mismatch
echo "4️⃣  Creating Service selector mismatch..."
kubectl create service clusterip test-service --tcp=80:8080
kubectl run test-pod --image=nginx --labels=app=wrong-app

# Scenario 5: Pending
echo "5️⃣  Creating Pending pod scenario..."
kubectl run pending-test --image=nginx --requests=cpu=1000,memory=1000Gi

# Scenario 6: Healthy
echo "6️⃣  Creating healthy deployment..."
kubectl create deployment healthy-app --image=nginx --replicas=2

echo "✅ Test scenarios ready!"
echo ""
echo "📊 Current cluster state:"
kubectl get all --all-namespaces
```

---

## Testing Workflow

### Step 1: Set up test scenarios
```bash
bash test_scenarios.sh
```

### Step 2: Open AI Kubernetes Agent
```
http://localhost:3000
```

### Step 3: Investigate cluster
- Click "Investigate Cluster"
- Watch progress updates
- Verify diagnosis matches expected result

### Step 4: Check different scenarios
- Multiple scenarios exist simultaneously
- Each investigation reveals different issues
- Compare diagnoses with expected results

---

## Cleanup

Remove all test scenarios:

```bash
# Delete all test resources
kubectl delete pods crash-test test-pod oom-test pending-test config-error --ignore-not-found
kubectl delete deployment image-fail healthy-app --ignore-not-found
kubectl delete service test-service --ignore-not-found

# Verify cleanup
kubectl get all
```

---

## Verification Checklist

✅ **CrashLoopBackOff** - Pod status shows restart loop  
✅ **ImagePullBackOff** - Pod stuck in pulling state  
✅ **OOMKilled** - Container killed due to memory  
✅ **Service Mismatch** - Service with 0 endpoints  
✅ **Pending** - Pod can't be scheduled  
✅ **Healthy** - All pods running, no issues  

---

## Expected AI Diagnoses

| Scenario | Root Cause | Confidence | Fix |
|----------|-----------|-----------|-----|
| CrashLoopBackOff | Pod keeps crashing | 95%+ | Check logs, fix startup |
| ImagePullBackOff | Image not found | 98%+ | Verify image name/tag |
| OOMKilled | Memory exceeded | 96%+ | Increase limits |
| Service Mismatch | No endpoints | 94%+ | Fix labels/selector |
| Pending | Can't schedule | 92%+ | Add resources |
| Healthy | No issues | 100% | No action |

---

## Notes

- Test scenarios persist until deleted
- Each investigation is independent
- AI should identify different root causes
- Confidence scores reflect diagnosis certainty
- Use for validation before production use
