#!/bin/bash
# Description: Safely removes the sentry module and restores system defaults.

set -euo pipefail

# --- Configuration Variables ---
APP_NAME="sentry"
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
    if systemctl is-active --quiet sentry.service 2>/dev/null || systemctl is-enabled --quiet sentry.service 2>/dev/null; then
        systemctl disable --now sentry.service || true
    fi
    rm -f "$SYSTEMD_DIR/sentry.service"
    systemctl daemon-reload || true
else
    log_info "Systemd engine not detected. Bypassing service termination."
    rm -f "$SYSTEMD_DIR/sentry.service"
fi

# --- 2. PAM Restoration ---
log_info "Auditing PAM Authentication Matrix..."
if grep -q "sentry-trigger" "$PAM_FILE"; then
    log_info "Extracting Sentry hook from sudo configuration..."
    # Surgically delete ONLY the line containing our specific trigger
    sed -i '/sentry-trigger/d' "$PAM_FILE"
    log_info "PAM configuration restored to factory defaults."
else
    log_info "No sentry rules found in PAM configuration. System is clean."
fi

# Clean up the backup file we made during installation
if [[ -f "${PAM_FILE}.sentry.bak" ]]; then
    rm -f "${PAM_FILE}.sentry.bak"
    log_info "Removed PAM backup file."
fi

# --- 3. Asset Purge ---
log_info "Removing application binaries and working directories..."
rm -rf "$INSTALL_DIR"
rm -f "$BIN_DIR/sentry"
rm -f "$BIN_DIR/sentry-trigger"
rm -f /tmp/sentry.sock

log_info "Uninstallation complete. System restored to standard configuration."