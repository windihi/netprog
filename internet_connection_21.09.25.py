import socket
import time
import pygame as pg

WIDTH = 800
HEIGHT = 600

mainsocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
mainsocket.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
mainsocket.bind(("localhost",12424))
mainsocket.setblocking(False)
mainsocket.listen(5)
print("socket создан")

pg.init()
screen = pg.display.set_mode((WIDTH,HEIGHT))
pg.display.set_caption("bacteria")

players = []

run = True
while run:
    for event in pg.event.get():
        if event == pg.QUIT:
            run = False
        
    try:
        newsocket,addr = mainsocket.accept()
        print(newsocket,addr)
        newsocket.setblocking(False)
        players.append(newsocket)
    except BlockingIOError:
        pass

    for s in players:
        try:
            s.send("sync".encode())
        except:
            s.close()
            players.remove(s)
            print("socket закрыт")
    
    time.sleep(1)
pg.quit()