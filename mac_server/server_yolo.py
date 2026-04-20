import cv2
import time
import socket
import numpy as np
from ultralytics import YOLO

# --- Configuration ---
PI_IP = "172.20.10.2"
PI_PORT = 5001
STREAM_URL = f"tcp://{PI_IP}:8888"

CONF_THRESHOLD = 0.55
COOLDOWN = 2.0
PERCENT_TOLERANCE = 0.15 
WALL_PROXIMITY_THRESHOLD = 0.88 

# Classes: 0 is person. 
OBSTACLE_CLASSES = [56, 57, 59, 60, 61, 62, 63] 

# --- Initialization ---
model = YOLO("yolov8n-seg.pt")
cap = cv2.VideoCapture(STREAM_URL)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) 

if not cap.isOpened():
    print("Error: Could not open stream.")
    raise SystemExit

last_sent_time = 0
last_person_id = None
last_area = 0

def send_tts_message(text: str):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            s.connect((PI_IP, PI_PORT))
            s.sendall((text + "\n").encode("utf-8"))
    except:
        pass 

print("M3 Pro System Active. Camera Flip Enabled.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # --- 1. ORIENTATION FIX (180 Rotation) ---
    # This ensures "top" is sky and "bottom" is floor
    frame = cv2.rotate(frame, cv2.ROTATE_180)

    # --- 2. CROP WIDTH (Tunnel Vision) ---
    h, w = frame.shape[:2]
    left_cut = int(w * 0.20)
    right_cut = int(w * 0.80)
    frame = frame[:, left_cut:right_cut]
    h, w = frame.shape[:2]

    # --- 3. INFERENCE ---
    results = model.track(frame, imgsz=320, classes=[0]+OBSTACLE_CLASSES, verbose=False, persist=True)
    result = results[0]
    
    now = time.time()
    msg = None

    if result.boxes is not None:
        # --- 4. DYNAMIC OBSTACLE DETECTION ---
        if result.masks is not None:
            classes = result.boxes.cls.int().tolist()
            for i, cls_id in enumerate(classes):
                if cls_id in OBSTACLE_CLASSES:
                    mask_points = result.masks.xy[i]
                    if len(mask_points) > 0:
                        # lowest_y is now correctly the ground-side pixels
                        lowest_y = np.max(mask_points[:, 1])
                        
                        if lowest_y > (h * WALL_PROXIMITY_THRESHOLD):
                            if now - last_sent_time > COOLDOWN:
                                label = model.names[cls_id]
                                msg = f"{label} ahead"
                            break

        # --- 5. PERSON DISTANCE LOGIC ---
        if msg is None and result.boxes.id is not None:
            boxes = result.boxes.xyxy.tolist()
            ids = result.boxes.id.int().tolist()
            confs = result.boxes.conf.tolist()

            for i in range(len(ids)):
                if confs[i] >= CONF_THRESHOLD:
                    tid = ids[i]
                    curr_area = (boxes[i][2] - boxes[i][0]) * (boxes[i][3] - boxes[i][1])
                    
                    if now - last_sent_time > COOLDOWN:
                        if tid == last_person_id:
                            rel_change = (curr_area - last_area) / last_area if last_area > 0 else 0
                            if rel_change > PERCENT_TOLERANCE: msg = "person getting closer"
                            elif rel_change < -PERCENT_TOLERANCE: msg = "person moving away"
                            else: msg = "person at same distance"
                        else:
                            msg = "person ahead"
                        
                        last_person_id = tid
                        last_area = curr_area
                    break

    # --- 6. ACTIONS ---
    if msg:
        send_tts_message(msg)
        print(f"SENT: {msg}")
        last_sent_time = now

    cv2.imshow("M3 Pro AI Vision (Corrected)", result.plot())

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()