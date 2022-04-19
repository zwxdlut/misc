#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Python-Socket server"""

print("\n############################## %s ##################################\n" %(__doc__))

import socket
 
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((socket.gethostname(), 8090))
sock.listen(5)

while True:
    conn, addr = sock.accept()
    print("connected address: %s" %(str(addr)))

    while True:
        try:
            buf = conn.recv(1024)

            if not buf:
                print("connection lost")
                break;

            print("recv:", buf)

            size = conn.send(buf)
            print("send:", buf[0:size])
            
            print()
        except Exception as e:
            print(e)
            break;

    conn.close()

sock.close()
