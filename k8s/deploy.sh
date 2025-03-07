#!/bin/bash
set -e

# Parse command line arguments
CLEAR_DB=false
SKIP_INIT=false
SHUTDOWN=false
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--clear-db)
            CLEAR_DB=true
            shift
            ;;
        -s|--shutdown)
            SHUTDOWN=true
            shift
            ;;
        --skip-init)
            SKIP_INIT=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [-c|--clear-db] [--skip-init] [-s|--shutdown]"
            exit 1
            ;;
    esac
done

if [ "$SHUTDOWN" = true ]; then
    echo "Shutting down cluster..."
    # Delete all deployments and services but keep PVCs
    kubectl delete deployment -n realnet --all
    kubectl delete service -n realnet --all
    kubectl delete configmap -n realnet --all
    kubectl delete secret -n realnet --all
    kubectl delete ingress -n realnet --all
    echo "Cluster shutdown complete. Data volumes are preserved."
    exit 0
fi

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

# Clear database if requested
if [ "$CLEAR_DB" = true ]; then
    echo "Clearing database..."
    # Delete realnet and RBAC first
    kubectl delete -f k8s/base/realnet.yaml --ignore-not-found
    kubectl delete -f k8s/base/rbac.yaml --ignore-not-found
    # Delete existing PostgreSQL deployment and PVC
    kubectl delete -f k8s/base/postgresql.yaml --ignore-not-found
    kubectl delete pvc -n realnet postgresql-data --ignore-not-found
    # Wait for pods to be fully terminated
    kubectl wait --namespace realnet --for=delete pod -l app=realnet --timeout=60s 2>/dev/null || true
    kubectl wait --namespace realnet --for=delete pod -l app=postgresql --timeout=60s 2>/dev/null || true
    
    # Wait for PVC to be fully deleted
    echo "Waiting for PostgreSQL PVC to be deleted..."
    while kubectl get pvc -n realnet postgresql-data &>/dev/null; do
        sleep 2
    done

    # Clean up any leftover data
    echo "Cleaning up PostgreSQL data..."
    sudo rm -rf /var/lib/docker/volumes/*postgresql-data* || true
    sudo rm -rf /var/lib/rancher/k3s/storage/*postgresql-data* || true
    sudo rm -rf ~/.docker/desktop/docker-desktop-data/data/docker/volumes/*postgresql-data* || true
    echo "Database cleared"
fi

# Apply storage and wait for PVC
kubectl apply -f k8s/base/storage.yaml
echo "Waiting for PostgreSQL PVC to be created..."
while ! kubectl get pvc -n realnet postgresql-data &>/dev/null; do
    sleep 2
done

# Deploy PostgreSQL
kubectl apply -f k8s/base/postgresql.yaml
wait_for_pod realnet postgresql

# Deploy Mosquitto MQTT broker
kubectl apply -f k8s/base/mosquitto.yaml
wait_for_pod realnet mosquitto

# Deploy WordPress database
kubectl apply -f k8s/base/wordpress-db.yaml
wait_for_pod realnet wordpress-db

# Deploy WordPress
kubectl apply -f k8s/base/wordpress.yaml
wait_for_pod realnet wordpress

# Deploy RBAC configuration
echo "Deploying RBAC configuration..."
kubectl apply -f k8s/base/rbac.yaml

# Deploy Realnet
kubectl apply -f k8s/base/realnet.yaml
wait_for_pod realnet realnet

echo "Realnet cluster deployment complete!"

# Initialize realnet if not skipped
if [ "$SKIP_INIT" = false ]; then
    if [ "$CLEAR_DB" = true ]; then
        # Wait a bit for the database to be fully ready after clearing
        sleep 10
    fi

    echo "Initializing realnet..."
    kubectl exec -n realnet deployment/realnet -- realnet server initialize --name public --username admin --email admin@realnet.local --password admin --uri http://localhost:8080 --redirect_uri http://localhost:8080/callback --mobile_redirect_uri realnet://callback
else
    echo "Skipping initialization..."
fi

# Display service information
echo "Services are now accessible at:"
echo "PostgreSQL: localhost:5433"
echo "  - Database: realnet"
echo "  - Username: realnet"
echo "  - Password: realnet"
echo "MQTT Broker: localhost:1883"
echo "  - MQTT: localhost:1883"
echo "  - WebSockets: localhost:9001"
echo "WordPress: http://localhost:8081"
echo "  - Admin: http://localhost:8081/wp-admin"
echo "  - Username: admin"
echo "  - Password: admin"
echo "Realnet API: http://localhost:8080"

# Wait for LoadBalancer services to get external IPs
echo -n "Waiting for services to be ready..."
while ! kubectl get svc -n realnet postgresql -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' &>/dev/null && \
      ! kubectl get svc -n realnet postgresql -o jsonpath='{.status.loadBalancer.ingress[0].ip}' &>/dev/null; do
    echo -n "."
    sleep 2
done
echo " Done!"

# Show final service status
echo -e "\nService Status:"
kubectl get svc -n realnet
