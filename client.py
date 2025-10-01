import socket
import time
import pygame as pg
import math

WIDTH = 800
HEIGHT = 600
CENTER = (WIDTH//2,HEIGHT//2)
radius = 50
ovec = (0,0)

mainsocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
mainsocket.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
mainsocket.connect(("localhost",12424))

pg.init()
screen = pg.display.set_mode((WIDTH,HEIGHT))
pg.display.set_caption("bacteria")

run = True
while run:
    for event in pg.event.get():
        if event == pg.QUIT:
            run = False
        if pg.mouse.get_focused():
            coords = pg.mouse.get_pos() 
            vecc = coords[0] - CENTER[0],coords[1] - CENTER[1]
            lenght = math.sqrt(vecc[0]**2 + vecc[1]**2)
            vecc = vecc[0]/lenght,vecc[1]/lenght
            if lenght <= radius:
                vecc = (0,0)
            if vecc != ovec:
                ovec = vecc
                mainsocket.send(f"<{vecc[0]},{vecc[1]}>".encode())
                print(f"<{vecc[0]},{vecc[1]}>")

    data = mainsocket.recv(1024).decode()
    print(data)
    screen.fill("grey")
    pg.draw.circle(screen,(255,0,0),CENTER,radius)
    pg.draw.line(screen,(0,0,0),CENTER,coords)
    pg.display.update()
pg.quit()


#каждый вектор имеет свои координаты формула - x = xконец - xначало у У также