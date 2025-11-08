import socket
import pygame as pg
import math
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox

WIDTH = 800
HEIGHT = 600
CENTER = (WIDTH//2,HEIGHT//2)
NAME = None
radius = 50
ovec = (0,0)

def check_and_login():
    global NAME,COLOR
    NAME = entry.get()
    COLOR = combb.get()
    if NAME != "" and COLOR != "":
        root.destroy()
    else:
        tkinter.messagebox.showerror("Ошибка","Выберите имя и Цвет")

def find_visible_players(data):
    first = None
    for num,sign in enumerate(data):
        if sign == "<":
            first = num
        if sign == ">" and first is not None:
            second = num
            res = data[first+1:second]
            return res    
    return ""   

root = tk.Tk()
root.title("Вход")
root.geometry("400x400")
root["bg"] = "grey"

COLORS = ['Maroon', 'DarkRed', 'FireBrick', 'Red', 'Salmon', 'Tomato', 'Coral', 'OrangeRed',
           'Chocolate', 'SandyBrown', 'DarkOrange', 'Orange', 'DarkGoldenrod', 'Goldenrod', 'Gold',
             'Olive', 'Yellow', 'YellowGreen', 'GreenYellow', 'Chartreuse', 'LawnGreen', 'Green',
               'Lime', 'Lime Green', 'SpringGreen', 'MediumSpringGreen', 'Turquoise',
                 'LightSeaGreen', 'MediumTurquoise', 'Teal', 'DarkCyan', 'Aqua', 'Cyan', 'Dark Turquoise',
                   'DeepSkyBlue', 'DodgerBlue', 'RoyalBlue', 'Navy', 'DarkBlue', 'MediumBlue']
COLOR = tk.StringVar(value=COLORS[0])

entry = ttk.Entry(root)
entry.pack()
combb = ttk.Combobox(root,values=COLORS,textvariable=COLOR)
combb.pack()
cbtn = ttk.Button(root,text="Вход",command=check_and_login)
cbtn.pack()

root.mainloop()


mainsocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
mainsocket.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
mainsocket.connect(("localhost",12424))

mainsocket.send(f"{NAME},{COLOR}".encode())

pg.init()
screen = pg.display.set_mode((WIDTH,HEIGHT))
pg.display.set_caption("bacteria")

run = True
while run:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        if pg.mouse.get_focused():
            coords = pg.mouse.get_pos() 
            vecc = coords[0] - CENTER[0],coords[1] - CENTER[1]
            lenght = math.sqrt(vecc[0]**2 + vecc[1]**2)
            try:
                vecc = vecc[0]/lenght,vecc[1]/lenght
            except:
                pass
            if lenght <= radius:
                vecc = (0,0)
            if vecc != ovec:
                ovec = vecc
                mainsocket.send(f"<{vecc[0]},{vecc[1]}>".encode())

    data = mainsocket.recv(1024).decode()
    data = find_visible_players(data).split(",")
    screen.fill("grey")

    if data != [""]:
        for s in data:
            sp = s.split()
            x = CENTER[0] + int(sp[0])
            y = CENTER[1] + int(sp[1])
            size = int(sp[2])
            color = sp[3]
            pg.draw.circle(screen,color,(x,y),size) 

    pg.draw.circle(screen,COLOR,CENTER,radius)
    pg.draw.line(screen,(0,0,0),CENTER,coords)
    pg.display.update()
pg.quit()


#каждый вектор имеет свои координаты формула - x = xконец - xначало у У также