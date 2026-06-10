# Makefile for Face Authentication Sentry

.PHONY: help install uninstall clean

# Ensure 'help' is the default target if a user just types 'make'
.DEFAULT_GOAL := help

help:
	@echo "Face Auth System - Build & Deployment"
	@echo ""
	@echo "Commands:"
	@echo "  sudo make install    - Deploys the sandbox, systemd daemon, and PAM rule"
	@echo "  sudo make uninstall  - Safely removes all system hooks and daemon files"
	@echo "  make clean           - Removes local development sandbox (.venv) and caches"

install:
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "[-] CRITICAL: 'make install' must be run as root. Try 'sudo make install'."; \
		exit 1; \
	fi
	@echo "[*] Triggering deployment engine..."
	@chmod +x ./install.sh
	@./install.sh

uninstall:
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "[-] CRITICAL: 'make uninstall' must be run as root. Try 'sudo make uninstall'."; \
		exit 1; \
	fi
	@echo "[*] Triggering uninstall fail-safe..."
	@chmod +x ./uninstall.sh
	@./uninstall.sh

clean:
	@echo "[*] Purging local development caches..."
	@rm -rf .venv
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "[+] Clean complete."