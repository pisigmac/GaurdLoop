# Deployment Guide

## Local Development

```bash
docker-compose up --build
```

## Staging

```bash
# Build images
docker build -t guardloop/backend:staging ./backend
docker build -t guardloop/frontend:staging ./frontend

# Push to registry
docker push guardloop/backend:staging
docker push guardloop/frontend:staging

# Deploy to staging K8s cluster
kubectl apply -f infra/k8s/ --namespace=guardloop-staging
```

## Production (Kubernetes)

### Prerequisites

- K8s cluster (EKS/GKE/AKS or self-hosted)
- cert-manager for TLS
- nginx-ingress controller
- External DNS (optional)

### Steps

1. **Create namespace and secrets**
   ```bash
   kubectl apply -f infra/k8s/namespace.yaml
   kubectl apply -f infra/k8s/secret.yaml
   kubectl apply -f infra/k8s/configmap.yaml
   ```

2. **Deploy data layer**
   ```bash
   kubectl apply -f infra/k8s/postgres.yaml
   kubectl apply -f infra/k8s/redis.yaml
   ```

3. **Deploy application**
   ```bash
   kubectl apply -f infra/k8s/backend.yaml
   kubectl apply -f infra/k8s/frontend.yaml
   kubectl apply -f infra/k8s/ingress.yaml
   ```

4. **Verify**
   ```bash
   kubectl get pods -n guardloop
   kubectl get svc -n guardloop
   kubectl get ingress -n guardloop
   ```

### Rollback

```bash
kubectl rollout undo deployment/guardloop-backend -n guardloop
```
