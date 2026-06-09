# src/verify.py
import numpy as np
import time
import os
from vision.camera import CameraPipeline
from vision.engine import VisionEngine

BASELINE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_baseline.npy')

# OpenCV's official research threshold for SFace is 0.363. 
# We are raising it to 0.5 to enforce strict security for root access.
MATCH_THRESHOLD = 0.999

def verify_user():
    if not os.path.exists(BASELINE_PATH):
        print("[-] CRITICAL: No baseline found. Run enroll.py first.")
        return

    print("[*] Loading biometric master key from disk...")
    baseline = np.load(BASELINE_PATH)

    cam = CameraPipeline()
    engine = VisionEngine()

    print("\n[*] SYSTEM ARMED. Look at the camera to authenticate...")
    
    try:
        # Throw away initial frames to let hardware auto-exposure settle
        for _ in range(5):
            cam.get_frame()
            time.sleep(0.1)

        frame = cam.get_frame()
        if frame is None:
            print("[-] Camera hardware buffer failed.")
            return

        # Generate the math vector for the current face
        embedding, latency = engine.get_embedding(frame)

        if embedding is None:
            print("\n[-] No face detected in frame. ACCESS DENIED.")
            return

        # The Core Security Math: Cosine Similarity (Dot Product)
        score = np.dot(embedding, baseline)
        
        print(f"\n[STAT] Hardware Latency: {latency:.2f} ms")
        print(f"[STAT] Cryptographic Match Score: {score:.4f} (Required: {MATCH_THRESHOLD})")

        # The Final Gatekeeper
        if score >= MATCH_THRESHOLD:
            print("\n[SUCCESS] IDENTITY VERIFIED. UNLOCKING SYSTEM.")
        else:
            print("\n[!] STRANGER DETECTED. ACCESS DENIED.")

    finally:
        cam.release()

if __name__ == "__main__":
    verify_user()