import socket
import time

mainsocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
mainsocket.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
mainsocket.bind(("localhost",12424))
mainsocket.setblocking(False)
mainsocket.listen(5)
print("socket создан")


players = []

run = True
while run:
    try:
        newsocket,addr = mainsocket.accept()
        print(newsocket,addr)
        newsocket.setblocking(False)
        players.append(newsocket)
    except BlockingIOError:
        pass
    
    try:
        for s in players:
            data = s.recv(1024).decode()
            print(data)
    except:
        pass
    
    time.sleep(1)