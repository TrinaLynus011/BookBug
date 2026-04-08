# BookBug – DevOps CI/CD Pipeline Demo

BookBug is a book-recommendation web application used to demonstrate a complete DevOps lifecycle:
version control → CI/CD → containerisation → infrastructure as code → container orchestration → automated deployment.

---

## Architecture Overview

```
Developer push
     │
     ▼
GitHub Repository
     │
     ▼
GitHub Actions CI/CD (.github/workflows/ci.yml)
  ├── Lint (flake8)
  ├── Test (pytest)
  ├── Build Docker image
  └── Push to Docker Hub
           │
           ▼
     Docker Hub Registry
           │
     ┌─────┴──────┐
     ▼            ▼
Terraform      Ansible
(infra/)       (ansible/)
AWS VPC/EC2    Pull & run container
           │
           ▼
  Kubernetes Cluster (k8s/)
  ├── bookbug-backend  (2 replicas)
  └── bookbug-frontend (2 replicas)
```

---

## Project Structure

```
BookBug/
├── backend/
│   ├── app/              # FastAPI application
│   ├── tests/            # pytest test suite
│   ├── Dockerfile        # Production Docker image
│   └── requirements.txt
├── frontend/             # React/Vite frontend (unchanged)
├── infra/                # Terraform – AWS VM + networking
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── k8s/                  # Kubernetes manifests
│   ├── deployment.yaml
│   └── service.yaml
├── ansible/              # Ansible automation
│   ├── deploy.yml
│   └── inventory.ini
├── .github/
│   └── workflows/
│       └── ci.yml        # GitHub Actions pipeline
├── docker-compose.yml    # Local full-stack deployment
└── README.md
```

---

## Quick Start – Local Development

```bash
# Copy and edit environment variables
cp .env.example .env   # set SECRET_KEY

# Start all services (backend + frontend + MongoDB)
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

---

## CI/CD Pipeline (GitHub Actions)

The pipeline runs automatically on every push/PR to `main`.

| Stage | Tool | What happens |
|-------|------|-------------|
| Lint | flake8 | PEP-8 style checks |
| Test | pytest | Unit & integration tests |
| Build | Docker Buildx | Multi-platform image build |
| Push | Docker Hub | Image tagged `:latest` + `:sha` |

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |

---

## Infrastructure as Code (Terraform)

Provisions an AWS VPC, public subnet, security group, and EC2 instance that auto-starts the container on boot.

```bash
cd infra/
terraform init
terraform plan -var="dockerhub_username=<you>" -var="secret_key=<key>"
terraform apply
```

Outputs the public IP and backend URL.

---

## Kubernetes Deployment

```bash
# Create namespace + deployments + services
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Verify pods are running
kubectl get pods -n bookbug

# Access the app
# Backend:  http://<node-ip>:30080
# Frontend: http://<node-ip>:30081
```

> Update `your-dockerhub-username` in `k8s/deployment.yaml` before applying.

---

## Ansible Automation

Installs Docker, pulls the image, and starts the container on any Ubuntu host.

```bash
cd ansible/

# Edit inventory.ini with your server IP and SSH key path
ansible-playbook -i inventory.ini deploy.yml \
  -e "dockerhub_username=<you>" \
  -e "secret_key=<key>"
```

---

## DevOps Capabilities Demonstrated

| Capability | Implementation |
|-----------|---------------|
| Version Control | Git + GitHub |
| CI/CD Automation | GitHub Actions |
| Containerisation | Docker + Docker Compose |
| Infrastructure as Code | Terraform (AWS) |
| Container Orchestration | Kubernetes |
| Automated Deployment | Ansible |
| Scalable Architecture | K8s replicas + HPA |
| Observability | Prometheus metrics (`/metrics`) |
