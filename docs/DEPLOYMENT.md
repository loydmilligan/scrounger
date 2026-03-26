# Scrounger Deployment Guide

## Quick Start (New Raspberry Pi)

### Prerequisites

- Raspberry Pi 4 or 5 (4GB+ RAM recommended)
- Raspberry Pi OS (64-bit)
- Docker and Docker Compose installed
- Git installed

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/Scrounger.git
cd Scrounger

# 2. Copy environment template and configure
cp .env.example .env
nano .env  # Edit with your settings

# 3. Build and start containers
docker compose up -d --build

# 4. Run database migrations
docker compose exec backend alembic upgrade head

# 5. (Optional) Seed default data
docker compose exec backend python -m src.scripts.seed

# 6. Access the application
# Frontend: http://YOUR_PI_IP:8851
# Backend API: http://YOUR_PI_IP:8849
```

---

## Detailed Setup

### 1. Install Docker on Raspberry Pi

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group (logout/login required)
sudo usermod -aG docker $USER

# Install Docker Compose plugin
sudo apt install docker-compose-plugin -y

# Verify installation
docker --version
docker compose version
```

### 2. Clone and Configure

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/Scrounger.git
cd Scrounger

# Create environment file
cp .env.example .env

# Edit configuration
nano .env
```

**Required settings in `.env`:**
```
OPENROUTER_API_KEY=sk-or-v1-your-actual-key
USER_STATE=TX  # Your state
USER_ZIP=78701  # Your ZIP
```

### 3. Build and Start

```bash
# Build containers (first time takes ~5-10 minutes on Pi)
docker compose build

# Start in background
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### 4. Database Setup

```bash
# Run migrations
docker compose exec backend alembic upgrade head

# Seed default categories and marketplaces
docker compose exec backend python -m src.scripts.seed
```

### 5. Verify Installation

```bash
# Check backend health
curl http://localhost:8849/health

# Check frontend
curl http://localhost:8851
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./data/scrounger.db` | Database connection string |
| `OPENROUTER_API_KEY` | (required) | OpenRouter API key for AI features |
| `OPENROUTER_MODEL` | `anthropic/claude-3.5-sonnet` | Default AI model |
| `USER_STATE` | `TX` | Your state for post formatting |
| `USER_ZIP` | `78701` | Your ZIP for shipping estimates |
| `BACKEND_PORT` | `8849` | Backend API port |
| `FRONTEND_PORT` | `8851` | Frontend web port |
| `DEBUG` | `false` | Enable debug mode |

### Ports

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 8851 | Web interface |
| Backend | 8849 | REST API |

### Data Persistence

Data is stored in:
- `./backend/data/scrounger.db` - SQLite database
- Volume mounted to container at `/app/data`

**To backup:**
```bash
cp backend/data/scrounger.db backup/scrounger_$(date +%Y%m%d).db
```

---

## Database Migrations

### Running Migrations

```bash
# Apply all pending migrations
docker compose exec backend alembic upgrade head

# Check current version
docker compose exec backend alembic current

# View migration history
docker compose exec backend alembic history
```

### Creating New Migrations

```bash
# Auto-generate from model changes
docker compose exec backend alembic revision --autogenerate -m "Description of changes"

# Create empty migration for manual edits
docker compose exec backend alembic revision -m "Description"
```

### Rolling Back

```bash
# Downgrade one version
docker compose exec backend alembic downgrade -1

# Downgrade to specific version
docker compose exec backend alembic downgrade abc123
```

---

## Updating

### Standard Update

```bash
# Pull latest code
git pull origin main

# Rebuild containers
docker compose build

# Apply migrations
docker compose exec backend alembic upgrade head

# Restart with new code
docker compose up -d
```

### Update with Database Changes

```bash
# Backup database first
cp backend/data/scrounger.db backend/data/scrounger_backup.db

# Pull and rebuild
git pull origin main
docker compose build

# Apply migrations
docker compose exec backend alembic upgrade head

# Restart
docker compose up -d
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs backend
docker compose logs frontend

# Rebuild from scratch
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Database Errors

```bash
# Check database file exists
ls -la backend/data/

# Verify migrations
docker compose exec backend alembic current

# Reset database (WARNING: deletes all data)
rm backend/data/scrounger.db
docker compose exec backend alembic upgrade head
docker compose exec backend python -m src.scripts.seed
```

### Permission Issues

```bash
# Fix data directory permissions
sudo chown -R $USER:$USER backend/data/
chmod 755 backend/data/
```

### Port Conflicts

```bash
# Check what's using the port
sudo lsof -i :8849
sudo lsof -i :8851

# Change ports in .env
BACKEND_PORT=8850
FRONTEND_PORT=8852

# Rebuild
docker compose up -d
```

---

## Moving to a New Pi

### On Old Pi

```bash
# Stop containers
docker compose down

# Backup database
cp backend/data/scrounger.db ~/scrounger_backup.db

# Copy to new Pi (example using scp)
scp ~/scrounger_backup.db pi@NEW_PI_IP:~/
scp ~/.env pi@NEW_PI_IP:~/scrounger.env
```

### On New Pi

```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/Scrounger.git
cd Scrounger

# Restore configuration
cp ~/scrounger.env .env

# Restore database
mkdir -p backend/data
cp ~/scrounger_backup.db backend/data/scrounger.db

# Build and start
docker compose up -d --build

# Verify data
docker compose exec backend alembic current
```

---

## Production Considerations

### Security

1. **Change default ports** in production
2. **Use HTTPS** - set up a reverse proxy (nginx/caddy) with SSL
3. **Restrict CORS** - modify backend for specific origins
4. **Backup regularly** - set up automated backups

### Performance

1. **Increase swap** on low-memory Pis:
   ```bash
   sudo dphys-swapfile swapoff
   sudo nano /etc/dphys-swapfile  # CONF_SWAPSIZE=2048
   sudo dphys-swapfile setup
   sudo dphys-swapfile swapon
   ```

2. **Use SSD** instead of SD card for better database performance

### Monitoring

```bash
# Resource usage
docker stats

# Disk usage
df -h
du -sh backend/data/

# Container health
docker compose ps
```

---

## n8n Integration (Optional)

If using n8n for Reddit email automation:

1. **Network configuration:**
   ```yaml
   # In docker-compose.yml, add external network
   networks:
     scrounger-network:
       external: true
       name: n8n_network
   ```

2. **Use internal Docker hostname:**
   - From n8n, call `http://scrounger-backend:8000/api/webhook/reddit-email`
   - Or use host IP: `http://192.168.X.X:8849/api/webhook/reddit-email`

---

*Last updated: 2026-03-26*
