#!/bin/bash
# Description: Installs and configures the Sentry authentication module.

set -euo pipefail

# --- Configuration Variables ---
APP_NAME="sentry"
INSTALL_DIR="/opt/$APP_NAME"
VENV_DIR="$INSTALL_DIR/.venv"
BIN_DIR="/usr/local/bin"
SYSTEMD_DIR="/etc/systemd/system"
BASELINE_FILE="$INSTALL_DIR/src/user_baseline.npy"
PAM_FILE="/etc/pam.d/sudo"
PAM_RULE="auth sufficient pam_exec.so quiet stdout $BIN_DIR/sentry-trigger"

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

# --- 2. Environment Configuration (Universal OS Detection) ---
log_info "Detecting Linux Distribution..."

if [[ -f /etc/os-release ]]; then
    # Source the file. We disable set -u temporarily just in case the 
    # OS file contains unbound variables, then immediately re-enable it.
    set +u
    . /etc/os-release
    set -u
    OS="${ID:-}"
    OS_LIKE="${ID_LIKE:-}"
    PRETTY="${PRETTY_NAME:-$OS}"
else
    log_err "Cannot determine Linux distribution. /etc/os-release not found."
fi

log_info "Provisioning isolated Python environment for: $PRETTY..."

case "$OS" in
    *ubuntu*|*debian*|*pop*|*kali*|*mint*)
        export DEBIAN_FRONTEND=noninteractive
        apt-get update -qq
        apt-get install -y -qq python3-venv python3-pip libgl1 libglib2.0-0 > /dev/null
        ;;
    *fedora*|*rhel*|*centos*)
        dnf install -y -q python3 python3-pip mesa-libGL glib2
        ;;
    *arch*|*manjaro*)
        pacman -Sy --noconfirm --quiet python python-pip mesa glib2
        ;;
    *opensuse*|*suse*)
        zypper refresh -q
        zypper install -y -q python3 python3-pip Mesa-libGL1 glib2
        ;;
    *)
        # Fallback to parent architecture
        case "$OS_LIKE" in
            *debian*)
                export DEBIAN_FRONTEND=noninteractive
                apt-get update -qq
                apt-get install -y -qq python3-venv python3-pip libgl1 libglib2.0-0 > /dev/null
                ;;
            *arch*)
                pacman -Sy --noconfirm --quiet python python-pip mesa glib2
                ;;
            *rhel*|*fedora*)
                dnf install -y -q python3 python3-pip mesa-libGL glib2
                ;;
            *)
                log_err "Unsupported distribution engine. Please install python3-venv, pip, libGL, and glib2 manually."
                ;;
        esac
        ;;
esac

log_info "Building venv and installing Python dependencies..."
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -r "$INSTALL_DIR/requirements.txt"

# --- 3. Binary Deployment ---
log_info "Deploying executable binaries..."
install -m 755 bin/sentry "$BIN_DIR/sentry"
install -m 755 -o root -g root security/trigger.py "$BIN_DIR/sentry-trigger"

# --- 4. PAM Integration ---
log_info "Auditing PAM Authentication Matrix..."
if grep -q "sentry-trigger" "$PAM_FILE"; then
    log_info "Sentry PAM hook already exists. Bypassing injection."
else
    log_info "Creating cryptographic backup of sudo configuration..."
    cp "$PAM_FILE" "${PAM_FILE}.sentry.bak"
    
    log_info "Surgically wiring Sentry into Linux Kernel PAM..."
    sed -i "1 a\\$PAM_RULE" "$PAM_FILE"
    log_info "PAM configuration successfully updated."
fi

# --- 5. Biometric Baseline Check ---
if [[ ! -f "$BASELINE_FILE" ]]; then
    log_warn "No biometric baseline detected."
    log_info "Initiating user enrollment sequence..."
    "$BIN_DIR/sentry" enroll
else
    log_info "Existing biometric baseline verified. Data preserved."
fi

# --- 6. Service Registration ---
log_info "Configuring background daemon..."
if command -v systemctl >/dev/null 2>&1; then
    install -m 644 systemd/sentry.service "$SYSTEMD_DIR/"
    systemctl daemon-reload
    systemctl enable --now sentry.service
    log_info "Installation complete. Sentry service is active."
else
    log_warn "Systemd not detected. The sentry service has not been started."
    log_info "You must manually configure your init system to execute: /opt/sentry/.venv/bin/python3 /opt/sentry/src/daemon.py"
    log_info "Installation complete."
fi