import cv2 
import config as cf

class CameraPipeline:
    def __init__(self, device_id=cf.CAMERA_DEVICE_ID):
        self.cap = cv2.VideoCapture(device_id, cv2.CAP_V4L2)

        if not self.cap.isOpened():
            raise RuntimeError("CRITICAL: Cannot bind to /dev/video0. Is the camera in use?")
        
        # optimize the hardware buffer to prevent frame lag
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, cf.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cf.CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) # discard the old frames instantly

    
    def get_frame(self):
        ret, frame = self.cap.read() # reads the most recent frame 
        if not ret:
            return None
        return frame
    
    def release(self):
        self.cap.release() # unmounts the webcam safely 