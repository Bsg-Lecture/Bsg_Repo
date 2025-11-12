#!/usr/bin/env python3
import socket, json, time, collections
IDS_PORT = 5010
WINDOW_S = 2.0
THRESH = 5
def server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', IDS_PORT))
    buf = collections.deque()
    print("[IDS] listening on UDP", IDS_PORT)
    while True:
        data, addr = sock.recvfrom(2048)
        msg = json.loads(data.decode())
        t = time.time()
        buf.append(t)
        while buf and (t - buf[0]) > WINDOW_S:
            buf.popleft()
        if len(buf) >= THRESH:
            print(f"[ALERT][CORRELATED_STARTS] count={len(buf)} window={WINDOW_S}s at {t}")
if __name__ == "__main__":
    server()
