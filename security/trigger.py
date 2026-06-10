#!/usr/bin/env python3

import socket
import sys

SOCKET_PATH = "/tmp/faceauth.sock"

def trigger():
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        # STRICT 3-SECOND TIMEOUT
        client.settimeout(3.0) 
        client.connect(SOCKET_PATH)
        
        client.sendall(b"WAKE")
        response = client.recv(1024).decode('utf-8')
        
        # ONLY a strict "1" grants root access
        if response == "1":
            sys.exit(0) # SUCCESS: Grant sudo
        else:
            sys.exit(1) # DENIED: Fallback to password
            
    except Exception:
        # THE FAIL-CLOSED LOCKDOWN
        # If the daemon is dead, the socket is broken, or the camera is unplugged,
        # we MUST return an error code so PAM falls back to the typed password.
        sys.exit(1)

if __name__ == "__main__":
    trigger()

