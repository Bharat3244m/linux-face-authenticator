#!/usr/bin/env python3

import socket
import sys
import os

SOCKET_PATH = "/tmp/sentry.sock"
AUTH_FILE = "/opt/sentry/src/authorized.txt"

def trigger():
    try:
        # 1. Read the dynamically bound user
        if not os.path.exists(AUTH_FILE):
            sys.exit(1) # Fail-closed if no one is enrolled
            
        with open(AUTH_FILE, "r") as f:
            authorized_user = f.read().strip()

        # 2. Grab the Linux PAM Context Variables
        pam_user = os.environ.get('PAM_USER', '')       # target account
        pam_ruser = os.environ.get('PAM_RUSER', '')     # requesting account

        # 3. The Privilege Escalation Defense
        if authorized_user not in [pam_user, pam_ruser]:
            sys.exit(1)

        # 4. Trigger the Daemon
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.settimeout(3.0) 
        client.connect(SOCKET_PATH)
        
        client.sendall(b"WAKE")
        response = client.recv(1024).decode('utf-8')
        
        if response == "1":
            sys.exit(0) 
        else:
            sys.exit(1) 
            
    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    trigger()