# Вырезает здания 4 уровня из карт игры (preprod.cut) в pieces.pkl для town_preview.py.
import sys; sys.path.insert(0,'/home/claude/f2-rpu-mod/tools/layout')
from preprod import *
import render
from render import hexxy
COLS='ABCDEFGHIJKLMNOPQRST'
def plot_hex(c1,r1,c2,r2):
    # x растет влево: колонка = (199-x)//10
    xa=199-(COLS.index(c2)*10+9); xb=199-COLS.index(c1)*10
    return xa,(r1-1)*10,xb,r2*10-1
SK=('tree','weed','rock','eggs','bush','cac','drock','block')
def org_render(c,rad): X,Y=hexxy(c); return X-rad[0],Y-rad[1]
pieces={}
m=load('ncr3'); o=ov_origin(m)
pieces['pump']=cut(m,(2390,300,2800,560),o,SK+('adw','fen'))
pieces['garden']=cut(m,(300,90,1040,560),org_render(25131,(520,300)),SK+('adw','gate4'))
pieces['storage']=cut(m,(3090,800,3550,1050),o,SK+('adw',))
pieces['barracks']=cut(m,(1290,340,2370,950),o,SK+('adw',))
pieces['house']=cut(m,(1920,1095,2325,1320),o,SK+('adw','fen'))
m2=load('ncr2'); pieces['hall']=cut(m2,(2480,140,3330,640),ov_origin(m2),SK)
mv=load('vctydwtn'); ov=ov_origin(mv)
pieces['bar']=cut(mv,(1470,1100,2340,1450),ov,SK)
pieces['clinic']=cut(mv,(1020,150,1830,510),ov,SK)
pieces['hero']=cut(mv,(540,450,1230,870),ov,SK)
mn=load('navarro',rpu=True); pieces['workshop']=cut(mn,(470,30,1090,380),org_render(24696,(560,300)),SK)
mm=load('modmain'); pieces['ranch']=cut(mm,(1440,390,2640,990),ov_origin(mm),SK)
tk=[o for o in mm['objs'] if 0x3000478<=o['pid']<=0x3000481 or o['pid']==0x2000291]
xs=[t['tile']%200 for t in tk]; ys=[t['tile']//200 for t in tk]
pieces['cistern']=dict(objs=tk,floor={},bb=(min(xs),min(ys),max(xs),max(ys)))
for k,p in pieces.items():
    b=p['bb']; print(k,len(p['objs']),'size',b[2]-b[0]+1,'x',b[3]-b[1]+1)
import pickle; pickle.dump(pieces,open('/tmp/claude-0/m3/pieces.pkl','wb'))
