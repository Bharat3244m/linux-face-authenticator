import cv2 

class CameraPipeline:
    def __init__(self, device_id=0):
        self.cap = cv2.VideoCapture(device_id, cv2.CAP_V4L2)

        if not self.cap.isOpened():
            raise RuntimeError("CRITICAL: Cannot bind to /dev/video0. Is the camera in use?")
        
        # optimize the hardware buffer to prevent frame lag
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) # discard the old frames instantly

    
    def get_frame(self):
        ret, frame = self.cap.read() # reads the most recent frame 
        if not ret:
            return None
        return frame
    
    def release(self):
        self.cap.release() # unmounts the webcam safely 