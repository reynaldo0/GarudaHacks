#!/bin/bash
set -e

# ============================================================================
# PROJECT THEMIS - Frontend Deploy Script
# ============================================================================
# Usage: bash deploy-frontend.sh
# Run from the frontend directory on the VPS
# ============================================================================

APP_NAME="themis-frontend"
APP_DIR="/home/reynaldo/projects/python/themis/frontend"
NODE_PORT=3000

echo "============================================="
echo "  PROJECT THEMIS - Frontend Deploy"
echo "============================================="

# --- Step 1: Check Node.js ---
echo ""
echo "[1/6] Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "  Installing Node.js 22.x..."
    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo bash -
    sudo apt-get install -y nodejs
else
    echo "  OK: Node.js $(node -v)"
fi

# --- Step 2: Check PM2 ---
echo ""
echo "[2/6] Checking PM2..."
if ! command -v pm2 &> /dev/null; then
    echo "  Installing PM2..."
    sudo npm install -g pm2
    pm2 startup | tail -1 | sudo bash
else
    echo "  OK: PM2 found"
fi

# --- Step 3: Setup directory ---
echo ""
echo "[3/6] Setting up directory..."
mkdir -p $APP_DIR

# --- Step 4: Copy files ---
echo ""
echo "[4/6] Syncing files..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
rsync -av --delete \
  --exclude 'node_modules' \
  --exclude '.next' \
  --exclude '.git' \
  "$SCRIPT_DIR/" "$APP_DIR/"

# --- Step 5: Install & Build ---
echo ""
echo "[5/6] Installing dependencies and building..."
cd $APP_DIR
npm ci --production=false
npm run build
echo "  OK: Build complete"

# --- Step 6: Start/Restart PM2 ---
echo ""
echo "[6/6] Starting frontend with PM2..."
cd $APP_DIR
pm2 delete $APP_NAME 2>/dev/null || true
pm2 start npm --name $APP_NAME -- start -- -p $NODE_PORT
pm2 save

echo ""
echo "============================================="
echo "  Deploy Complete!"
echo "============================================="
echo ""
echo "  Frontend URL: http://localhost:$NODE_PORT"
echo ""
echo "  PM2 status:   pm2 status"
echo "  PM2 logs:     pm2 logs $APP_NAME"
echo "  PM2 restart:  pm2 restart $APP_NAME"
echo ""
