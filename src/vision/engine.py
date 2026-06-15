import cv2
import numpy as np
import time
import os
import config as cf
import onnxruntime as ort

class VisionEngine:
    def __init__(self):
        print("[*] Booting Dual-Gate Security Engine...")

        if not os.path.exists(cf.DETECTOR_MODEL) or not os.path.exists(cf.RECOGNIZER_MODEL):
            raise FileNotFoundError("CRITICAL: Vision models missing from src/models/")
        
        # 1. Initialize YuNet 
        self.detector = cv2.FaceDetectorYN.create(
            model=cf.DETECTOR_MODEL,
            config="",
            input_size=(cf.CAMERA_WIDTH, cf.CAMERA_HEIGHT),
            score_threshold=0.8,
            nms_threshold=0.3,
            top_k=1
        )

        # 2. Initialize GATE 1: MiniFASNet (Anti-Spoofing / Liveness)
        if not os.path.exists(cf.LIVENESS_MODEL):
            raise FileNotFoundError("CRITICAL: Liveness model missing. Cannot guarantee anti-spoofing.")
        self.liveness = ort.InferenceSession(cf.LIVENESS_MODEL, providers=['CPUExecutionProvider'])

        # 3. Initialize GATE 2: SFace (Identity / Affine Alignment)
        self.recognizer = cv2.FaceRecognizerSF.create(
            model=cf.RECOGNIZER_MODEL,
            config=""
        )
        print("[+] All Gates Online. Engine locked and loaded.")
    
    def get_embedding(self, frame):
        height, width, _ = frame.shape
        self.detector.setInputSize((width, height))
        start_time = time.perf_counter()

        _, faces = self.detector.detect(frame)
        if faces is None:
            return None, 0
        face = faces[0]

        # --- GATE 1: LIVENESS (Fail-Fast) ---
        x, y, w, h = int(face[0]), int(face[1]), int(face[2]), int(face[3])

        cx = x + w // 2    # Face center point
        cy = y + h // 2   

        side =  int(max(w, h) * 2.7)

        x1, y1 = max(0, cx - side // 2), max(0, cy - side // 2)
        x2, y2 = min(width, cx + w + side // 2), min(height, cy + h + side // 2)
        
        fas_crop = frame[y1:y2, x1:x2]
        if fas_crop.size == 0:
            return None, 0
        fas_crop = cv2.resize(fas_crop, (80, 80))
        blob = cv2.dnn.blobFromImage(fas_crop, 1.0, (80, 80), (0, 0, 0), swapRB=False, crop=False)
        
        input_name = self.liveness.get_inputs()[0].name
        
        # Run inference and grab the 1D array of the 3 class scores
        liveness_output = self.liveness.run(None, {input_name: blob})[0][0]
        
        # Print the raw brain activity to the logs for debugging
        print(f"[DEBUG] Liveness Vector: {liveness_output}")
        
        # Find which of the 3 classes has the highest confidence score
        best_class = np.argmax(liveness_output)
        
        # Class 1 is the ONLY valid 'Real Human' class. 
        # If it scores highest in Class 0 (Paper) or Class 2 (Screen), kill it.
        if best_class != 1:
            print(f"[!] GATE 1 KILLED: Spoof Detected (Class {best_class}). Aborting.")
            return None, (time.perf_counter() - start_time) * 1000
        else:
            print("[+] GATE 1 PASSED: Real pulse detected.")
        
        # --- GATE 2: IDENTITY (Affine Alignment) ---
        aligned_face = self.recognizer.alignCrop(frame, face)
        embedding = self.recognizer.feature(aligned_face)
        embedding = embedding[0]
        embedding = embedding / np.linalg.norm(embedding)

        latency = (time.perf_counter() - start_time) * 1000
        return embedding, latency