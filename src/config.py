import os

# 1. Base Directory Resolution
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. System Architecture
SOCKET_PATH = "/tmp/sentry.sock"

# 3. Vision & Intelligence Paths
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DETECTOR_MODEL = os.path.join(MODELS_DIR, 'face_detection_yunet_2023mar.onnx')
RECOGNIZER_MODEL = os.path.join(MODELS_DIR, 'face_recognition_sface_2021dec.onnx')
LIVENESS_MODEL = os.path.join(MODELS_DIR, 'minifasnet_v2.onnx')
BASELINE_PATH = os.path.join(BASE_DIR, 'user_baseline.npy')
AUTH_FILE = os.path.join(BASE_DIR, 'authorized.txt')

# 4. Hardware Constraints
CAMERA_DEVICE_ID = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# 5. Security Protocols
MATCH_THRESHOLD = 0.80

