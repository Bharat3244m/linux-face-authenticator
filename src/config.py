import os

# 1. Base Directory Resolution
# This ensures paths work perfectly whether you are testing in your local
# dev folder or running as a background service from /opt/faceauth-universal/src/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. System Architecture
# The location of the virtual mailbox in the Linux RAM
SOCKET_PATH = "/tmp/faceauth.sock"

# 3. Vision & Intelligence Paths
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DETECTOR_MODEL = os.path.join(MODELS_DIR, 'face_detection_yunet_2023mar.onnx')
RECOGNIZER_MODEL = os.path.join(MODELS_DIR, 'face_recognition_sface_2021dec.onnx')
LIVENESS_MODEL = os.path.join(MODELS_DIR, 'minifasnet_v2.onnx')
BASELINE_PATH = os.path.join(BASE_DIR, 'user_baseline.npy')

# 4. Hardware Constraints
# Change this if you plug in an external USB webcam (usually 1 or 2)
CAMERA_DEVICE_ID = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# 5. Security Protocols
# Cosine Similarity Threshold (0.0 to 1.0)
# - 0.363 is OpenCV's baseline research recommendation.
# - 0.900+ is highly secure root-level protection.
MATCH_THRESHOLD = 0.80

