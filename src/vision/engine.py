import cv2
import numpy as np
import time
import os
import config as cf

class VisionEngine:
    def __init__(self):
        print("[*] Booting SFace ONNX Engine...")

        if not os.path.exists(cf.DETECTOR_MODEL) or not os.path.exists(cf.RECOGNIZER_MODEL):
            raise FileNotFoundError("CRITICAL: ONNX models missing from src/models/")
        
        # 1. Initialize YuNet (Face Detection & Landmarks)
        self.detector = cv2.FaceDetectorYN.create(
            model=cf.DETECTOR_MODEL,
            config="",
            input_size=(cf.CAMERA_WIDTH, cf.CAMERA_HEIGHT),
            score_threshold=0.8,
            nms_threshold=0.3,
            top_k=1
        )

        # 2. Initialize SFace (Identity & Alignment Wrapper)
        # This completely replaces the manual 'onnxruntime' block
        self.recognizer = cv2.FaceRecognizerSF.create(
            model=cf.RECOGNIZER_MODEL,
            config=""
        )
        print("[+] Inference engine bound to OpenCV DNN")
    
    def get_embedding(self, frame):
        height, width, _ = frame.shape
        self.detector.setInputSize((width, height))
        start_time = time.perf_counter()

        # 1. Detect Face and Landmarks
        _, faces = self.detector.detect(frame)
        if faces is None:
            return None, 0
        
        face = faces[0]

        # 2. THE FIX: Affine Alignment
        # Automatically warps, rotates, and crops to a perfect 112x112 standard
        aligned_face = self.recognizer.alignCrop(frame, face)
        
        # 3. Extract Identity Vector
        embedding = self.recognizer.feature(aligned_face)
        
        # OpenCV returns a 2D array, grab the raw 1D vector
        embedding = embedding[0]
        
        # 4. Normalize to prevent exploding dot products
        embedding = embedding / np.linalg.norm(embedding)

        latency = (time.perf_counter() - start_time) * 1000
        return embedding, latency