#!/bin/bash
set -e

# ============================================================================
# PROJECT THEMIS - Backend Deploy Script
# ============================================================================
# Usage: bash deploy-backend.sh
# Run from the backend directory on the VPS
# ============================================================================

APP_NAME="themis-backend"
APP_DIR="/home/reynaldo/projects/python/themis/backend"
SERVICE_NAME="themis"
PYTHON_VERSION="python3"

echo "============================================="
echo "  PROJECT THEMIS - Backend Deploy"
echo "============================================="

# --- Step 1: Check Python ---
echo ""
echo "[1/7] Checking Python..."
if ! command -v $PYTHON_VERSION &> /dev/null; then
    echo "[ERROR] Python3 not found. Install with: sudo apt install -y python3 python3-venv python3-pip"
    exit 1
fi
echo "  OK: $($PYTHON_VERSION --version)"

# --- Step 2: Setup venv ---
echo ""
echo "[2/7] Setting up virtual environment..."
cd $APP_DIR
if [ ! -d ".venv" ]; then
    echo "  Creating new venv..."
    $PYTHON_VERSION -m venv .venv
fi
source .venv/bin/activate
echo "  OK: venv activated"

# --- Step 3: Install dependencies ---
echo ""
echo "[3/7] Installing Python dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "  OK: dependencies installed"

# --- Step 4: Create .env for production ---
echo ""
echo "[4/7] Checking .env configuration..."
if [ -f ".env" ]; then
    echo "  Backing up existing .env to .env.bak..."
    cp .env .env.bak
fi
echo "  Creating production .env..."
cat > .env << 'ENVEOF'
APP_NAME=PROJECT THEMIS
APP_VERSION=6.0.0
APP_ENV=production
APP_DEBUG=false
HOST=0.0.0.0
PORT=8005
DATABASE_URL=mysql+pymysql://themis:themis_pass_2026@127.0.0.1:3306/themis
API_KEY=da1GdehRzd59b71fwyeJDkuXY151hOO_uhIYpDSbNwazer4y3sWudjMNREYLq4Y_
JWT_SECRET=change-this-to-a-random-secret-in-production
CORS_ORIGINS=["https://garudahacks.my.id","https://api.themis.my.id"]
LOG_LEVEL=INFO
ENVEOF
echo "  WARNING: Edit .env with your actual secrets (especially JWT_SECRET)!"

# --- Step 5: Create database tables ---
echo ""
echo "[5/7] Ensuring database tables exist..."
$PYTHON_VERSION -c "
import pymysql; pymysql.install_as_MySQLdb()
from app.database.connection import engine, Base
from app.database.models import *
Base.metadata.create_all(bind=engine)
print('  OK: All tables created/verified')
" 2>&1 || echo "  WARNING: Database table creation failed. Check MySQL connection."

# --- Step 6: Create systemd service ---
echo ""
echo "[6/7] Setting up systemd service..."
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null << SVCEOF
[Unit]
Description=THEMIS FastAPI Backend
After=network.target docker.service
Requires=docker.service

[Service]
User=reynaldo
Group=reynaldo
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/.venv/bin"
ExecStart=${APP_DIR}/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8005 --workers 1
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SVCEOF

sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
echo "  OK: systemd service created"

# --- Step 7: Restart backend ---
echo ""
echo "[7/7] Restarting backend..."
sudo systemctl restart $SERVICE_NAME
sleep 3

if sudo systemctl is-active --quiet $SERVICE_NAME; then
    echo "  OK: Backend is running"
else
    echo "  ERROR: Backend failed to start!"
    sudo journalctl -u $SERVICE_NAME --no-pager -n 20
    exit 1
fi

# --- Verify ---
echo ""
echo "============================================="
echo "  Deploy Complete!"
echo "============================================="
echo ""
echo "  Backend URL:  http://localhost:8005"
echo "  Health:       http://localhost:8005/health"
echo "  API Docs:     http://localhost:8005/docs"
echo ""
echo "  Service:      sudo systemctl status $SERVICE_NAME"
echo "  Logs:         sudo journalctl -u $SERVICE_NAME -f"
echo "  Restart:      sudo systemctl restart $SERVICE_NAME"
echo ""
