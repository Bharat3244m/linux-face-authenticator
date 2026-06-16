# Sentry: Dual-Gate Linux Biometric Daemon

A fast, secure, and distribution-agnostic biometric authentication system for Linux.

Sentry intercepts PAM (Pluggable Authentication Modules) requests—such as `sudo` verification or lock-screen logins—and uses your webcam to verify your identity through a high-performance computer vision pipeline. Built with a strict Fail-Closed philosophy, it isolates all biometric data within a protected root vault.

---

## 🏗 System Architecture

Standard facial recognition systems can be bypassed by 2D photographs or fail if you sit at a different angle. Sentry addresses both vulnerabilities using a sequential, dual-gate neural network pipeline:

* **Gate 1: Liveness Analysis (MiniFASNet)** – Analyzes the 3D structural depth and environmental context of the frame. It instantly terminates authentication if it detects a digital screen, a printed photograph, or a mask.
* **Gate 2: Alignment & Identity (YuNet + SFace)** – Isolates 5 facial landmarks to execute an Affine Transformation, mathematically rotating and cropping the face into a uniform 112x112 matrix. It then extracts a 128-dimensional vector to verify your identity using Cosine Similarity.

---

## ✨ Core Features

* **Dynamic Security Binding** – Automatically binds authentication privileges to the specific local account invoking enrollment, mitigating local privilege escalation risks.
* **The Root Vault** – Core binaries, AI models, and your identity matrix reside securely in `/opt/sentry/`, accessible only by root.
* **Fail-Closed Operation** – If a camera fault occurs, communication breaks, or verification fails, the system instantly falls back to standard password entry.

---

## 🚀 Installation

Ensure an operational RGB webcam is connected to your machine before proceeding.

### Option 1: Ubuntu / Debian-based Systems (Via APT Repository)
This is the recommended path for Debian-family systems, allowing for seamless automated updates.

```bash
# 1. Add the repository public signing key
curl -s --compressed "https://Bharat3244m.github.io/sentry-ppa/KEY.gpg" | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/sentry-ppa.gpg >/dev/null

# 2. Add the repository source
echo "deb [signed-by=/etc/apt/trusted.gpg.d/sentry-ppa.gpg] https://Bharat3244m.github.io/sentry-ppa ./" | sudo tee /etc/apt/sources.list.d/sentry.list

# 3. Synchronize package lists and install
sudo apt update
sudo apt install sentry
```


### Option 2: Universal Linux (Via Source Tarball)

For Arch Linux, Fedora, openSUSE, or minimal installations, use the universal deployment engine:

```bash
# 1. Extract the release matrix
tar -xzf sentry_1.0.0_source.tar.gz
cd sentry

# 2. Execute the automated installer
sudo ./install.sh
```

*The installer automatically detects your package manager, provisions underlying graphical dependencies (`libgl1`, `glib2`, `mesa`), builds an isolated virtual environment, and registers the system daemon.*

---

## 🧬 Biometric Enrollment

To map your facial structure, you must capture a Multi-Vector Identity Matrix. Sentry will prompt you to position your face across 6 distinct angles for robust accuracy.

```bash
sudo sentry enroll
```

---

## 🛡️ Usage & Testing

Once enrolled, the module handles authentication silently in the background. Open a new terminal session and execute any privileged action to trigger verification:

```bash
sudo apt update
```

### Testing the Authentication Loop

Linux caches successful `sudo` credentials for 15 minutes by default, bypassing PAM checks during that window. To clear this cache and forcefully test the biometric authentication mechanism, use the `-k` flag:

```bash
sudo -k && sudo echo "Sentry Verification Active"
```

---

## 🧹 Complete Uninstallation

The uninstallation pipeline completely tears down background processes, handles PAM cleanup, and purges all local assets to return your operating system to a pristine state.

### If Installed via APT (Option 1):

```bash
sudo apt purge sentry
sudo rm /etc/apt/sources.list.d/sentry.list
sudo rm /etc/apt/trusted.gpg.d/sentry-ppa.gpg
```

### If Installed via Tarball (Option 2):

Navigate to your extracted source folder and run:

```bash
sudo ./uninstall.sh
```

---

## Dependencies & Acknowledgments

Built using `onnxruntime` and the OpenCV DNN core module.

* **Face Detection**: [YuNet](https://github.com/opencv/opencv_zoo/tree/master/models/face_detection_yunet)
* **Face Recognition**: [SFace](https://github.com/opencv/opencv_zoo/tree/master/models/face_recognition_sface)
* **Anti-Spoofing / Liveness**: [MiniFASNet](https://github.com/minivision-ai/Silent-Face-Anti-Spoofing)
