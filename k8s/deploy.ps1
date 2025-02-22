# PowerShell script for deploying realnet to Kubernetes on Windows

# Create namespace if it doesn't exist
Write-Host "Creating namespace..."
kubectl apply -f base/namespace.yaml

# Apply storage configuration
Write-Host "Configuring storage..."
kubectl apply -f base/storage.yaml

# Deploy PostgreSQL
Write-Host "Deploying PostgreSQL..."
kubectl apply -f base/postgresql.yaml

# Deploy Mosquitto MQTT broker
Write-Host "Deploying Mosquitto MQTT broker..."
kubectl apply -f base/mosquitto.yaml

# Deploy realnet
Write-Host "Deploying realnet..."
kubectl apply -f base/realnet.yaml

Write-Host "Deployment complete!"

# Wait for pods to be ready
Write-Host "Waiting for pods to be ready..."
kubectl wait --namespace realnet --for=condition=ready pod --all --timeout=300s

# Get service status
Write-Host "`nService Status:"
kubectl get services -n realnet

# Get pod status
Write-Host "`nPod Status:"
kubectl get pods -n realnet
