"""Python-Socket client"""

print("\n############################## %s ##################################\n" %(__doc__))

import socket
import time

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

try:
    sock.connect((socket.gethostname(), 8090))

    buf = bytes([1, 2, 3, 4]) #b"Welcome!"

    while True:
        try:
            size = sock.send(buf)
            print("send:", buf[0:size])

            buf = sock.recv(1024)

            if not buf:
                print("connection lost")
                break;

            print("recv:", buf)

            print()
        except Exception as e:
            print(e)
            break;

        time.sleep(1)
except Exception as e:
    print("connect error:", e)

sock.close()
