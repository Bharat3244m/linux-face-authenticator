#!/usr/bin/env python3

import socket
import sys

SOCKET_PATH = "/tmp/faceauth.sock"

def pam_auth():
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.settimeout(3.0)

        client.connect(SOCKET_PATH)
        client.sendall(b"WAKE")

        response = client.recv(1)
        client.close()

        if response == b"1":
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception:
        sys.exit(1)

