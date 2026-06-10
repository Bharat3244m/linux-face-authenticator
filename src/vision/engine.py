import cv2
import numpy as np
import time
import onnxruntime as ort
import os
import src.config as cf

class VisionEngine:
    def __init__(self):
        print("[*] Booting Universal ONNX Engine")

        # paths
        # base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # detector_path = os.path.join(base_dir, "models", "face_detection_yunet_2023mar.onnx")
        # recognizer_path = os.path.join(base_dir, "models", "face_recognition_sface_2021dec.onnx")

        if not os.path.exists(cf.DETECTOR_MODEL) or not os.path.exists(cf.RECOGNIZER_MODEL):
            raise FileNotFoundError("CRITICAL: ONNX models missing from src/models/")
        
        # 1. Initialize YuNet (Face Detection)
        self.detector = cv2.FaceDetectorYN.create(
            model=cf.DETECTOR_MODEL,
            config="",
            input_size=(cf.CAMERA_WIDTH, cf.CAMERA_HEIGHT),
            score_threshold=0.8,
            nms_threshold=0.3,
            top_k=1
        )

        # 2. Initialize MobileFaceNet (face Recognition)
        providers = [
            'CUDAExecutionProvider',
            'CPUExecutionProvider'
            'ROCMExecutionProvider'
            'OpenVINOExecutionProvider'
        ]
        self.recognizer = ort.InferenceSession(cf.RECOGNIZER_MODEL, providers=providers)
        print(f"[+] Inference successfully bound to: {self.recognizer.get_providers()[0]}")
    
    def get_embedding(self, frame):
        # takes raw frame and convert it to 512D vector 
        height, width, _ = frame.shape
        self.detector.setInputSize((width, height))
        start_time = time.perf_counter()

        # 1. Detect
        _, faces = self.detector.detect(frame)
        if faces is None:
            return None, 0
        
        face = faces[0]
        x, y, w, h = int(face[0]), int(face[1]), int(face[2]), int(face[3])
        x, y = max(0, x), max(0, y)
        x_end, y_end = min(width, x + w), min(height, y + h)

        # 2. Isolate and Preprocess
        face_crop = frame[y:y_end, x:x_end]
        if face_crop.size == 0:
            return None, 0
        
        face_crop = cv2.resize(face_crop, (112, 112))
        face_crop = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
        
        blob = (face_crop.astype(np.float32) - 127.5) / 127.5
        blob = np.transpose(blob, (2, 0, 1))
        blob = np.expand_dims(blob, axis=0)

        input_name = self.recognizer.get_inputs()[0].name
        embedding = self.recognizer.run(None, {input_name: blob})[0][0]
        
        embedding = embedding / np.linalg.norm(embedding)

        latency = (time.perf_counter() - start_time) * 1000
        return embedding, latency
    



