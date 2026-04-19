import cv2
import socket
import pickle
import struct
from ultralytics import YOLO

# load YOLO model (runs on your PC)
model = YOLO("yolov8n.pt")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 9999))
server_socket.listen(1)

conn, addr = server_socket.accept()

data = b""
payload_size = struct.calcsize("Q")

while True:
    while len(data) < payload_size:
        packet = conn.recv(4096)
        if not packet:
            break
        data += packet

    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("Q", packed_msg_size)[0]

    while len(data) < msg_size:
        data += conn.recv(4096)

    frame_data = data[:msg_size]
    data = data[msg_size:]

    frame = pickle.loads(frame_data)

    # 🔥 YOLO inference happens HERE (on your PC)
    results = model(frame)

    annotated = results[0].plot()

    cv2.imshow("YOLO Detection", annotated)

    if cv2.waitKey(1) == 27:
        break