# Makefile for Face Authentication Sentry

.PHONY: help install uninstall clean tarball

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
	@chmod +x scripts/install.sh
	@scripts/install.sh

uninstall:
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "[-] CRITICAL: 'make uninstall' must be run as root. Try 'sudo make uninstall'."; \
		exit 1; \
	fi
	@echo "[*] Triggering uninstall fail-safe..."
	@chmod +x scripts/uninstall.sh
	@scripts/uninstall.sh

clean:
	@echo "[*] Purging local development caches..."
	@rm -rf .venv __pycache__/ *.deb *.tar.gz
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "[+] Clean complete."

tarball:
	@echo "Building universal source tarball..."
	mkdir -p build/sentry
	cp -r src/ bin/ security/ systemd/ requirements.txt scripts/* build/sentry/
	tar -czvf sentry_1.0.0_source.tar.gz -C build sentry/
	rm -rf build/
	@echo "Tarball built successfully."
