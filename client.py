import socket
import time

mainsocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
mainsocket.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
mainsocket.connect(("localhost",12424))

run = True
while run:
    msg = "test"
    mainsocket.send(msg.encode())