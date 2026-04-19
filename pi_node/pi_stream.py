import cv2
import socket
import pickle
import struct

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("172.20.10.3", 9999))

cap = cv2.VideoCapture(0)

while True:
	ret, frame = cap.read()
	if not ret:
		break

	data= pickle.dumps(frame)
	message = struct.pack("Q", len(data)) + data

	client_socket.sendall(message)
