import socket
import time
import pygame as pg
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column,Integer,String
from sqlalchemy.orm import sessionmaker
import psycopg2
import math
from russian_names import RussianNames
import random

POLEWIDTH = 4000
POLEHEIGHT = 4000
WIDTH = 300
HEIGHT = 300
FPS = 100
PROP = WIDTH/POLEWIDTH
COLORS = ['Maroon', 'DarkRed', 'FireBrick', 'Red', 'Salmon', 'Tomato', 'Coral', 'OrangeRed',
           'Chocolate', 'SandyBrown', 'DarkOrange', 'Orange', 'DarkGoldenrod', 'Goldenrod', 'Gold',
             'Olive', 'Yellow', 'YellowGreen', 'GreenYellow', 'Chartreuse', 'LawnGreen', 'Green',
            'Lime', 'Lime Green', 'SpringGreen', 'MediumSpringGreen', 'Turquoise',
            'LightSeaGreen', 'MediumTurquoise', 'Teal', 'DarkCyan', 'Aqua', 'Cyan', 'Dark Turquoise',
            'DeepSkyBlue', 'DodgerBlue', 'RoyalBlue', 'Navy', 'DarkBlue', 'MediumBlue']
BOTSQUANTITY = 20
FOODSIZE = 20
FOODMULTIPLIER = POLEWIDTH * POLEHEIGHT / 400000
FOODQUANTITY = int(FOODMULTIPLIER * 1)

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
        self.address = address
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

    def new_abs_speed(self):
        self.abs_speed = 10/math.sqrt(self.size)

    def update(self):
        if self.x - self.size <= 0:
            if self.speed_x >= 0:
                self.x += self.speed_x
        elif self.x + self.size >= POLEWIDTH:
            if self.speed_x <= 0:
                self.x += self.speed_x
        else:
            self.x += self.speed_x
        
        if self.y - self.size <= 0:
            if self.speed_y >= 0:
                self.y += self.speed_y
        elif self.y + self.size >= POLEHEIGHT:
            if self.speed_y <= 0:
                self.y += self.speed_y
        else:
            self.y += self.speed_y

    def sync(self):
        self.db.size = self.size
        self.db.abs_speed = self.abs_speed
        self.db.speed_x = self.speed_x
        self.db.speed_y = self.speed_y
        self.db.errors = self.errors
        self.db.x = self.x
        self.db.y = self.y
        self.db.color = self.color
        self.db.w_vision = self.w_vision
        self.db.h_vision = self.h_vision
        s.merge(self.db)
        s.commit()

    def load(self):
        self.size = self.db.size
        self.abs_speed = self.db.abs_speed
        self.speed_x = self.db.speed_x
        self.speed_y = self.db.speed_y
        self.errors = self.db.errors
        self.x = self.db.x
        self.y = self.db.y
        self.color = self.db.color
        self.w_vision = self.db.w_vision
        self.h_vision = self.db.h_vision
        return self

def check_visibility(dict):
    lp = list(players)
    for x in range(0,len(lp)):
        for f in foods:
            hero = players[lp[x]]
            dist = math.sqrt((hero.x - f.x)**2 + (hero.y - f.y)**2)
            vision_dist = math.sqrt((hero.w_vision//2)**2 + (hero.h_vision//2)**2) + f.size

            if dist <= vision_dist:
                if dist <= hero.size and hero.size > f.size * 1.1:
                    hero.size = math.sqrt(hero.size**2 + f.size**2)
                    hero.new_abs_speed()
                    f.size = 0

                if hero.socket is not None:
                    vis_x = str(round(f.x - hero.x))
                    vis_y = str(round(f.y - hero.y))
                    size = str(round(f.size))
                    color = f.color

                    data = vis_x+" "+vis_y+" "+size+" "+color
                    dict[hero.id].append(data)

        for i in range(x+1,len(lp)):
            hero1 = players[lp[x]]
            hero2 = players[lp[i]]

            dist = math.sqrt((hero1.x - hero2.x)**2 + (hero1.y - hero2.y)**2)
            vision_dist1 = math.sqrt((hero1.w_vision//2)**2 + (hero1.h_vision//2)**2) + hero2.size
            vision_dist2 = math.sqrt((hero2.w_vision//2)**2 + (hero2.h_vision//2)**2) + hero1.size

            
            if dist <= vision_dist1:
                if dist <= hero1.size and hero1.size > hero2.size * 1.1:
                    hero1.size = math.sqrt(hero1.size**2 + hero2.size**2)
                    hero1.new_abs_speed()

                    hero2.size,hero2.speed_x,hero2.speed_y = 0,0,0
                if hero1.socket is not None:
                    vis_x = str(round(hero2.x - hero1.x))
                    vis_y = str(round(hero2.y - hero1.y))
                    size = str(round(hero2.size))
                    color = hero2.color

                    data = vis_x+" "+vis_y+" "+size+" "+color
                    dict[hero1.id].append(data)
                
            
            
            if dist <= vision_dist2:
                if dist <= hero2.size and hero2.size > hero1.size * 1.1:
                    hero2.size = math.sqrt(hero1.size**2 + hero2.size**2)
                    hero2.new_abs_speed()

                    hero1.size,hero1.speed_x,hero1.speed_y = 0,0,0
                if hero2.socket is not None:
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
        # r2(1) + r2(2) -> sqrt(r(3))
        
class Food():
    def __init__(self,x,y,size,color):
        self.x = x
        self.y = y
        self.size = size
        self.color = color

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

players = {}
foods = []

bots_names = RussianNames(count=BOTSQUANTITY*2,patronymic=False,surename=False,rare=True)
bots_names = list(set(bots_names))
for n in range(BOTSQUANTITY):
    bot = Player(bots_names[n],None)
    bot.color = random.choice(COLORS)
    bot.x = random.randint(0,POLEWIDTH)
    bot.y = random.randint(0,POLEHEIGHT)
    bot.speed_x = random.randint(-1,1)
    bot.speed_y = random.randint(-1,1)
    bot.size = random.randint(10,100)
    s.add(bot)
    s.commit()
    botlocal = LocalPlayer(bot.id,bot.name,None,None,bot.color).load()
    players[botlocal.id] = botlocal

for f in range(0,FOODQUANTITY):
    x = random.randint(0,POLEWIDTH)
    y = random.randint(0,POLEHEIGHT)
    color = random.choice(COLORS)
    food = Food(x,y,FOODSIZE,color)
    foods.append(food)

pg.init()
screen = pg.display.set_mode((WIDTH,HEIGHT))
pg.display.set_caption("bacteria")
clock = pg.time.Clock()


run = True
tick = -1
while run:
    clock.tick(FPS)
    tick += 1
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False

    if tick % 50 == 0:            
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
        if players[id].socket is not None:
            try:
                data = players[id].socket.recv(1024).decode()
                players[id].change_speed(data)
            except:
                pass
        else:
            if tick % 400 == 0:
                vec = f"<{random.uniform(-1.0,1.0)},{random.uniform(-1.0,1.0)}>"
                players[id].change_speed(vec)
    

    for id in list(players):
        players[id].update()
        
    
    visible_bac = {}
    for id in list(players):
        visible_bac[id] = []
    check_visibility(visible_bac)

    for id in list(players):
        visible_bac[id] = "<" + ",".join(visible_bac[id])+","+str(round(players[id].size))+">"

    

    screen.fill("black")

    for id in list(players):    
        if players[id].socket is not None:
            try:
                players[id].socket.send(visible_bac[id].encode())
            except:
                players[id].socket.close()
                del players[id]
                s.query(Player).filter(Player.id == id).delete()
                s.commit()
                print("socket закрыт")

    for id in list(players):
        if players[id].size == 0:
            if players[id].socket is not None:
                players[id].socket.close()
            del players[id]
            s.query(Player).filter(Player.id == id).delete()
            s.commit()

    for f in foods:
        if f.size == 0:
            del f
        else:
            serv_x = round(f.x * PROP)
            serv_y = round(f.y * PROP)
            serv_r = round(f.size * PROP)
            pg.draw.circle(screen,f.color,(serv_x,serv_y),serv_r)


    for id in list(players):
        serv_x = round(players[id].x * PROP)
        serv_y = round(players[id].y * PROP)
        serv_r = round(players[id].size * PROP)
        pg.draw.circle(screen,players[id].color,(serv_x,serv_y),serv_r)

    if tick % 500 == 0:
        for id in list(players):
            players[id].sync()

    pg.display.update()
pg.quit()
mainsocket.close()
s.query(Player).delete()
s.commit()
#разобраться с вектором
#еда и размер