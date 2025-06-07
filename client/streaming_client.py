import socket
import threading
import tempfile
import cv2
import os
import time

SERVER_IP = input("Enter server IP: ").strip()
VIDEO_PORT = int(input("Enter server VIDEO port: ").strip())
CTRL_PORT = int(input("Enter server CTRL port: ").strip())
TEMP_VIDEO = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name

stop_flag = threading.Event()

def send_control(ctrl_sock):
    while not stop_flag.is_set():
        try:
            cmd = input("Enter command (p=play, t=pause, q=stop): ").strip()
            if stop_flag.is_set():
                break
            if cmd in ['p', 't', 'q']:
                ctrl_sock.sendall(cmd.encode())
                print(f"[CLIENT] Sent command: {cmd}")
                if cmd == 'q':
                    stop_flag.set()
                    break
        except Exception:
            break

def recv_video(video_sock):
    total_bytes = 0
    chunk_count = 0
    first_byte_time = None
    last_byte_time = None
    connect_time = time.time()  # 連線成功的時間
    startup_delay = None  # 啟動延遲時間

    with open(TEMP_VIDEO, "wb") as f:
        while not stop_flag.is_set():
            try:
                data = video_sock.recv(4096)
                if data:
                    if first_byte_time is None:
                        first_byte_time = time.time()
                        startup_delay = first_byte_time - connect_time
                        print(f"[CLIENT] Startup Delay: {startup_delay:.3f} seconds")
                    f.write(data)
                    total_bytes += len(data)
                    chunk_count += 1
                    print(f"[CLIENT] Received chunk {chunk_count}: {len(data)} bytes (Total: {total_bytes} bytes)")
                else:
                    last_byte_time = time.time()
                    break
            except Exception as e:
                print(f"[CLIENT] Video receive error: {e}")
                break
    print("[CLIENT] Video reception finished.")
    if first_byte_time and last_byte_time:
        total_transfer_time = last_byte_time - first_byte_time
        avg_throughput = total_bytes / total_transfer_time if total_transfer_time > 0 else 0
        print(f"[CLIENT] Startup Delay: {startup_delay:.3f} seconds")
        print(f"[CLIENT] Total Transfer Time: {total_transfer_time:.3f} seconds")
        print(f"[CLIENT] Average Throughput: {avg_throughput/1024:.2f} KB/s")
    stop_flag.set()

def main():
    video_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ctrl_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    video_sock.connect((SERVER_IP, VIDEO_PORT))
    ctrl_sock.connect((SERVER_IP, CTRL_PORT))
    print("[CLIENT] Connected to server (video & control)")

    t1 = threading.Thread(target=recv_video, args=(video_sock,))
    t2 = threading.Thread(target=send_control, args=(ctrl_sock,))
    t1.start()
    t2.start()
    t1.join()
    stop_flag.set()
    video_sock.close()
    ctrl_sock.close()
    print("[CLIENT] Connections closed.")

    # 播放影片
    cap = cv2.VideoCapture(TEMP_VIDEO)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow('Received Video', frame)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    os.remove(TEMP_VIDEO)

if __name__ == "__main__":
    main()