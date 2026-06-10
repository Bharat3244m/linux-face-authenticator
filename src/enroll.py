# src/enroll.py
import time
import os
import numpy as np
import src.config as cf
from vision.camera import CameraPipeline
from vision.engine import VisionEngine

def enroll_user():
    print("\n[*] Initializing Multi-Vector Enrollment Protocol...")
    cam = CameraPipeline()
    engine = VisionEngine()
    
    matrix = []
    
    # The exact 6-pose sequence you requested
    poses = [
        "FRONT FACE (1/2)", "FRONT FACE (2/2)",
        "LEFT FACE (1/2)", "LEFT FACE (2/2)",
        "RIGHT FACE (1/2)", "RIGHT FACE (2/2)"
    ]
    
    try:
        # Throw away initial frames for auto-exposure
        for _ in range(10):
            cam.get_frame()
            time.sleep(0.1)
            
        for pose in poses:
            print(f"\n[*] Please position: {pose}")
            time.sleep(1.5) # Give you time to move your head
            
            captured = False
            while not captured:
                frame = cam.get_frame()
                if frame is None:
                    continue
                    
                embedding, _ = engine.get_embedding(frame)
                
                if embedding is not None:
                    # Normalize the individual vector before adding to matrix
                    normalized_vector = embedding / np.linalg.norm(embedding)
                    matrix.append(normalized_vector)
                    print(f"[+] Capture successful.")
                    captured = True
                    time.sleep(0.5)
                else:
                    print("[-] Face lost. Adjust angle slightly...")
                    time.sleep(1)
                
        print("\n[*] Compiling 6-Pose Biometric Matrix...")
        
        # Convert list of 6 vectors into a strict (6, 128) NumPy Matrix
        master_matrix = np.array(matrix)
        
        # Save the matrix to disk
        np.save(cf.BASELINE_PATH, master_matrix)
        
        print(f"[SUCCESS] Matrix saved. Dimensions: {master_matrix.shape}")
        print("[*] Multi-pose authentication is now locked in.")
        
    finally:
        cam.release()

if __name__ == "__main__":
    enroll_user()