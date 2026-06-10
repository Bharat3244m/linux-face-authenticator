#!/bin/bash
# Description: Safely removes the faceauth module and restores system defaults.
# Target OS: Linux (Universal / OS-Agnostic)

set -euo pipefail

# --- Configuration Variables ---
APP_NAME="faceauth"
INSTALL_DIR="/opt/$APP_NAME"
BIN_DIR="/usr/local/bin"
SYSTEMD_DIR="/etc/systemd/system"
PAM_FILE="/etc/pam.d/sudo"

# --- Logging Functions ---
log_info() { echo -e "[INFO] $1"; }
log_err()  { echo -e "[ERROR] $1" >&2; exit 1; }

# --- Pre-flight Checks ---
if [[ "$EUID" -ne 0 ]]; then
    log_err "Uninstallation requires root privileges. Please execute with sudo."
fi

log_info "Initiating uninstallation of $APP_NAME..."

# --- 1. Service Teardown ---
log_info "Terminating background services..."
# Safely check if systemd actually exists on this Linux distribution before calling it
if command -v systemctl >/dev/null 2>&1; then
    if systemctl is-active --quiet faceauth.service 2>/dev/null || systemctl is-enabled --quiet faceauth.service 2>/dev/null; then
        systemctl disable --now faceauth.service || true
    fi
    rm -f "$SYSTEMD_DIR/faceauth.service"
    systemctl daemon-reload || true
else
    log_info "Systemd engine not detected. Bypassing service termination."
    rm -f "$SYSTEMD_DIR/faceauth.service"
fi

# --- 2. PAM Restoration ---
log_info "Restoring default PAM configuration..."
if grep -q "faceauth-trigger" "$PAM_FILE"; then
    sed -i '/faceauth-trigger/d' "$PAM_FILE"
    log_info "PAM configuration restored successfully."
else
    log_info "No faceauth rules found in PAM configuration."
fi

# --- 3. Asset Purge ---
log_info "Removing application binaries and working directories..."
rm -rf "$INSTALL_DIR"
rm -f "$BIN_DIR/faceauth"
rm -f "$BIN_DIR/faceauth-trigger"
rm -f /tmp/faceauth.sock

log_info "Uninstallation complete. System restored to standard configuration."