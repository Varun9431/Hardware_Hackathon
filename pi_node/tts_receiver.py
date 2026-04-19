
import socket
import os

HOST = "0.0.0.0"
PORT = 5001

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1)

print(f"Listening for TTS messages on port {PORT}...")

while True:
    conn, addr = server.accept()
    print(f"Connected by {addr}")

    with conn:
        buffer = b""
        while True:
            data = conn.recv(1024)
            if not data:
                break
            buffer += data

            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                message = line.decode("utf-8", errors="ignore").strip()
                if message:
                    print("Speaking:", message)
                    os.system(f'espeak "{message}"')
