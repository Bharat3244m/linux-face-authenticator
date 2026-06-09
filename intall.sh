#!/bin/bash
# install.sh

# 1. Root Check
if [ "$EUID" -ne 0 ]; then
  echo "[-] CRITICAL: Please run the installer with sudo."
  exit 1
fi

echo "[*] Initializing Deployment Engine..."
INSTALL_DIR="/opt/faceauth-universal"

# 2. Build the System Directory
echo "[*] Creating secure directory at $INSTALL_DIR..."
mkdir -p $INSTALL_DIR
cp -r src/ $INSTALL_DIR/
cp requirements.txt $INSTALL_DIR/

# 3. Compile the Isolated Sandbox
echo "[*] Building isolated Python environment..."
apt-get install -y python3-venv python3-pip
python3 -m venv $INSTALL_DIR/.venv
$INSTALL_DIR/.venv/bin/pip install --upgrade pip
$INSTALL_DIR/.venv/bin/pip install -r $INSTALL_DIR/requirements.txt

# 4. Deploy the Security Bridge (PAM Trigger)
echo "[*] Deploying PAM Trigger..."
cp security/trigger.py /usr/local/bin/faceauth-trigger
chown root:root /usr/local/bin/faceauth-trigger
chmod 755 /usr/local/bin/faceauth-trigger

# 5. Inject into the Linux Kernel (Safely)
echo "[*] Injecting into /etc/pam.d/sudo..."
PAM_FILE="/etc/pam.d/sudo"
PAM_RULE="auth sufficient pam_exec.so quiet /usr/local/bin/faceauth-trigger"

# Check if the rule already exists to prevent duplicate entries
if grep -q "faceauth-trigger" "$PAM_FILE"; then
    echo "[+] PAM rule already exists. Skipping injection."
else
    # Insert the rule right after the first line (usually the header)
    sed -i "1 a\\$PAM_RULE" "$PAM_FILE"
    echo "[+] PAM rule successfully injected."
fi

# 6. Ignite the Background Sentry
echo "[*] Registering systemd daemon..."
cp systemd/faceauth.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable faceauth.service
systemctl restart faceauth.service

echo "\n[SUCCESS] Universal Face Authentication is live."
echo "[*] Type 'sudo systemctl status faceauth.service' to verify the daemon."