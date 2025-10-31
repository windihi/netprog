import socket
import time
import pygame as pg
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column,Integer,String
from sqlalchemy.orm import sessionmaker
import psycopg2
import math

POLEWIDTH = 4000
POLEHEIGHT = 4000
WIDTH = 300
HEIGHT = 300
FPS = 60
PROP = WIDTH/POLEWIDTH


Base = declarative_base()
class Player(Base):
    __tablename__ = "gamers"
    id = Column(Integer,primary_key=True,autoincrement=True)
    name = Column(String(250))
    address = Column(String)
    x = Column(Integer,default=500)
    y = Column(Integer,default=500)
    size = Column(Integer,default=50)
    color = Column(String(250), default="red")
    errors = Column(Integer,default=0)
    abs_speed = Column(Integer,default=1)
    speed_x = Column(Integer,default=0)
    speed_y = Column(Integer,default=0)
    h_vision = Column(Integer,default=600)
    w_vision = Column(Integer,default=800)

    def __init__(self,name,address):
        self.name = name
        self.address = address

class LocalPlayer():
    def __init__(self,id,name,socket,address,color):
        self.id = id
        self.db: Player = s.get(Player, self.id)
        self.socket = socket
        self.name = name
        self.address = addr
        self.x = 500
        self.y = 500
        self.size = 50
        self.color = color
        self.errors = 0
        self.abs_speed = 1
        self.speed_x = 0
        self.speed_y = 0
        self.w_vision = 800
        self.h_vision = 600

    def find_vec(self,vec):
        first = None
        for num,sign in enumerate(vec):
            if sign == "<":
                first = num
            if sign == ">" and first is not None:
                second = num
                res = list(map(float,vec[first+1:second].split(",")))
                return res    
        return ""       

    def change_speed(self,vec):
        vecl = self.find_vec(vec)
        self.speed_x = vecl[0] * self.abs_speed
        self.speed_y = vecl[1] * self.abs_speed

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

def check_visibility(dict):
    lp = list(players)
    for x in range(0,len(lp)):
        for i in range(x+1,len(lp)):
            hero1 = players[lp[x]]
            hero2 = players[lp[i]]

            dist = math.sqrt((hero1.x - hero2.x)**2 + (hero1.y - hero2.y)**2)
            vision_dist1 = math.sqrt((hero1.w_vision//2)**2 + (hero1.h_vision//2)**2) + hero2.size
            vision_dist2 = math.sqrt((hero2.w_vision//2)**2 + (hero2.h_vision//2)**2) + hero1.size

            if dist <= vision_dist1:
                vis_x = str(round(hero2.x - hero1.x))
                vis_y = str(round(hero2.y - hero1.y))
                size = str(round(hero2.size))
                color = hero2.color

                data = vis_x+" "+vis_y+" "+size+" "+color
                dict[hero1.id].append(data)
            
            if dist <= vision_dist2:
                vis_x = str(round(hero1.x - hero2.x))
                vis_y = str(round(hero1.y - hero2.y))
                size = str(round(hero1.size))
                color = hero1.color

                data = vis_x+" "+vis_y+" "+size+" "+color
                dict[hero2.id].append(data)
        #сравнение расстояния между бактериями и диагональю экрана + радиус
        #цикл попарного прохода по словарю 
        #если истинно формируем данные к добавлению в список(x,y,size,color)
        #помещаем данные в шаблон строки
        #нужно сравнить видимость второго игрока первым 
        

engine = create_engine("postgresql+psycopg2://postgres:gh538000@localhost/postgres")
Session = sessionmaker(engine)
s = Session()

Base.metadata.create_all(engine)

mainsocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
mainsocket.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
mainsocket.bind(("localhost",12424))
mainsocket.setblocking(False)
mainsocket.listen(5)
print("socket создан")

pg.init()
screen = pg.display.set_mode((WIDTH,HEIGHT))
pg.display.set_caption("bacteria")
clock = pg.time.Clock()

players = {}

run = True
while run:
    clock.tick(FPS)
    for event in pg.event.get():
        if event == pg.QUIT:
            run = False
                
    try:
        newsocket,addr = mainsocket.accept()
        newsocket.setblocking(False)
        new_player = Player("test",addr)
        s.merge(new_player)
        s.commit()
        data = newsocket.recv(1024).decode()
        name,color = data.split(",")
        s.query(Player).filter(Player.address == f"({addr[0]},{addr[1]})").update({"name":name,"color":color})
        s.commit()
        q = s.query(Player).filter(Player.address == f"({addr[0]},{addr[1]})").all()
        for u in q:
            loc_player = LocalPlayer(u.id,u.name,newsocket,u.address,color)
            players[u.id] = loc_player
    except BlockingIOError:
        pass

    for id in list(players):
        try:
            data = players[id].socket.recv(1024).decode()
            players[id].change_speed(data)
        except:
            pass

    for id in list(players):
        players[id].update()
        
    
    visible_bac = {}
    for id in list(players):
        visible_bac[id] = []
    check_visibility(visible_bac)

    for id in list(players):
        visible_bac[id] = "<" + ",".join(visible_bac[id])+">"

    

    screen.fill("black")

    for id in list(players):    
        try:
            players[id].socket.send(visible_bac[id].encode())
        except:
            players[id].socket.close()
            del players[id]
            s.query(Player).filter(Player.id == id).delete()
            s.commit()
            print("socket закрыт")
    
    for id in list(players):
        serv_x = round(players[id].x * PROP)
        serv_y = round(players[id].y * PROP)
        serv_r = round(players[id].size * PROP)
        pg.draw.circle(screen,players[id].color,(serv_x,serv_y),serv_r)

    pg.display.update()
pg.quit()