# PROJECT THEMIS 🚆

> **AI-Powered Railway Occupancy Intelligence & Decision Support Platform**

PROJECT THEMIS is an intelligent railway operation platform that leverages Artificial Intelligence, Computer Vision, and Digital Twin technology to provide real-time passenger occupancy monitoring, operational analytics, and AI-driven decision support for railway operators.

---

# 🚨 The Problem

Urban railway systems transport millions of passengers every day. However, operators still face significant challenges in monitoring passenger distribution inside train carriages in real time.

Without accurate occupancy information, operators often struggle to:

- Detect overcrowded carriages before they become critical.
- Monitor passenger distribution across multiple train cars simultaneously.
- Make fast, data-driven operational decisions.
- Analyze historical occupancy trends for service optimization.
- Improve passenger comfort and operational efficiency.

As a result, overcrowding frequently occurs while nearby carriages remain underutilized, reducing both passenger experience and operational effectiveness.

---

# 💡 Our Solution

PROJECT THEMIS addresses these challenges through an AI-powered decision support platform that combines Computer Vision, Machine Learning, and Digital Twin technology.

Using cameras installed inside train carriages, our AI continuously analyzes passenger occupancy and transforms raw visual data into actionable operational intelligence.

The platform provides railway operators with:

- 🚆 Real-time passenger occupancy monitoring
- 🧠 AI-generated operational recommendations
- 📊 Historical analytics and occupancy trends
- 🌐 Interactive Digital Twin visualization
- ⚡ Real-time dashboard for railway operations
- 📡 Live communication through WebSocket
- 📈 Decision support for smarter railway management

Instead of reacting after overcrowding occurs, PROJECT THEMIS enables operators to proactively monitor conditions and make faster, smarter, and data-driven decisions.

---

# 🎯 Vision

Our vision is to transform railway operations through intelligent decision support, making public transportation safer, more efficient, and more sustainable.

PROJECT THEMIS evolves from an occupancy monitoring system into a scalable AI platform capable of supporting future intelligent transportation ecosystems.

---

# ✨ Key Features

- 🤖 AI-based Passenger Occupancy Detection
- 🚆 Real-time Occupancy Monitoring
- 📊 Interactive Analytics Dashboard
- 🌍 Digital Twin Train Visualization (Unity)
- 📡 WebSocket Live Updates
- 📈 Historical Occupancy Analytics
- 🧠 AI Recommendation Engine
- 📷 Multi-camera Image Processing Pipeline
- 🔐 Secure REST API
- 🐳 Docker-based Deployment
- ☁️ Production-ready Architecture

---

# 🏗️ System Architecture

```text
Train Cameras
      │
      ▼
 Computer Vision & AI
      │
      ▼
 FastAPI Backend
      │
 ┌────┴─────────┐
 ▼              ▼
MySQL      WebSocket
      │
      ▼
 Next.js Dashboard
      │
      ▼
 Unity Digital Twin
      │
      ▼
 Railway Operators
```

---

## Tech Stack

### Backend
| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| Web Framework | FastAPI 0.115 |
| ASGI Server | Uvicorn 0.30 |
| ORM | SQLAlchemy 2.0 |
| Database | MySQL 8.0 (Docker) via PyMySQL |
| AI/CV | OpenCV, NumPy, Pillow, Ultralytics |
| WebSocket | FastAPI WebSocket + websockets |
| Logging | Loguru |

### Frontend
| Component | Technology |
|-----------|-----------|
| Framework | Next.js 16 (App Router) |
| UI Library | React 19 |
| Language | TypeScript |
| Styling | Tailwind CSS 4 |
| State | Zustand 5 |
| Charts | Recharts 3 |
| Icons | Lucide React |

### Infrastructure
| Component | Technology |
|-----------|-----------|
| Database | MySQL 8.0 (Docker container) |
| Reverse Proxy | Nginx |
| Process Manager | PM2 (production) |
| Digital Twin | Unity (C#) |

---

## Prerequisites

- **Python 3.10+**
- **Node.js 22+**
- **Docker** (for MySQL database)
- **Git**

---

## Quick Start (Local Development)

### 1. Clone Repository

```bash
git clone <repo-url> GarudaHack
cd GarudaHack
```

### 2. Start MySQL (Docker)

```bash
docker run -d \
  --name themis-mysql \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=themis \
  -p 3306:3306 \
  mysql:8.0 \
  --default-authentication-plugin=mysql_native_password
```

Verify:

```bash
docker ps | grep themis-mysql
mysql -h 127.0.0.1 -u root -proot -e "SHOW DATABASES;"
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env            # or edit .env directly
```

Edit `.env`:

```ini
DATABASE_URL=mysql+pymysql://root:root@127.0.0.1:3306/themis
PORT=8005
HOST=0.0.0.0
API_KEY=da1GdehRzd59b71fwyeJDkuXY151hOO_uhIYpDSbNwazer4y3sWudjMNREYLq4Y_
```

Create tables:

```bash
python -c "
import pymysql; pymysql.install_as_MySQLdb()
from app.database.connection import engine, Base
from app.database.models import *
Base.metadata.create_all(bind=engine)
print('Tables created')
"
```

Start backend:

```bash
# Option A: start script
./start.bat                  # Windows
# Option B: direct
uvicorn main:app --host 0.0.0.0 --port 8005 --reload
```

Verify:

```bash
curl http://localhost:8005/health
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Open: http://localhost:3000

---

## VPS Deployment (Ubuntu/Debian)

### 1. Server Requirements

| Resource | Minimum |
|----------|---------|
| OS | Ubuntu 22.04 LTS |
| CPU | 2 vCPU |
| RAM | 4 GB |
| Storage | 40 GB SSD |
| Ports | 80, 443, 8005, 3000 |

### 2. Initial Server Setup

```bash
# SSH into server
ssh reynaldo@<server-ip>

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install -y docker.io docker-compose-v2
sudo systemctl enable docker
sudo usermod -aG docker $USER
# Log out and back in for docker group

# Install Nginx
sudo apt install -y nginx

# Install Node.js 22
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

# Install PM2
sudo npm install -g pm2
```

### 3. Deploy MySQL (Docker)

```bash
# Create docker-compose.yml
mkdir -p /home/reynaldo/docker
cat > /home/reynaldo/docker/docker-compose.yml << 'EOF'
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: themis-mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: themis
    ports:
      - "3306:3306"
    volumes:
      - themis_mysql_data:/var/lib/mysql
    command: >
      --default-authentication-plugin=mysql_native_password
      --character-set-server=utf8mb4
      --collation-server=utf8mb4_unicode_ci
      --max-connections=200
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  themis_mysql_data:
    driver: local
EOF

# Start MySQL
cd /home/reynaldo/docker
docker compose up -d

# Verify
docker compose ps
docker exec themis-mysql mysql -u root -proot -e "SHOW DATABASES;"
```

### 4. Deploy Backend

```bash
# Create project directory
mkdir -p /home/reynaldo/projects/python/themis
cd /home/reynaldo/projects/python/themis

# Clone/copy backend
git clone <repo-url> temp
mv temp/backend .
rm -rf temp

# Setup Python
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Configure `.env`:

```bash
cat > .env << 'EOF'
APP_NAME=PROJECT THEMIS
APP_VERSION=6.0.0
APP_ENV=production
APP_DEBUG=false
HOST=0.0.0.0
PORT=8005
DATABASE_URL=mysql+pymysql://root:root@127.0.0.1:3306/themis
API_KEY=da1GdehRzd59b71fwyeJDkuXY151hOO_uhIYpDSbNwazer4y3sWudjMNREYLq4Y_
JWT_SECRET=your-production-secret-change-this
CORS_ORIGINS=["https://garudahacks.my.id","https://api.themis.my.id"]
LOG_LEVEL=INFO
EOF
```

Create tables:

```bash
.venv/bin/python -c "
import pymysql; pymysql.install_as_MySQLdb()
from app.database.connection import engine, Base
from app.database.models import *
Base.metadata.create_all(bind=engine)
print('Tables created')
"
```

Create systemd service:

```bash
sudo cat > /etc/systemd/system/themis.service << 'EOF'
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
EOF

sudo systemctl daemon-reload
sudo systemctl enable themis
sudo systemctl start themis
sudo systemctl status themis
```

Verify:

```bash
curl http://localhost:8005/health
```

### 5. Deploy Frontend

```bash
mkdir -p /home/reynaldo/projects/python/themis/frontend
cd /home/reynaldo/projects/python/themis/frontend

# Copy frontend files
# (git clone or rsync from local)

npm ci
npm run build
```

Start with PM2:

```bash
pm2 start npm --name "themis-frontend" -- start -- -p 3000
pm2 save
pm2 startup    # follow the output instructions
```

### 6. Configure Nginx

```bash
sudo cat > /etc/nginx/sites-available/themis << 'EOF'
# Frontend + Backend reverse proxy
server {
    listen 80;
    server_name garudahacks.my.id;

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

# Direct backend access (Unity clients)
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
    }

    location /ws {
        proxy_pass http://127.0.0.1:8005;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/themis /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

### 7. SSL with Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d garudahacks.my.id -d api.themis.my.id
sudo certbot renew --dry-run
```

---

## Environment Variables

### Backend `.env`

```ini
# Application
APP_NAME=PROJECT THEMIS
APP_VERSION=6.0.0
APP_ENV=development
APP_DEBUG=true

# Server
HOST=0.0.0.0
PORT=8005

# Database (Docker MySQL)
DATABASE_URL=mysql+pymysql://root:root@127.0.0.1:3306/themis

# AI Model
SEGMENTATION_MODEL_PATH=weights/segmentation_model.pth
SEGMENTATION_CONFIDENCE=0.5
SEGMENTATION_IMAGE_SIZE=640

# Fisheye Camera
FISHEYE_CALIBRATION_DIR=config/calibration

# Density Thresholds
DENSITY_GREEN_THRESHOLD=0.6
DENSITY_YELLOW_THRESHOLD=0.3
DENSITY_RED_THRESHOLD=0.0

# Train Configuration
DEFAULT_TRAIN_FORMATION=SF10
DEFAULT_CAPACITY=200
FLOOR_AREA_M2=42.0

# Camera (40 total, 4 per car)
NUM_CAMERAS_PER_CAR=4
CAMERA_TYPE=ceiling_fisheye

# Door Automation
DOOR_MIDDLE_OPEN_ON_RED=true

# Redistribution
REDISTRIBUTION_ENABLED=true
REDISTRIBUTION_MIN_DIFF=0.2

# CALES Bogie Maintenance
CALES_HISTORY_SIZE=100
CALES_WHEEL_FLANGE_NOMINAL_MONTHS=12
CALES_AIR_SPRING_NOMINAL_MONTHS=192
CALES_CHEVRON_RUBBER_NOMINAL_MONTHS=72

# WebSocket
WS_PATH=/ws
WS_HEARTBEAT=30

# Logging
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=["http://localhost:3000","https://garudahacks.my.id"]

# Auth
JWT_SECRET=change-this-in-production
API_KEY=da1GdehRzd59b71fwyeJDkuXY151hOO_uhIYpDSbNwazer4y3sWudjMNREYLq4Y_
```

### Frontend `.env.local`

```ini
NEXT_PUBLIC_FRAME_API_KEY=da1GdehRzd59b71fwyeJDkuXY151hOO_uhIYpDSbNwazer4y3sWudjMNREYLq4Y_
```

---

## API Endpoints

Base URL: `http://localhost:8005`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | No | App info |
| GET | `/health` | No | Health check |
| **POST** | **`/api/v1/frame`** | **X-API-Key** | **Upload 4 fisheye frames → full AI pipeline** |
| GET | `/api/v1/health` | No | Detailed health (DB, AI, cameras) |
| GET | `/api/v1/state` | No | Full system state |
| GET | `/api/v1/occupancy` | No | All cars occupancy data |
| GET | `/api/v1/occupancy/{car_id}` | No | Single car occupancy |
| GET | `/api/v1/recommendation` | No | Redistribution recommendations |
| GET | `/api/v1/history` | No | Historical occupancy records |
| GET | `/api/v1/history/warnings` | No | Warning history |
| GET | `/api/v1/config` | No | System configuration |
| GET | `/api/v1/config/lookup-table` | No | Camera-to-car mapping |
| POST | `/api/v1/simulation/scenario/{name}` | No | Load scenario (empty/normal/peak_hour/holiday/imbalanced/emergency) |
| POST | `/api/v1/simulation/reset` | No | Reset simulation |
| POST | `/api/v1/auth/login` | No | Operator login |
| POST | `/api/v1/auth/register` | No | Operator registration |
| **WS** | **`/ws`** | No | **WebSocket realtime events** |

### Core Pipeline Endpoint

```bash
curl -X POST http://localhost:8005/api/v1/frame \
  -H "X-API-Key: da1GdehRzd59b71fwyeJDkuXY151hOO_uhIYpDSbNwazer4y3sWudjMNREYLq4Y_" \
  -F "files=@cam1.jpg" \
  -F "files=@cam2.jpg" \
  -F "files=@cam3.jpg" \
  -F "files=@cam4.jpg" \
  -F "camera_ids=cam01,cam02,cam03,cam04" \
  -F "station_id=duri" \
  -F "train_id=SF10-001"
```

### WebSocket Events

```json
{
  "type": "pipeline_state_updated",
  "data": { "car_id": "car_01", "occupancy_ratio": 0.65, "density_indicator": "YELLOW" }
}
{
  "type": "occupancy_updated",
  "data": { "train_id": "SF10-001", "cars": [...] }
}
{
  "type": "warning_updated",
  "data": { "severity": "CRITICAL", "message": "Car 3 is RED density" }
}
{
  "type": "recommendation_changed",
  "data": { "from_car_id": 3, "to_car_id": 8, "confidence": 0.82 }
}
```

---

## AI Pipeline

Each frame upload triggers a 12-step pipeline:

```
1.  VideoAdapter       → Decode + fisheye undistortion + resize 640x640
2.  SpatialEngine      → Spatial occupancy segmentation (per frame)
3.  FusionEngine       → Fuse 4 camera grids into 1 carriage map
4.  OccupancyEngine    → Calculate occupancy_ratio, free_space_ratio, risk
5.  DensityClassifier  → GREEN (>60% free) / YELLOW (30-60%) / RED (<30%)
6.  CCALESEngine       → Bogie health: asymmetry, severity, duration → cales_score
7.  RedistributionEngine → Find best target carriage if imbalance > 0.2
8.  DoorEngine         → OPEN_MIDDLE only if RED + valid target < 70%
9.  AnnouncementEngine → "Carriage X has available capacity..."
10. DecisionEngine     → Warning generation (CRITICAL/WARNING/INFO)
11. PersistenceService → Save to 5 MySQL tables
12. IntegrationHub     → Broadcast via WebSocket
```

---

## Database Tables

| Table | Records Per Upload | Description |
|-------|-------------------|-------------|
| `occupancy_history` | 1 | Occupancy metrics per car |
| `prediction_history` | 1 | Predicted occupancy + risk |
| `warning_history` | 0-1 | Only for RED/YELLOW density |
| `decision_history` | 0-1 | Only when redistribution recommended |
| `bogie_history` | 1 | CALES health scores |
| `system_log` | - | System event logs |
| `camera_configuration` | - | 40 camera definitions |
| `train_configuration` | - | Train formation info |

---

## Unity Integration

Unity Digital Twin connects to:

| URL | Purpose |
|-----|---------|
| `http://localhost:8005/api/v1/frame` | Upload 4 fisheye frames |
| `ws://localhost:8005/ws` | Realtime WebSocket events |

Unity scripts are in `unity/Assets/Scripts/`:

| Script | Purpose |
|--------|---------|
| `Camera/CameraSimulator.cs` | Simulates 4 cameras, POSTs frames every 5s |
| `Network/ApiClient.cs` | HTTP client for REST API |
| `Network/WebSocketClient.cs` | WebSocket client for realtime |
| `Managers/AppManager.cs` | Main orchestrator, parses PipelineState |
| `Train/DoorController.cs` | Door OPEN_MIDDLE/CLOSE animation |
| `Train/BogieDashboard.cs` | CALES health display |
| `Indicators/LEDIndicator.cs` | GREEN/YELLOW/RED LED |

---

## Simulation Scenarios

```bash
# Load a scenario
curl -X POST http://localhost:8005/api/v1/simulation/scenario/peak_hour

# Reset to empty
curl -X POST http://localhost:8005/api/v1/simulation/reset
```

| Scenario | Description |
|----------|-------------|
| `empty` | No passengers |
| `normal` | Balanced mid-day (~36%) |
| `peak_hour` | Rush hour (~77%) |
| `holiday` | Light traffic (~14%) |
| `imbalanced` | Redistribution test (97% → 5%) |
| `emergency` | Multiple RED (75-99%) |

---

## Docker MySQL Management

```bash
# Start
docker start themis-mysql

# Stop
docker stop themis-mysql

# Restart
docker restart themis-mysql

# Logs
docker logs themis-mysql

# Enter MySQL shell
docker exec -it themis-mysql mysql -u root -proot

# Backup database
docker exec themis-mysql mysqldump -u root -proot themis > backup.sql

# Restore database
docker exec -i themis-mysql mysql -u root -proot themis < backup.sql

# Remove (will lose data unless volume persists)
docker rm -f themis-mysql
```

---

## Troubleshooting

### Backend won't start

```bash
# Check logs
sudo journalctl -u themis -f

# Check if port is in use
sudo lsof -i :8005

# Test database connection
cd backend && .venv/bin/python -c "
import pymysql; pymysql.install_as_MySQLdb()
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='themis')
print('Connected'); conn.close()
"
```

### Tables not created

```bash
cd backend
.venv/bin/python -c "
import pymysql; pymysql.install_as_MySQLdb()
from app.database.connection import engine, Base
from app.database.models import *
Base.metadata.create_all(bind=engine)
print('Tables created')
"
```

### MySQL container issues

```bash
# Check container status
docker ps -a | grep themis

# Check MySQL is ready
docker exec themis-mysql mysqladmin ping -u root -proot

# Full reset
docker rm -f themis-mysql
docker volume rm docker_themis_mysql_data
# Then re-run the docker run command from step 2
```

### Frontend can't connect to backend

```bash
# Check backend is running
curl http://localhost:8005/health

# Check WebSocket
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" http://localhost:8005/ws
```

---

## Project Structure

```
GarudaHack/
├── backend/                    # Python/FastAPI backend
│   ├── main.py                 # App entry point + lifespan
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment config
│   ├── alembic.ini             # Migration config
│   ├── start.bat               # Windows start script
│   ├── app/
│   │   ├── config/settings.py  # Pydantic Settings
│   │   ├── api/endpoints/      # 9 API endpoint modules
│   │   ├── websocket/router.py # WebSocket endpoint
│   │   ├── ai/                 # 9 AI engine modules
│   │   ├── core/               # StateManager, IntegrationHub, Security
│   │   ├── database/           # SQLAlchemy models + connection
│   │   ├── schemas/            # Pydantic response schemas
│   │   ├── services/persistence.py  # DB persistence service
│   │   └── simulation/seeder.py     # 6 scenario seeders
│   └── alembic/                # Database migrations
│
├── frontend/                   # Next.js 16 frontend
│   ├── src/app/                # 5 pages (Dashboard, Train, Upload, History, Simulation)
│   ├── src/components/         # 12 UI components
│   ├── src/hooks/              # useWebSocket, useVoiceRecommendation
│   ├── src/store/              # Zustand state management
│   ├── src/lib/api.ts          # API client
│   ├── deploy.sh               # VPS deploy script
│   └── nginx-themis.conf       # Nginx config
│
├── unity/                      # Unity Digital Twin
│   └── Assets/Scripts/         # C# scripts (Camera, Network, Train, UI)
│
├── postman_collection.json     # API test collection
├── UNITY_API_ENDPOINTS.md      # Full API reference
└── README.md                   # This file
```

---

## License

Internal project - GarudaHack Team.
