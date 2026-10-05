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
pieces['house']=cut(m,(1920,1095,2325,1320),o,SK+('adw','fen'))
m2=load('ncr2'); pieces['hall']=cut(m2,(2480,140,3330,640),ov_origin(m2),SK)
mv=load('vctydwtn'); ov=ov_origin(mv)
pieces['bar']=cut(mv,(1470,1100,2340,1450),ov,SK)
pieces['clinic']=cut(mv,(1020,150,1830,510),ov,SK)
pieces['hero']=cut(mv,(540,450,1230,870),ov,SK)
# казарма: жилой дом Города-Убежища (4 спальни вокруг общей комнаты с плитой), без креста и вывесок
pieces['barracks']=cut(mv,(270,930,1080,1380),ov,SK+('vclight',))
mn=load('navarro',rpu=True); pieces['workshop']=cut(mn,(470,30,1090,380),org_render(24696,(560,300)),SK)
mm=load('modmain'); pieces['ranch']=cut(mm,(1440,390,2640,990),ov_origin(mm),SK)
tk=[o for o in mm['objs'] if 0x3000478<=o['pid']<=0x3000481 or o['pid']==0x2000291]
xs=[t['tile']%200 for t in tk]; ys=[t['tile']//200 for t in tk]
pieces['cistern']=dict(objs=tk,floor={},bb=(min(xs),min(ys),max(xs),max(ys)))
# доводка: оставить само здание (самую большую связную группу), убрать лишние стены, пол только под стенами
from render import fidpath
P=pieces
for k in list(P):
    if k!='cistern': P[k]=main_part(P[k])
def drop(k,pre):
    p=P[k]; p['objs']=[o for o in p['objs'] if not any((fidpath(o['fid']) or '').split('\\')[-1].lower().startswith(s) for s in pre)]
    P[k]=main_part(p,gap=70)
def wallfloor(k):
    p=P[k]; w=[o['tile'] for o in p['objs'] if o['pid']>>24==3]
    xs=[t%200 for t in w]; ys=[t//200 for t in w]
    p['floor']={kk:v for kk,v in p['floor'].items() if min(xs)//2<=kk[0]<=max(xs)//2 and min(ys)//2<=kk[1]<=max(ys)//2}
drop('hall',('adw',))
for k in ('hall','clinic','hero','workshop','barracks','house','pump','storage'): wallfloor(k)
g=cut(m,(300,90,1040,560),org_render(25131,(520,300)),SK+('adw','gate4','adb','ncrdoor'))
g=main_part(g,90); g['floor']={}; P['garden']=g
b=main_part(cut(mv,(1470,1170,2340,1450),ov,SK+('adw','fen')),90); P['bar']=b; wallfloor('bar')
mi=load('modinn'); P['stall']=main_part(cut(mi,(240,900,1170,1320),ov_origin(mi),SK),90)
mr=load('redment'); P['corral']=main_part(cut(mr,(540,960,1980,1400),ov_origin(mr),SK),90)
for k,p in pieces.items():
    b=p['bb']; print(k,len(p['objs']),'size',b[2]-b[0]+1,'x',b[3]-b[1]+1)
import pickle; pickle.dump(pieces,open('/tmp/claude-0/m3/pieces.pkl','wb'))
