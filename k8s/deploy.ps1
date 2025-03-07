# PowerShell script for deploying realnet to Kubernetes on Windows
param(
    [switch]$ClearDB,
    [switch]$SkipInit,
    [switch]$Shutdown
)

if ($Shutdown) {
    Write-Host "Shutting down cluster..."
    # Delete all deployments and services but keep PVCs
    kubectl delete deployment -n realnet --all
    kubectl delete service -n realnet --all
    kubectl delete configmap -n realnet --all
    kubectl delete secret -n realnet --all
    kubectl delete ingress -n realnet --all
    Write-Host "Cluster shutdown complete. Data volumes are preserved."
    exit 0
}

# Create namespace if it doesn't exist
Write-Host "Creating namespace..."
kubectl apply -f k8s/base/namespace.yaml

# Create WordPress secrets and config maps
Write-Host "Creating WordPress secrets and config maps..."
kubectl create secret generic wordpress-api-secret -n realnet `
    --from-literal=username=admin `
    --from-literal=password=admin `
    --from-literal=token=realnet-dev-jwt-secret-key-change-in-production `
    --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic wordpress-db-secret -n realnet `
    --from-literal=username=wordpress `
    --from-literal=password=wordpress `
    --dry-run=client -o yaml | kubectl apply -f -

# Create realnet plugin ConfigMap
Write-Host "Creating realnet plugin ConfigMap..."
mkdir -Force wordpress-plugin/templates | Out-Null
Copy-Item realnet-wordpress/realnet.php wordpress-plugin/ | Out-Null
Copy-Item realnet-wordpress/templates/*.php wordpress-plugin/templates/ | Out-Null
kubectl create configmap realnet-plugin -n realnet --from-file=wordpress-plugin --dry-run=client -o yaml | kubectl apply -f -
Remove-Item -Recurse -Force wordpress-plugin

# Apply storage configuration
Write-Host "Configuring storage..."
kubectl apply -f k8s/base/storage.yaml

# Clear database if requested
if ($ClearDB) {
    Write-Host "Clearing database..."
    # Delete realnet and RBAC first
    kubectl delete -f k8s/base/realnet.yaml --ignore-not-found
    kubectl delete -f k8s/base/rbac.yaml --ignore-not-found
    # Delete WordPress and its database
    kubectl delete -f k8s/base/wordpress.yaml --ignore-not-found
    kubectl delete -f k8s/base/wordpress-db.yaml --ignore-not-found
    # Delete existing PostgreSQL deployment and PVC
    kubectl delete -f k8s/base/postgresql.yaml --ignore-not-found
    kubectl delete pvc -n realnet postgresql-data --ignore-not-found
    kubectl delete pvc -n realnet wordpress-pvc --ignore-not-found
    kubectl delete pvc -n realnet wordpress-db-pvc --ignore-not-found
    # Wait for pods to be fully terminated
    try {
        kubectl wait --namespace realnet --for=delete pod -l app=realnet --timeout=60s 2>$null
    } catch {}
    try {
        kubectl wait --namespace realnet --for=delete pod -l app=postgresql --timeout=60s 2>$null
    } catch {}
    try {
        kubectl wait --namespace realnet --for=delete pod -l app=wordpress --timeout=60s 2>$null
    } catch {}
    try {
        kubectl wait --namespace realnet --for=delete pod -l app=wordpress-db --timeout=60s 2>$null
    } catch {}
    
    # Wait for PVC to be fully deleted
    Write-Host "Waiting for PostgreSQL PVC to be deleted..."
    while (kubectl get pvc -n realnet postgresql-data 2>$null) {
        Start-Sleep -Seconds 2
    }

    # Clean up any leftover data
    Write-Host "Cleaning up PostgreSQL data..."
    $dockerPath = "$env:USERPROFILE\.docker\desktop\docker-desktop-data\data\docker\volumes"
    if (Test-Path $dockerPath) {
        Get-ChildItem -Path $dockerPath -Filter "*postgresql-data*" -Directory | ForEach-Object {
            Write-Host "Removing $($_.FullName)..."
            Remove-Item -Path $_.FullName -Recurse -Force
        }
    }
    Write-Host "Database cleared"
}

# Apply storage and wait for PVC
kubectl apply -f k8s/base/storage.yaml
Write-Host "Waiting for PostgreSQL PVC to be created..."
while (-not (kubectl get pvc -n realnet postgresql-data 2>$null)) {
    Start-Sleep -Seconds 2
}

# Deploy PostgreSQL
Write-Host "Deploying PostgreSQL..."
kubectl apply -f k8s/base/postgresql.yaml

# Deploy Mosquitto MQTT broker
Write-Host "Deploying Mosquitto MQTT broker..."
kubectl apply -f k8s/base/mosquitto.yaml

# Deploy WordPress database
Write-Host "Deploying WordPress database..."
kubectl apply -f k8s/base/wordpress-db.yaml

# Deploy WordPress
Write-Host "Deploying WordPress..."
kubectl apply -f k8s/base/wordpress.yaml

# Deploy RBAC configuration
Write-Host "Deploying RBAC configuration..."
kubectl apply -f k8s/base/rbac.yaml

# Deploy realnet
Write-Host "Deploying realnet..."
kubectl apply -f k8s/base/realnet.yaml

Write-Host "Deployment complete!"

# Wait for PostgreSQL to be ready
Write-Host "Waiting for PostgreSQL to be ready..."
kubectl wait --namespace realnet --for=condition=ready pod -l app=postgresql --timeout=300s

# Wait for Mosquitto to be ready
Write-Host "Waiting for Mosquitto to be ready..."
kubectl wait --namespace realnet --for=condition=ready pod -l app=mosquitto --timeout=300s

# Wait for WordPress database to be ready
Write-Host "Waiting for WordPress database to be ready..."
kubectl wait --namespace realnet --for=condition=ready pod -l app=wordpress-db --timeout=300s

# Wait for WordPress to be ready
Write-Host "Waiting for WordPress to be ready..."
kubectl wait --namespace realnet --for=condition=ready pod -l app=wordpress --timeout=300s

# Wait for realnet to be ready
Write-Host "Waiting for realnet to be ready..."
kubectl wait --namespace realnet --for=condition=ready pod -l app=realnet --timeout=300s

# Get service status
Write-Host "`nService Status:"
kubectl get services -n realnet

# Get pod status
Write-Host "`nPod Status:"
kubectl get pods -n realnet

# Initialize realnet if not skipped
if (-not $SkipInit) {
    if ($ClearDB) {
        # Wait a bit for the database to be fully ready after clearing
        Start-Sleep -Seconds 10
    }

    Write-Host "`nInitializing realnet..."
    kubectl exec -n realnet deployment/realnet -- realnet server initialize --name public --username admin --email admin@realnet.local --password admin --uri http://localhost:8080 --redirect_uri http://localhost:8080/callback --mobile_redirect_uri realnet://callback
} else {
    Write-Host "`nSkipping initialization..."
}

# Display service information
Write-Host "`nServices are now accessible at:"
Write-Host "PostgreSQL: localhost:5433"
Write-Host "  - Database: realnet"
Write-Host "  - Username: realnet"
Write-Host "  - Password: realnet"
Write-Host "MQTT Broker: localhost:1883"
Write-Host "  - MQTT: localhost:1883"
Write-Host "  - WebSockets: localhost:9001"
Write-Host "WordPress: http://localhost:8081"
Write-Host "  - Admin: http://localhost:8081/wp-admin"
Write-Host "  - Username: admin"
Write-Host "  - Password: admin"
Write-Host "Realnet API: http://localhost:8080"

# Wait for LoadBalancer services to get external IPs
Write-Host -NoNewline "`nWaiting for services to be ready..."
while ($true) {
    $ip = $null
    try {
        $ip = kubectl get svc -n realnet postgresql -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>$null
        $hostname = kubectl get svc -n realnet postgresql -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>$null
        if ($ip -or $hostname) { break }
    } catch {}
    Write-Host -NoNewline "."
    Start-Sleep -Seconds 2
}
Write-Host " Done!"

# Show final service status
Write-Host "`nService Status:"
kubectl get svc -n realnet
