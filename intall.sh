#!/bin/bash
# Description: Installs and configures the faceauth authentication module.
# Target OS: Linux (Debian/Ubuntu)

# Enforce strict error handling:
# -e: Exit immediately if a command exits with a non-zero status.
# -u: Treat unset variables as an error.
# -o pipefail: Return value of a pipeline is the status of the last to exit with a non-zero status.
set -euo pipefail

# --- Configuration Variables ---
APP_NAME="faceauth"
INSTALL_DIR="/opt/$APP_NAME"
VENV_DIR="$INSTALL_DIR/.venv"
BIN_DIR="/usr/local/bin"
SYSTEMD_DIR="/etc/systemd/system"
PAM_FILE="/etc/pam.d/sudo"
PAM_RULE="auth sufficient pam_exec.so quiet $BIN_DIR/faceauth-trigger"
BASELINE_FILE="$INSTALL_DIR/src/user_baseline.npy"

# --- Logging Functions ---
log_info() { echo -e "[INFO] $1"; }
log_warn() { echo -e "[WARN] $1" >&2; }
log_err()  { echo -e "[ERROR] $1" >&2; exit 1; }

# --- Pre-flight Checks ---
if [[ "$EUID" -ne 0 ]]; then
    log_err "Installation requires root privileges. Please execute with sudo."
fi

log_info "Initializing $APP_NAME installation process..."

# --- 1. File System Preparation ---
log_info "Setting up installation directories at $INSTALL_DIR..."
install -d -m 755 "$INSTALL_DIR"
cp -r src/ requirements.txt "$INSTALL_DIR/"

# --- 2. Environment Configuration ---
log_info "Provisioning isolated Python environment..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq python3-venv python3-pip > /dev/null

python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -r "$INSTALL_DIR/requirements.txt"

# --- 3. Binary Deployment ---
log_info "Deploying executable binaries..."
install -m 755 bin/faceauth "$BIN_DIR/faceauth"
install -m 755 -o root -g root security/trigger.py "$BIN_DIR/faceauth-trigger"

# --- 4. PAM Integration ---
log_info "Configuring PAM authentication rules..."
if grep -q "faceauth-trigger" "$PAM_FILE"; then
    log_info "PAM configuration already exists. Bypassing injection."
else
    sed -i "1 a\\$PAM_RULE" "$PAM_FILE"
    log_info "PAM configuration successfully updated."
fi

# --- 5. Biometric Baseline Check ---
if [[ ! -f "$BASELINE_FILE" ]]; then
    log_warn "No biometric baseline detected."
    log_info "Initiating user enrollment sequence..."
    "$BIN_DIR/faceauth" enroll
else
    log_info "Existing biometric baseline verified. Data preserved."
fi

# --- 6. Service Registration ---
log_info "Configuring systemd service..."
install -m 644 systemd/faceauth.service "$SYSTEMD_DIR/"
systemctl daemon-reload
systemctl enable --now faceauth.service

log_info "Installation complete. $APP_NAME service is active."