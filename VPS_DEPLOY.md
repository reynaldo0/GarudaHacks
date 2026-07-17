# VPS Deployment Guide - PROJECT THEMIS

Step-by-step deploy ke VPS: Docker MySQL, Backend FastAPI, Frontend Next.js, WebSocket, SSL.

---

## Server Requirements

| Item | Minimum |
|------|---------|
| OS | Ubuntu 22.04 LTS |
| CPU | 2 vCPU |
| RAM | 4 GB |
| Storage | 40 GB SSD |
| Ports | 80, 443 |

## Architecture

```
Internet
  |
  v
Nginx (80/443)
  |-- themis.my.id --> Frontend (PM2, port 3000)
  |                       --> /api/* --> Backend (port 8005)
  |                       --> /ws    --> Backend WebSocket (port 8005)
  |-- api.themis.my.id  --> Backend (port 8005)
  |                       --> /ws    --> Backend WebSocket (port 8005)
  v
Backend (port 8005) --> MySQL Docker (port 3306)
```

---

## Step 1: Server Initial Setup

```bash
ssh reynaldo@<YOUR_VPS_IP>

# Update system
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git ufw

# Firewall
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## Step 2: Install Docker

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
# Log out and back in
exit
```

Re-login, verify:

```bash
docker --version
docker compose version
```

---

## Step 3: Deploy MySQL (Docker)

```bash
mkdir -p /home/reynaldo/projects/python/themis
cd /home/reynaldo/projects/python/themis
```

Copy `docker-compose.yml` from project root, then:

```bash
docker compose up -d
docker compose ps
docker exec themis-mysql mysqladmin ping -u root -pthemis_root_2026
```

---

## Step 4: Deploy Backend

```bash
cd /home/reynaldo/projects/python/themis

# Copy backend files (git or scp)
git clone <repo> temp && mv temp/backend . && rm -rf temp

# Setup
cd backend
python3 -m venv .venv
    source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Create `.env` (see backend/.env.example for all vars). Key vars:

```bash
cat > .env << 'ENVEOF'
APP_NAME=PROJECT THEMIS
APP_VERSION=6.0.0
APP_ENV=production
APP_DEBUG=false
HOST=0.0.0.0
PORT=8005
DATABASE_URL=mysql+pymysql://themis:themis_pass_2026@127.0.0.1:3306/themis
API_KEY=da1GdehRzd59b71fwyeJDkuXY151hOO_uhIYpDSbNwazer4y3sWudjMNREYLq4Y_
JWT_SECRET=<generate-random>
CORS_ORIGINS=["https://themis.my.id","https://api.themis.my.id"]
LOG_LEVEL=INFO
ENVEOF
```

Create tables + test:

```bash
source .venv/bin/activate
python -c "import pymysql; pymysql.install_as_MySQLdb(); from app.database.connection import engine, Base; from app.database.models import *; Base.metadata.create_all(bind=engine); print('Tables OK')"
uvicorn main:app --host 0.0.0.0 --port 8005
# Ctrl+C to stop
```

Setup systemd:

```bash
sudo tee /etc/systemd/system/themis.service > /dev/null << 'SVCEOF'
[Unit]
Description=THEMIS FastAPI Backend
After=network.target docker.service
Requires=docker.service

[Service]
User=reynaldo
Group=reynaldo
WorkingDirectory=/home/reynaldo/projects/python/themis/backend
Environment="PATH=/home/reynaldo/projects/python/themis/backend/.venv/bin"
ExecStart=/home/reynaldo/projects/python/themis/backend/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8005
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SVCEOF

sudo systemctl daemon-reload
sudo systemctl enable themis
sudo systemctl start themis
curl http://localhost:8005/health
```

---

## Step 5: Deploy Frontend

```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo bash -
sudo apt-get install -y nodejs

# Install PM2
sudo npm install -g pm2

# Setup frontend
cd /home/reynaldo/projects/python/themis/frontend
npm ci
npm run build

# Start with PM2
pm2 start npm --name "themis-frontend" -- start -- -p 3000
pm2 save
pm2 startup
# Follow printed instructions

# Verify
curl http://localhost:3000
pm2 status
```

---

## Step 6: Configure Nginx

```bash
sudo apt install -y nginx

sudo tee /etc/nginx/sites-available/themis > /dev/null << 'NGINXEOF'
server {
    listen 80;
    server_name themis.my.id www.themis.my.id;
    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8005;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 50M;
        proxy_read_timeout 300s;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8005;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 86400;
    }
}

server {
    listen 80;
    server_name api.themis.my.id;
    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8005;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8005;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
NGINXEOF

sudo ln -sf /etc/nginx/sites-available/themis /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

---

## Step 7: SSL with Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d themis.my.id -d api.themis.my.id
sudo certbot renew --dry-run
```

---

## Step 8: Point Domain DNS

  | Domain | Type | Value |
  |--------|------|-------|
  | themis.my.id | A | YOUR_VPS_IP |
  | api.themis.my.id | A | YOUR_VPS_IP |

---

## Step 9: WebSocket Verification

```bash
# Test WebSocket connection
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
  http://localhost:8005/ws
```

Expected: HTTP 101 Switching Protocols

---

## Service Management

| Action | Command |
|--------|---------|
| Backend status | `sudo systemctl status themis` |
| Backend restart | `sudo systemctl restart themis` |
| Backend logs | `sudo journalctl -u themis -f` |
| Frontend status | `pm2 status` |
| Frontend restart | `pm2 restart themis-frontend` |
| Frontend logs | `pm2 logs themis-frontend` |
| MySQL status | `docker compose ps` |
| MySQL shell | `docker exec -it themis-mysql mysql -u root -pthemis_root_2026` |
| MySQL restart | `docker compose restart` |
| Nginx reload | `sudo systemctl reload nginx` |

---

## Database Backup

```bash
# Backup
docker exec themis-mysql mysqldump -u root -pthemis_root_2026 themis > backup_$(date +%Y%m%d).sql

# Restore
docker exec -i themis-mysql mysql -u root -pthemis_root_2026 themis < backup.sql
```

---

## Troubleshooting

**Backend won't start:**
```bash
sudo journalctl -u themis -n 50
# Check if port is in use
sudo lsof -i :8005
# Check MySQL connection
cd backend && source .venv/bin/activate && python -c "import pymysql; pymysql.install_as_MySQLdb(); c=pymysql.connect(host='127.0.0.1',port=3306,user='root',password='themis_root_2026',database='themis'); print('DB OK'); c.close()"
```

**Frontend 502 Bad Gateway:**
```bash
# Check backend is running
curl http://localhost:8005/health
# Check PM2
pm2 status
pm2 logs themis-frontend
```

**WebSocket not connecting:**
```bash
# Check nginx config
sudo nginx -t
# Check backend WebSocket endpoint
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" http://localhost:8005/ws
```

**MySQL connection refused:**
```bash
docker compose ps
docker compose logs mysql --tail 20
# Full reset
docker compose down -v
docker compose up -d
```

**Tables not created:**
```bash
cd backend && source .venv/bin/activate
python -c "import pymysql; pymysql.install_as_MySQLdb(); from app.database.connection import engine, Base; from app.database.models import *; Base.metadata.create_all(bind=engine); print('Tables created')"
```
