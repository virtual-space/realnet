#!/bin/bash
set -e

# Function to wait for a pod to be ready
wait_for_pod() {
    local namespace=$1
    local label=$2
    local timeout=${3:-300}  # Default timeout 5 minutes
    
    echo "Waiting for pod with label $label in namespace $namespace..."
    
    local start_time=$(date +%s)
    while true; do
        if [ $(($(date +%s) - start_time)) -gt $timeout ]; then
            echo "Timeout waiting for pod $label"
            return 1
        fi
        
        if kubectl -n $namespace get pods -l app=$label -o jsonpath='{.items[0].status.phase}' | grep -q "Running"; then
            if kubectl -n $namespace get pods -l app=$label -o jsonpath='{.items[0].status.containerStatuses[0].ready}' | grep -q "true"; then
                echo "Pod $label is ready"
                return 0
            fi
        fi
        
        sleep 5
    done
}

# Create namespace
kubectl apply -f k8s/base/namespace.yaml

# Apply storage configuration
kubectl apply -f k8s/base/storage.yaml

# Deploy PostgreSQL
kubectl apply -f k8s/base/postgresql.yaml
wait_for_pod realnet postgresql

# Deploy Mosquitto MQTT broker
kubectl apply -f k8s/base/mosquitto.yaml
wait_for_pod realnet mosquitto

# Deploy Realnet
kubectl apply -f k8s/base/realnet.yaml
wait_for_pod realnet realnet

echo "Realnet cluster deployment complete!"
echo "PostgreSQL: postgresql.realnet.svc.cluster.local:5432"
echo "MQTT Broker: mosquitto.realnet.svc.cluster.local:1883"
echo "Realnet API: realnet.realnet.svc.cluster.local:8080"
