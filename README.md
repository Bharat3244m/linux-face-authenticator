# Linux Face Authentication Sentry

A distribution-agnostic, military-grade biometric security daemon for Linux.

This system intercepts Linux Kernel PAM (Pluggable Authentication Modules) requests—such as sudo—and executes a high-performance, dual-gate computer vision pipeline to verify your identity using a standard RGB webcam. Built with a strict Fail-Closed philosophy, it operates entirely within a secure root vault, isolating biometric matrices from user space.

## 🏗 System Architecture

Standard face recognition systems are vulnerable to two major flaws: spatial misalignment (failing when you sit differently) and 2D spoofing (passing when shown a photograph). This Sentry solves both using a specialized Dual-Gate ONNX neural network pipeline:

### Gate 1: The Liveness Gatekeeper (MiniFASNet)

- Captures a 2.7x contextually expanded frame.
- Evaluates the 3D depth and environmental context of the face.
- **Fail-Fast**: Instantly terminates the authentication process if it detects a digital screen, a paper photograph, or a 2D mask.

### Gate 2: The Identity Bouncer (SFace + YuNet)

- Uses YuNet to extract 5 precise facial landmarks (eyes, nose, mouth corners).
- Executes an Affine Transformation to mathematically rotate, scale, and crop the face to a perfect 112x112 upright matrix, completely stripping away posture and environmental variables.
- Extracts a 128-dimensional identity vector and calculates the Cosine Similarity against the securely stored biometric baseline.

## ✨ Core Features

- **Universal Deployment**: Uses a Makefile engine to dynamically provision an isolated Python environment (venv) and bind to system libraries without polluting the host OS.

- **The Root Vault**: All AI models, executable binaries, and the user's `user_baseline.npy` identity matrix are locked inside `/opt/faceauth/` and strictly owned by root. Malware running in user space cannot modify or delete the biometric data.

- **Fail-Closed Security**: If the webcam fails, the socket disconnects, or the mathematical threshold is not met, the PAM module instantly drops back to standard password authentication. You are never permanently locked out.

- **Zero-Latency Daemon**: The ONNX networks are kept loaded in active RAM via a background systemd service (`faceauth.service`), communicating with the PAM trigger over an ultra-fast UNIX domain socket (`/tmp/faceauth.sock`).

## 🚀 Installation

Ensure you have standard build tools and a working webcam connected.

Clone the repository:

```bash
git clone https://github.com/yourusername/linux-face-auth.git
cd linux-face-auth
```

Execute the Deployment Engine:

```bash
sudo make install
```

This will build the `/opt/faceauth/` vault, provision dependencies, patch your PAM configuration, and start the systemd daemon.

## 🧬 Biometric Enrollment

Once installed, you must capture your Multi-Vector Identity Matrix. The system will guide you through capturing 6 distinct facial poses to ensure high accuracy across different angles.

Because the vault is write-protected, this command must be run as root:

```bash
sudo faceauth enroll
```

## 🛡️ Usage & Testing

Once enrolled, the system works completely silently in the background. Open a new terminal and attempt to run a privileged command:

```bash
sudo apt update
```

### Testing the Security (The Sudo Cache Trap)

By default, Linux caches sudo credentials for 15 minutes. During this window, PAM is bypassed completely, and the camera will not turn on. To forcefully clear this cache and rigorously test the biometric system (or test spoofing attempts), use the `-k` flag:

```bash
sudo -k && sudo echo "Security Test"
```

## 🧹 Complete Uninstallation

In accordance with strict system engineering principles, the uninstaller leaves zero ghost files, orphaned processes, or broken symlinks. It restores your machine to a pristine, factory-default state.

```bash
sudo make uninstall
```

## Dependencies & Acknowledgments

Built using onnxruntime and OpenCV DNN module.

- **Face Detection**: [YuNet](https://github.com/opencv/opencv_zoo/tree/master/models/face_detection_yunet)
- **Face Recognition**: [SFace](https://github.com/opencv/opencv_zoo/tree/master/models/face_recognition_sface)
- **Anti-Spoofing / Liveness**: [MiniFASNet](https://github.com/minivision-ai/Silent-Face-Anti-Spoofing)