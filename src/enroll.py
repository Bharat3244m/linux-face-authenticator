import time
import os
import numpy as np
from vision.camera import CameraPipeline
from vision.engine import VisionEngine

BASELINE_PATH =os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_baseline.npy')

def enroll_user():
    print("\n[*] Initializing enrollment protocol...")
    cam = CameraPipeline()
    engine = VisionEngine()

    embeddings = []
    required_samples = 5

    print(f"\n[*] Need {required_samples} clean captures. Look at the camera...")

    try:
        # throw away 10 initial frames for the camera to adjust the exposure
        for _ in range(10):
            cam.get_frame()
            time.sleep(0.1)

        while len(embeddings) < required_samples:
            frame = cam.get_frame()
            if frame is None:
                continue

            embedding, _ = engine.get_embedding(frame)

            if embedding is not None:
                embeddings.append(embedding)
                print(f"[+] Capture {len(embeddings)}/{required_samples} complete.")
                time.sleep(0.5)
            else:
                print("[-] No face detected in the frame. adjust lighting or posistion...")
                time.sleep(1)
            
        print("\n[*] Compiling biometric master key")

        master_embedding = np.mean(embeddings, axis=0)
        master_embedding = master_embedding / np.linalg.norm(master_embedding)

        np.save(BASELINE_PATH, master_embedding)

        print(f"[SUCCESS] Master key saved to: {BASELINE_PATH}")
        print("[*] Your are now securely enrolled in the system.")
    
    finally:
        print("[*] Releasing hardware interrupts...")
        cam.release()

# if __name__ == "__main__":
#     enroll_user()