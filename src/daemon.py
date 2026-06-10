import socket
import os
import time
import numpy as np
import config as cf
from vision.camera import CameraPipeline
from vision.engine import VisionEngine


def run_sentry():
    if not os.path.exists(cf.BASELINE_PATH):
        print("[-] CRITICAL: No baseline found. Exiting.")
        return
    
    print("[*] Sentry Daemon initializing...")

    # 1. Load the baseline and neural network in ram permanently
    baseline = np.load(cf.BASELINE_PATH)
    engine = VisionEngine()

    # 2. Bind the UNIX Socket
    if os.path.exists(cf.SOCKET_PATH):
        os.remove(cf.SOCKET_PATH)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(cf.SOCKET_PATH)
    os.chmod(cf.SOCKET_PATH, 0o666)
    server.listen(1)

    print(f"\n[*] Sentry locked. Listening for IPC triggers on {cf.SOCKET_PATH}...")

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
                        # --- CORE VERIFICATION LOGIC ---
                            embedding, latency = engine.get_embedding(frame)
                            
                            # 1. Null Check (No face or spoof detected)
                            if embedding is None:
                                print(f"[!] No face / Spoof detected. Aborting.")
                                conn.sendall(b"0")
                                break 
                            
                            # 2. Math Check
                            try:
                                embedding = embedding / np.linalg.norm(embedding)
                                scores = np.dot(baseline, embedding)
                                best_score = np.max(scores)
                                
                                print(f"[STAT] Math Score: {best_score:.4f}")
                                
                                # HARDCODED FAIL-CLOSED GATE
                                if best_score >= 0.65:
                                    print("[+] Identity Confirmed. Unlocking PAM.")
                                    conn.sendall(b"1")
                                else:
                                    print(f"[-] Intruder Rejected. Score too low.")
                                    conn.sendall(b"0")
                            except Exception as e:
                                print(f"[CRITICAL] Math failure: {e}")
                                conn.sendall(b"0") # Fail-closed on any error
                            
                            break # Always break after one complete check
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