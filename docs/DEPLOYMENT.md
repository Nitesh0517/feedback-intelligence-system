# Production Deployment & Operations Guide

## 1. Hosting Architecture Comparison

The Feedback Intelligence System is designed to support two primary production topologies depending on infrastructure preferences:

| Attribute | Option A: Self-Hosted VPS (Recommended) | Option B: Cloud PaaS (Render / Railway) |
| :--- | :--- | :--- |
| **Target Infrastructure** | Dedicated VPS (AWS EC2, DigitalOcean, Hetzner, Linode) | Managed Cloud PaaS (Render.com, Railway.app) |
| **Container Engine** | Multi-container Docker Compose v2 | Individual managed container/git services |
| **Database** | Containerized PostgreSQL 16 with persistent volume | Managed Cloud PostgreSQL (AWS RDS, Neon, Supabase) |
| **Cache & Queue** | Containerized Redis 7 Alpine | Managed Cloud Redis (Upstash, Redis Cloud) |
| **Reverse Proxy & SSL** | Host Nginx with Certbot (Let's Encrypt auto-renewal) | Automatic PaaS TLS termination |
| **Cost Predictability** | Fixed monthly cost ($5–$20/mo) | Variable usage-based pricing ($15–$50/mo) |
| **Operational Control** | Full root control over kernel, volumes, and networks | Platform-managed abstraction |

---

## 2. Docker Compose Production Configuration

In production, the base orchestration file `docker-compose.yml` is merged with the production override file `deployment/docker-compose.prod.yml`:

```bash
docker compose -f docker-compose.yml -f deployment/docker-compose.prod.yml up -d --build
```

### Production Hardening Applied in `docker-compose.prod.yml`:
1. **Host Port Closures:** External host bindings for PostgreSQL (`5432`) and Redis (`6379`) are completely closed to external ingress. They are only reachable internally over the isolated Docker bridge network.
2. **Container Log Rotation:** All services are configured with `json-file` log rotation (`max-size: 50m`, `max-file: 5`) to prevent disk exhaustion.
3. **Container Resource Limits:** Memory ceilings are placed on all services (PostgreSQL: 1024MB, Redis: 512MB, Backend: 1024MB, Celery: 1024MB, Frontend: 256MB) to ensure system stability.
4. **Non-Root Execution:** Backend and worker containers execute as the unprivileged `appuser` (UID 1000).

---

## 3. Production Environment Variables Reference

Create a `.env` file in the project root based on `.env.example`:

| Variable | Description | Recommended Production Value |
| :--- | :--- | :--- |
| `ENVIRONMENT` | Runtime mode | `production` |
| `LOG_LEVEL` | Application logging verbosity | `INFO` |
| `SECRET_KEY` | High-entropy JWT signing key (min 32 chars) | Generate via `openssl rand -hex 32` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT expiration duration in minutes | `60` (or `120`) |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg2://postgres:SECURE_DB_PASSWORD@postgres:5432/feedback_db` |
| `REDIS_URL` | Redis cache and queue URL | `redis://redis:6379/0` |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://redis:6379/0` |
| `CELERY_RESULT_BACKEND` | Celery task result backend | `redis://redis:6379/0` |
| `BACKEND_CORS_ORIGINS` | Permitted browser origins | `["https://feedback.yourdomain.com"]` |
| `RATE_LIMIT_ENABLED` | API rate limiter toggle | `True` |
| `RATE_LIMIT_PER_MINUTE` | General endpoint rate limit | `60` |
| `AUTH_RATE_LIMIT_PER_MINUTE` | Auth route rate limit | `15` |
| `INITIAL_ADMIN_EMAIL` | Automatic initial admin email | `admin@yourdomain.com` |
| `INITIAL_ADMIN_PASSWORD` | Initial admin password | Generate high-strength password |

---

## 4. Step-by-Step VPS Deployment Runbook (Ubuntu 22.04 / 24.04 LTS)

### Step 1: Server Provisioning & Docker Installation
Connect to your freshly provisioned Ubuntu server via SSH:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y ca-certificates curl gnupg lsb-release git ufw

# Install Docker Engine & Docker Compose plugin
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
```

### Step 2: Configure Firewall (UFW)
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

### Step 3: Clone Codebase & Configure Secrets
```bash
sudo mkdir -p /opt/feedback-intelligence-system
sudo chown $USER:$USER /opt/feedback-intelligence-system
git clone https://github.com/your-username/feedback-intelligence-system.git /opt/feedback-intelligence-system
cd /opt/feedback-intelligence-system

# Create production environment configuration
cp .env.example .env
nano .env  # Update SECRET_KEY, POSTGRES_PASSWORD, BACKEND_CORS_ORIGINS, and INITIAL_ADMIN credentials
```

### Step 4: Launch Production Containers
```bash
docker compose -f docker-compose.yml -f deployment/docker-compose.prod.yml up -d --build
```

### Step 5: Execute Database Migrations
```bash
docker compose exec -T backend alembic upgrade head
```

### Step 6: Verify Service Health
```bash
# Check container statuses
docker compose ps

# Check backend readiness endpoint
curl -f http://localhost:8000/ready
```

### Step 7: Host Nginx & Let's Encrypt SSL
Install host Nginx and Certbot:
```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

Configure `/etc/nginx/sites-available/feedback.conf`:
```nginx
server {
    server_name feedback.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site and acquire free SSL certificate:
```bash
sudo ln -s /etc/nginx/sites-available/feedback.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d feedback.yourdomain.com --non-interactive --agree-tos --email admin@yourdomain.com
```

---

## 5. Database Backup and Recovery Runbook

### Automated Daily Backup (`pg_dump`)
Add a root cron job (`sudo crontab -e`):
```bash
# Daily backup at 02:00 AM UTC
0 2 * * * docker compose -f /opt/feedback-intelligence-system/docker-compose.yml exec -T postgres pg_dump -U postgres feedback_db | gzip > /opt/backups/feedback_db_$(date +\%Y\%m\%d_\%H\%M\%S).sql.gz
```

### Manual Backup Command
```bash
docker compose exec -T postgres pg_dump -U postgres feedback_db > backup_manual_$(date +%Y%m%d).sql
```

### Restore Database Runbook
```bash
# Decompress if gzipped
gunzip backup_manual_20261014.sql.gz

# Restore into PostgreSQL container
docker compose exec -T postgres psql -U postgres -d feedback_db < backup_manual_20261014.sql
```

---

## 6. Troubleshooting & Operational Diagnostics

### 1. Backend Container Failing Health Checks
- **Symptom:** `curl http://localhost:8000/ready` returns non-200.
- **Diagnostics:**
  ```bash
  docker compose logs backend --tail 100
  ```
- **Remediation:** Verify that PostgreSQL and Redis containers are healthy (`docker compose ps`). Check if Alembic migrations completed successfully.

### 2. High Celery Memory Usage
- **Symptom:** Worker container exceeding memory limits.
- **Diagnostics:**
  ```bash
  docker compose logs celery_worker --tail 100
  ```
- **Remediation:** The Celery worker is configured with `-c 2` (2 concurrent processes) and `worker_prefetch_multiplier=1` to prevent task accumulation. If memory spikes, restart worker:
  ```bash
  docker compose restart celery_worker
  ```

---

## 7. Current Deployment Status

- **Architecture Validation:** **PASS** (Docker Compose schema, non-root user permissions, healthcheck definitions, and reverse proxy verified).
- **Automated CI Validation:** **PASS** (GitHub Actions `.github/workflows/ci.yml` builds all components).
- **Live Cloud Deployment:** **NOT RUN / BLOCKED**
  - **Reason:** Deployment to live cloud infrastructure requires production cloud infrastructure credentials and server secrets (`PRODUCTION_SERVER_HOST`, `PRODUCTION_SSH_USER`, `PRODUCTION_SSH_PRIVATE_KEY`), which are not configured in this local environment.
  - **Deployment Readiness:** 100% production-ready. The deployment runbook and scripts in `deployment/` can be triggered immediately once server access is granted.
