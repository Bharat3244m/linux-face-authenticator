import socket
import os
import time
import numpy as np
from vision.camera import CameraPipeline
from vision.engine import VisionEngine

SOCKET_PATH = "/tmp/faceauth.sock"
BASELINE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_baseline.npy')

MATCH_THRESHOLD = 0.99

def run_sentry():
    if not os.path.exists(BASELINE_PATH):
        print("[-] CRITICAL: No baseline found. Exiting.")
        return
    
    print("[*] Sentry Daemon initializing...")

    # 1. Load the baseline and neural network in ram permanently
    baseline = np.load(BASELINE_PATH)
    engine = VisionEngine()

    # 2. Bind the UNIX Socket
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    os.chmod(SOCKET_PATH, 0o666)
    server.listen(1)

    print(f"\n[*] Sentry locked. Listening for IPC triggers on {SOCKET_PATH}...")

    # 3. the Infinite sleep/wake loop
    while True:
        conn, addr = server.accept()
        try:
            data = conn.recv(1024)
            if data == b"WAKE":
                print("\n[*] trigger received. Engaging hardware...")
                cam = CameraPipeline()
                try:
                    for _ in range(5):
                        cam.get_frame()
                        time.sleep(0.05)
                    
                    frame = cam.get_frame()
                    if frame is not None:
                        embedding, _ = engine.get_embedding(frame)
                        if embedding is not None:
                            # Normalize the live webcam feed
                            embedding = embedding / np.linalg.norm(embedding)
                            
                            # Multiply the (128,) live face against the (6, 128) baseline matrix
                            scores = np.dot(baseline, embedding)
                            
                            # Grab the highest score out of the 6 angles
                            best_score = np.max(scores)
                            print(f"[STAT] Matrix Scores: {scores}")
                            print(f"[STAT] Best Match: {best_score:.4f}")
                            
                            # Send the binary response back through the socket
                            if best_score >= MATCH_THRESHOLD:
                                print("[SUCCESS] IDENTITY VERIFIED. UNLOCKING SYSTEM.")
                                conn.sendall(b"1")
                            else:
                                print("[!] STRANGER DETECTED. ACCESS DENIED.")
                                conn.sendall(b"0")
                        else:
                            print("[-] No face detected in frame. ACCESS DENIED.")
                            conn.sendall(b"0")
                    else:
                        print("[-] Camera hardware buffer failed.")
                        conn.sendall(b"0")
                finally:
                    cam.release()
                    print("[*] Hardware released. Sentry returning to sleep.")
        
        except Exception as e:
            print(f"[-] Daemon Error: {e}")
        
        finally:
            conn.close()

if __name__ == "__main__":
    run_sentry()