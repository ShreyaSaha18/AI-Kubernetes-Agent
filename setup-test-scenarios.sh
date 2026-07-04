#!/bin/bash

echo "🧪 Setting up Kubernetes test scenarios..."
echo ""

# Clean up previous tests
echo "🧹 Cleaning up previous test resources..."
kubectl delete deployment crash-test image-fail healthy-app --ignore-not-found 2>/dev/null
kubectl delete pod crash-pod test-pod pending-test config-error --ignore-not-found 2>/dev/null
kubectl delete service test-service --ignore-not-found 2>/dev/null
echo "✓ Cleanup complete"
echo ""

# Wait a moment for cleanup
sleep 2

# Scenario 1: CrashLoopBackOff
echo "1️⃣  Creating CrashLoopBackOff scenario..."
kubectl run crash-test --image=busybox -- /bin/sh -c 'exit 1' 2>/dev/null
echo "   ✓ Pod that continuously crashes"
sleep 1

# Scenario 2: ImagePullBackOff
echo "2️⃣  Creating ImagePullBackOff scenario..."
kubectl create deployment image-fail --image=nonexistent-image:v999 --replicas=1 2>/dev/null
echo "   ✓ Deployment with non-existent image"
sleep 1

# Scenario 3: Pending
echo "3️⃣  Creating Pending pod scenario..."
kubectl run pending-test --image=nginx --requests=cpu=1000,memory=1000Gi 2>/dev/null
echo "   ✓ Pod that can't be scheduled (insufficient resources)"
sleep 1

# Scenario 4: Service Selector Mismatch
echo "4️⃣  Creating Service selector mismatch..."
kubectl create service clusterip test-service --tcp=80:8080 2>/dev/null
kubectl run test-pod --image=nginx --labels=app=wrong-app 2>/dev/null
echo "   ✓ Service with no matching endpoints"
sleep 1

# Scenario 5: Healthy App
echo "5️⃣  Creating healthy deployment..."
kubectl create deployment healthy-app --image=nginx --replicas=2 2>/dev/null
echo "   ✓ Healthy deployment running normally"
sleep 1

echo ""
echo "✅ All test scenarios ready!"
echo ""
echo "📊 Current cluster state:"
echo ""
kubectl get pods --all-namespaces -o wide
echo ""
echo "🚀 Next steps:"
echo "   1. Open http://localhost:3000"
echo "   2. Login to dashboard"
echo "   3. Click 'Investigate Cluster'"
echo "   4. Watch the beautiful progress display with status levels"
echo "   5. See AI diagnosis for each scenario"
echo ""
echo "🧹 To cleanup later, run:"
echo "   kubectl delete pods crash-test test-pod pending-test --ignore-not-found"
echo "   kubectl delete deployment crash-test image-fail healthy-app --ignore-not-found"
echo "   kubectl delete service test-service --ignore-not-found"
