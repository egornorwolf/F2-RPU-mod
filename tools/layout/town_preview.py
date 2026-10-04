# Предпродакшн города: ставит здания 4 уровня (pieces.pkl из cut_pieces.py) на участки и рисует town_full.png / town_small.jpg.
import sys,pickle; sys.path.insert(0,'/home/claude/f2-rpu-mod/tools/layout')
from preprod import place
import render
from render import hexxy
from mapparse import parse
from PIL import Image, ImageDraw, ImageFont
P=pickle.load(open('/tmp/claude-0/m3/pieces.pkl','rb'))
base=parse('/home/claude/f2-rpu-mod/build/data/maps/f2mcamp.map')
def T(u,y): return y*200+(199-u)
objs=[]; floor={}; labels=[]
def put(name,u0,y0,label=None):
    p=P[name]; w=p['bb'][2]-p['bb'][0]+1; h=p['bb'][3]-p['bb'][1]+1
    o,f=place(p,199-u0-w+1,y0); objs.extend(o); floor.update(f)
    if label: labels.append((label,u0+w//2,y0+h//2))
    return w,h
def spr(path,u,y,kind='scenery'):
    objs.append(dict(tile=T(u,y),pid=0x2000001,fid=0,elev=0,flags=0,sid=-1,path=f'art\\{kind}\\{path}'))
LAY={}
# Запад
put('pump',35,35,'1 Водокачка'); put('cistern',52,38,'Цистерна')
spr('WELL001.frm',47,49); spr('well1.frm',55,49); spr('gektank5.frm',44,46)
put('ranch',35,58,'4 Ранчо')
put('workshop',35,105,'9 Автомастерская'); spr('crafter1.frm',33,128)
put('storage',36,130,'10 Склад')
# Вторая колонка
put('garden',68,35,'2 Огород'); put('garden',68,64,'3 Огород')
put('bar',68,108,'11 Бар'); put('clinic',70,124,'14 Госпиталь')
# Восток
for i in range(5): put('house',102+i*13,35)
for i in range(3): put('house',102+i*13,51)
labels.append(('6 Жилье',128,50))
put('hero',143,50,'8 Дом героя')
put('hall',102,68,'12 Ратуша')
put('barracks',128,116,'16 Казарма')
# Двор каравана у главных ворот
for i,(u,y) in enumerate([(84,152),(92,154),(108,152),(116,154)]): spr('CCART0%d.FRM'%(1+i%2),u,y,'items')
labels.append(('15 Двор каравана',100,156))
# Пост у ворот
spr('CONBAR01.frm',92,166); spr('vclight1.frm',96,166); spr('CONBAR01.frm',104,166); spr('vclight1.frm',108,166)
# Сквер и деревья
import random; random.seed(3)
for u in range(70,97,6):
    for y in (94,100):
        spr(random.choice(['tree11.frm','tree10.frm','TREE8.FRM']),u+random.randint(-1,1),y)
labels.append(('13 Сквер',83,97)); labels.append(('17 Охрана, тир, резерв',125,140))
for y in range(36,160,8): spr('tree11.frm',97,y)   # аллея вдоль главной оси (запад)
mm=dict(base); mm['objs']=objs
t=list(base['tiles'][0])
import collections, random
common=collections.Counter(v for v in t if v&0xffff>1).most_common(1)[0][0]
rnd=random.Random(7)
t=[v if (v&0xffff) not in (0,1,659,179,180) else (v&0xffff0000)|rnd.choice(range(191,199)) for v in t]
for (sx,sy),f in floor.items(): t[sy*100+sx]=f
mm['tiles']={0:t}
render.parse=lambda f:mm
# Рамка забора D–Q, 4–17
F=[T(30,30),T(169,30),T(169,169),T(30,169)]
pts=[hexxy(x) for x in F]
cx=(min(p[0] for p in pts)+max(p[0] for p in pts))//2; cy=(min(p[1] for p in pts)+max(p[1] for p in pts))//2
from hexlib import nearest
c=nearest(cx,cy); rx=(max(p[0] for p in pts)-min(p[0] for p in pts))//2+150; ry=(max(p[1] for p in pts)-min(p[1] for p in pts))//2+250
render.render('x','/tmp/claude-0/m3/town_full.png',c,rad_px=(rx,ry))
im=Image.open('/tmp/claude-0/m3/town_full.png'); d=ImageDraw.Draw(im)
X0,Y0=hexxy(c); X0-=rx; Y0-=ry
def scr(u,y): x,yy=hexxy(T(u,y)); return x+16-X0, yy+8-Y0
d.polygon([scr(30,30),scr(169,30),scr(169,169),scr(30,169)],outline=(255,210,90),width=6)
gx=scr(90,169),scr(109,169); d.line(gx,fill=(255,255,255),width=14)
fnt=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',44)
for lb,u,y in labels:
    x,yy=scr(u,y); d.text((x-len(lb)*12,yy-140),lb,font=fnt,fill=(255,255,120),stroke_width=4,stroke_fill=(0,0,0))
im.save('/tmp/claude-0/m3/town_full.png'); print(im.size)
sm=im.copy(); sm.thumbnail((2400,2400)); sm.save('/tmp/claude-0/m3/town_small.jpg',quality=88)
