#!/bin/bash

# paths
INSTALL_DIR="/opt/faceauth"
VENV_DIR="$INSTALL_DIR/venv"
SERVICE_FILE="/etc/systemd/system/face_auth.service"

echo "[*] Initializing installation"

# create the double-sandbox
sudo mkdir -p $INSTALL_DIR
sudo python3 -m venv $VENV_DIR
source $VENV_DIR/bin/pip install --upgrade pip

# Hardware flag
HAS_NVIDIA=false

if command -v nvidia-smi &> /dev/null; then
    echo "[*] NVIDIA GPU detected. Engaging CUDA compilation..."
    HAS_NVIDIA=true 
    sudo CUDACXX=/usr/bin/nvcc $VENV_DIR/bin/pip install --no-cache-dir --no-binary dlib dlib
else
    echo 