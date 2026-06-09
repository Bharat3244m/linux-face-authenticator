#!/bin/bash
# uninstall.sh

if [ "$EUID" -ne 0 ]; then
  echo "[-] CRITICAL: Please run the uninstaller with sudo."
  exit 1
fi

echo "[*] Initiating Uninstallation Protocol..."

# 1. Kill the Daemon
systemctl stop faceauth.service
systemctl disable faceauth.service
rm -f /etc/systemd/system/faceauth.service
systemctl daemon-reload

# 2. Remove the PAM Injection (The most important step)
echo "[*] Restoring standard /etc/pam.d/sudo configuration..."
sed -i '/faceauth-trigger/d' /etc/pam.d/sudo

# 3. Purge the Files
rm -rf /opt/faceauth-universal
rm -f /usr/local/bin/faceauth-trigger
rm -f /tmp/faceauth.sock

echo "[SUCCESS] System restored to factory password authentication."