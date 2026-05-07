#!/bin/bash

# OPTIMIZED DEPLOYMENT SCRIPT - DEDAN WORLDMINE
# High-performance, scalable, secure deployment

set -euo pipefail

# Configuration
PROJECT_NAME="worldmine"
DEPLOYMENT_ENV="${DEPLOYMENT_ENV:-production}"
REGION="${DEPLOYMENT_REGION:-us-west-2}"
CLUSTER_NAME="${CLUSTER_NAME:-worldmine-cluster}"
NAMESPACE="${NAMESPACE:-worldmine}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

log_info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if required tools are installed
    for tool in kubectl helm docker aws; do
        if ! command -v $tool &> /dev/null; then
            log_error "$tool is not installed"
            exit 1
        fi
    done
    
    # Check if kubectl is configured
    if ! kubectl cluster-info &> /dev/null; then
        log_error "kubectl is not configured"
        exit 1
    fi
    
    # Check if AWS credentials are configured
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials are not configured"
        exit 1
    fi
    
    log "Prerequisites check passed"
}

# Create namespace
create_namespace() {
    log "Creating namespace: $NAMESPACE"
    
    if kubectl get namespace $NAMESPACE &> /dev/null; then
        log_warning "Namespace $NAMESPACE already exists"
    else
        kubectl create namespace $NAMESPACE
        log "Namespace $NAMESPACE created successfully"
    fi
}

# Deploy optimized database
deploy_database() {
    log "Deploying optimized database..."
    
    # Create database secret
    kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: database-secret
  namespace: $NAMESPACE
type: Opaque
data:
  POSTGRES_DB: $(echo -n "$DB_NAME" | base64)
  POSTGRES_USER: $(echo -n "$DB_USER" | base64)
  POSTGRES_PASSWORD: $(echo -n "$DB_PASSWORD" | base64)
EOF
    
    # Deploy PostgreSQL with optimizations
    kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: $NAMESPACE
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_DB
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: POSTGRES_DB
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: POSTGRES_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: POSTGRES_PASSWORD
        - name: POSTGRES_INITDB_ARGS
          value: "--encoding=UTF-8"
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - \$(POSTGRES_USER)
            - -d
            - \$(POSTGRES_DB)
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - \$(POSTGRES_USER)
            - -d
            - \$(POSTGRES_DB)
          initialDelaySeconds: 5
          periodSeconds: 5
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 100Gi
      storageClassName: gp2
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: $NAMESPACE
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  type: ClusterIP
EOF
    
    log "Database deployed successfully"
}

# Deploy Redis cache
deploy_redis() {
    log "Deploying Redis cache..."
    
    kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: $NAMESPACE
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  namespace: $NAMESPACE
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
  type: ClusterIP
EOF
    
    log "Redis cache deployed successfully"
}

# Deploy optimized application
deploy_application() {
    log "Deploying optimized application..."
    
    # Create application secret
    kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: $NAMESPACE
type: Opaque
data:
  REDIS_URL: $(echo -n "redis://redis-service:6379" | base64)
  DATABASE_URL: $(echo -n "postgresql://\$POSTGRES_USER:\$POSTGRES_PASSWORD@postgres-service:5432/\$POSTGRES_DB" | base64)
  JWT_SECRET_KEY: $(echo -n "$JWT_SECRET_KEY" | base64)
  API_KEY: $(echo -n "$API_KEY" | base64)
EOF
    
    # Deploy optimized application
    kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: worldmine-app
  namespace: $NAMESPACE
  labels:
    app: worldmine-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: worldmine-app
  template:
    metadata:
      labels:
        app: worldmine-app
    spec:
      containers:
      - name: worldmine-app
        image: worldmine/app:2035.0.0-optimized
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: REDIS_URL
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: DATABASE_URL
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: JWT_SECRET_KEY
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: API_KEY
        - name: WORKERS
          value: "4"
        - name: LOG_LEVEL
          value: "INFO"
        - name: ENVIRONMENT
          value: "$DEPLOYMENT_ENV"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 15"]
---
apiVersion: v1
kind: Service
metadata:
  name: worldmine-service
  namespace: $NAMESPACE
  labels:
    app: worldmine-app
spec:
  selector:
    app: worldmine-app
  ports:
  - name: http
    port: 80
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: worldmine-ingress
  namespace: $NAMESPACE
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  tls:
  - hosts:
    - worldmine.com
    secretName: worldmine-tls
  rules:
  - host: worldmine.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: worldmine-service
            port:
              number: 80
EOF
    
    log "Application deployed successfully"
}

# Deploy monitoring
deploy_monitoring() {
    log "Deploying monitoring stack..."
    
    # Deploy Prometheus
    kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: $NAMESPACE
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: prometheus-config
          mountPath: /etc/prometheus
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
      volumes:
      - name: prometheus-config
        configMap:
          name: prometheus-config
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: $NAMESPACE
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
    - job_name: 'worldmine'
      static_configs:
      - targets: ['worldmine-service:80']
      metrics_path: /metrics
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus-service
  namespace: $NAMESPACE
spec:
  selector:
    app: prometheus
  ports:
  - port: 9090
    targetPort: 9090
  type: ClusterIP
EOF
    
    # Deploy Grafana
    kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: $NAMESPACE
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:latest
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          value: "admin123"
        resources:
          requests:
            memory: "256Mi"
            cpu: "125m"
          limits:
            memory: "512Mi"
            cpu: "250m"
---
apiVersion: v1
kind: Service
metadata:
  name: grafana-service
  namespace: $NAMESPACE
spec:
  selector:
    app: grafana
  ports:
  - port: 3000
    targetPort: 3000
  type: LoadBalancer
EOF
    
    log "Monitoring stack deployed successfully"
}

# Configure auto-scaling
configure_autoscaling() {
    log "Configuring auto-scaling..."
    
    kubectl apply -f - <<EOF
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: worldmine-hpa
  namespace: $NAMESPACE
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: worldmine-app
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
      selectPolicy: Max
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: worldmine-pdb
  namespace: $NAMESPACE
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: worldmine-app
EOF
    
    log "Auto-scaling configured successfully"
}

# Configure network policies
configure_network_policies() {
    log "Configuring network policies..."
    
    kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: worldmine-netpol
  namespace: $NAMESPACE
spec:
  podSelector:
    matchLabels:
      app: worldmine-app
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: $NAMESPACE
    ports:
    - protocol: TCP
      port: 5432
    - protocol: TCP
      port: 6379
    - to: []
      ports:
    - protocol: TCP
      port: 443
    - protocol: TCP
      port: 80
EOF
    
    log "Network policies configured successfully"
}

# Deploy security configurations
deploy_security() {
    log "Deploying security configurations..."
    
    # Create security context
    kubectl apply -f - <<EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: worldmine-sa
  namespace: $NAMESPACE
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: worldmine-role
  namespace: $NAMESPACE
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: worldmine-rolebinding
  namespace: $NAMESPACE
subjects:
- kind: ServiceAccount
  name: worldmine-sa
  namespace: $NAMESPACE
roleRef:
  kind: Role
  name: worldmine-role
  apiGroup: rbac.authorization.k8s.io
EOF
    
    log "Security configurations deployed successfully"
}

# Health check
health_check() {
    log "Performing health checks..."
    
    # Check pod status
    kubectl get pods -n $NAMESPACE
    
    # Check services
    kubectl get services -n $NAMESPACE
    
    # Check ingress
    kubectl get ingress -n $NAMESPACE
    
    # Test application endpoint
    if kubectl get ingress worldmine-ingress -n $NAMESPACE &> /dev/null; then
        INGRESS_URL=$(kubectl get ingress worldmine-ingress -n $NAMESPACE -o jsonpath='{.spec.rules[0].host}')
        log "Testing application at https://$INGRESS_URL/health"
        
        if curl -f -s "https://$INGRESS_URL/health" > /dev/null; then
            log "Application health check passed"
        else
            log_error "Application health check failed"
        fi
    fi
}

# Performance optimization
optimize_performance() {
    log "Optimizing performance..."
    
    # Set resource limits and requests
    kubectl patch deployment worldmine-app -n $NAMESPACE -p '{"spec":{"template":{"spec":{"containers":[{"name":"worldmine-app","resources":{"requests":{"memory":"1Gi","cpu":"500m"},"limits":{"memory":"4Gi","cpu":"2000m"}}}]}}}'
    
    # Enable horizontal pod autoscaler
    kubectl autoscale deployment worldmine-app -n $NAMESPACE --cpu-percent=70 --min=1 --max=10
    
    # Configure pod anti-affinity
    kubectl patch deployment worldmine-app -n $NAMESPACE -p '{"spec":{"template":{"spec":{"affinity":{"podAntiAffinity":{"requiredDuringSchedulingIgnoredDuringExecution":[{"labelSelector":{"matchLabels":{"app":"worldmine-app"}},"topologyKey":"kubernetes.io/hostname"}]}}}}}'
    
    log "Performance optimization completed"
}

# Cleanup old resources
cleanup() {
    log "Cleaning up old resources..."
    
    # Remove old pods
    kubectl delete pods -n $NAMESPACE --field-selector=status.phase=Succeeded --ignore-not-found=true
    kubectl delete pods -n $NAMESPACE --field-selector=status.phase=Failed --ignore-not-found=true
    
    # Clean up old configmaps
    kubectl delete configmaps -n $NAMESPACE --field-selector=metadata.creationTimestamp<$(date -d '7 days ago' --iso-8601) --ignore-not-found=true
    
    log "Cleanup completed"
}

# Main deployment function
main() {
    log "Starting optimized deployment of DEDAN WORLDMINE..."
    
    # Check prerequisites
    check_prerequisites
    
    # Create namespace
    create_namespace
    
    # Deploy infrastructure
    deploy_database
    deploy_redis
    
    # Deploy application
    deploy_application
    
    # Deploy monitoring
    deploy_monitoring
    
    # Configure auto-scaling
    configure_autoscaling
    
    # Configure network policies
    configure_network_policies
    
    # Deploy security configurations
    deploy_security
    
    # Optimize performance
    optimize_performance
    
    # Perform health check
    health_check
    
    # Cleanup old resources
    cleanup
    
    log "Optimized deployment completed successfully!"
    log "Application should be available at: https://worldmine.com"
    log "Grafana dashboard: https://$(kubectl get service grafana-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
    log "Prometheus metrics: https://$(kubectl get service prometheus-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}'):9090"
}

# Handle script arguments
case "${1:-}" in
    "database")
        deploy_database
        ;;
    "redis")
        deploy_redis
        ;;
    "app")
        deploy_application
        ;;
    "monitoring")
        deploy_monitoring
        ;;
    "cleanup")
        cleanup
        ;;
    "health")
        health_check
        ;;
    *)
        main
        ;;
esac
