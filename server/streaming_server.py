import socket
import threading
import os
import argparse
import time

VIDEO_FILE = "sample.mp4"
CHUNK_SIZE = 4096

client_states = {}
lock = threading.Lock()

def handle_control(conn, addr):
    global client_states
    try:
        while True:
            cmd = conn.recv(1024).decode().strip()
            if not cmd:
                break
            with lock:
                if cmd == 'p':
                    client_states[addr]['state'] = 'playing'
                    print(f"[SERVER] {addr} PLAY received. State=PLAYING")
                elif cmd == 't':
                    client_states[addr]['state'] = 'paused'
                    print(f"[SERVER] {addr} PAUSE received. State=PAUSED")
                elif cmd == 'q':
                    client_states[addr]['state'] = 'stopped'
                    print(f"[SERVER] {addr} STOP received. State=STOPPED")
                    break
    except Exception as e:
        print(f"[SERVER] Control connection error: {e}")
    finally:
        conn.close()
        print(f"[SERVER] Control connection with {addr} closed.")

def handle_video(conn, addr, delay):
    global client_states
    try:
        with open(VIDEO_FILE, "rb") as f:
            while True:
                with lock:
                    state = client_states[addr]['state']
                if state == 'playing':
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    try:
                        conn.sendall(chunk)
                        print(f"[SERVER] Sent chunk to {addr}: {len(chunk)} bytes")
                    except:
                        break
                    if delay > 0:
                        time.sleep(delay)
                elif state == 'paused':
                    time.sleep(0.1)
                elif state == 'stopped':
                    break
        print(f"[SERVER] Video streaming to {addr} finished.")
    except Exception as e:
        print(f"[SERVER] Video connection error: {e}")
    finally:
        conn.close()
        with lock:
            client_states.pop(addr, None)
        print(f"[SERVER] Video connection with {addr} closed.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--delay', type=float, default=0.0, help='Delay (in seconds) between sending chunks')
    args = parser.parse_args()
    delay = args.delay

    # 1. 檢查影片檔案
    if not os.path.exists(VIDEO_FILE):
        print(f"[SERVER] Error: {VIDEO_FILE} not found.")
        return
    print(f"[SERVER] Found video file: {VIDEO_FILE}")

    # 2. 監聽兩個 port
    video_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ctrl_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    video_sock.bind(('', 0))
    ctrl_sock.bind(('', 0))
    video_sock.listen(5)
    ctrl_sock.listen(5)
    video_port = video_sock.getsockname()[1]
    ctrl_port = ctrl_sock.getsockname()[1]
    print(f"[SERVER] Listening on VIDEO port {video_port}, CTRL port {ctrl_port} (delay={delay}s)")

    while True:
        print("[SERVER] Waiting for video connection...")
        v_conn, v_addr = video_sock.accept()
        print(f"[SERVER] Client {v_addr} connected (video)")
        print("[SERVER] Waiting for control connection from same client...")
        c_conn, c_addr = ctrl_sock.accept()
        print(f"[SERVER] Client {c_addr} connected (control)")

        # 初始化狀態為 paused
        with lock:
            client_states[v_addr] = {'state': 'paused'}

        # 啟動控制與資料 thread
        threading.Thread(target=handle_control, args=(c_conn, v_addr), daemon=True).start()
        threading.Thread(target=handle_video, args=(v_conn, v_addr, delay), daemon=True).start()

if __name__ == "__main__":
    main()