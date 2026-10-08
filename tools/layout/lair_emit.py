#!/usr/bin/env python3
"""Логово налетчиков (квест 1.4): карта f2mlair = копия горной карты mountn5 из RPU (лагерь у скалы, три палатки).
Точки людей и предметов ставим рукой (ниже), скрипт сдвигает каждую на ближайшую свободную клетку, до которой
можно дойти от точки входа героя, и пишет scripts_src/f2mlairl.h. С IMG=путь рисует карту с отметками."""
import os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapparse
from hexlib import tdir
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
SRC = os.path.join(ROOT, 'base/rpu-2.4.34/maps/mountn5.map')
HIDDEN, NOBLOCK, MULTIHEX = 0x1, 0x10, 0x800
def T(x, y): return y * 200 + x
def xy(t): return t % 200, t // 200
def ring(t, n):
    s = {t}
    for _ in range(n): s |= {tdir(u, r, 1) for u in s for r in range(6)}
    return s

m = mapparse.parse(SRC)
objs = [o for o in m['objs'] if o['elev'] == 0 and o['tile'] >= 0]
blk = set()
for o in objs:
    if o['pid'] >> 24 not in (1, 2, 3): continue
    f = o['flags']
    if f & (HIDDEN | NOBLOCK): continue
    blk |= ring(o['tile'], 1) if f & MULTIHEX else {o['tile']}
# Видимая часть карты (пол без черноты): прямоугольник в пикселях, по картинке mountn5 (render.py, центр 96,98)
from render import hexxy
cx, cy = hexxy(T(96, 98)); X0, Y0 = cx - 1300 + 663 + 40, cy - 800 + 400 + 30
X1, Y1 = cx - 1300 + 1992 - 40, cy - 800 + 1153 - 30
def inside(t):
    x, y = hexxy(t); return X0 <= x <= X1 and Y0 <= y <= Y1
ENTER = m['enter']
seen = {ENTER}; q = [ENTER]
while q:
    t = q.pop()
    for r in range(6):
        n = tdir(t, r, 1)
        if n not in seen and n not in blk and inside(n): seen.add(n); q.append(n)
FREE = seen
print('доступно клеток', len(FREE), 'вход', xy(ENTER))

used = set()
def snap(x, y, keep=1):
    t0 = T(x, y)
    for d in range(0, 12):
        for t in sorted(ring(t0, d) - (ring(t0, d - 1) if d else set())):
            if t in FREE and not (ring(t, keep) & used):
                used.add(t); return t
    sys.exit(f'нет места у {x},{y}')

# name: (x, y, комментарий)
P = [
    ('HERO',    84, 120, 'герой входит с юга, за деревьями'),
    ('POST0',   88, 108, 'пост у входа'),
    ('POST1',   79, 107, 'пост у входа'),
    ('KANE',   100,  86, 'главарь в глубине, у скалы'),
    ('CHEST',  101,  83, 'сундук за главарем (тайник)'),
    ('CELLAR', 113,  91, 'погреб под камнями у западной палатки'),
    ('WATER',   82,  91, 'бак с водой посреди лагеря'),
    ('STORE',   95,  93, 'ящик со складом (яд)'),
    ('DYNBOX', 108,  92, 'ящик с динамитом у западной палатки, рядом с погребом'),
    ('SPAWN0',  89,  99, 'патруль'), ('SPAWN1', 81,  97, 'патруль'), ('SPAWN2', 96, 100, 'патруль'),
    ('SPAWN3', 105,  92, 'у западной палатки'), ('SPAWN4', 92, 90, 'у шатра'), ('SPAWN5', 76, 93, 'у восточной палатки'),
    ('SPAWN6',  70,  90, 'у машины'), ('SPAWN7', 110, 95, 'у бочек'), ('SPAWN8', 99, 95, 'у ящиков'),
    ('SPAWN9',  85,  94, 'у костра'), ('SPAWN10', 102, 98, 'у костра'), ('SPAWN11', 74, 99, 'у восточной палатки'),
]
OUT = {}
for n, x, y, c in P:
    OUT[n] = (snap(x, y), c)
# Сундук и бак ставятся на клетку: не должны перекрыть проход к главарю и к погребу
blk2 = blk | {OUT[k][0] for k in ('CHEST', 'WATER', 'STORE', 'DYNBOX')} | ring(OUT['CELLAR'][0], 1)   # куча камней многоклеточная
def reach(a, b, blkx):
    s = {a}; q = [a]
    while q:
        t = q.pop()
        for r in range(6):
            n = tdir(t, r, 1)
            if n in ring(b, 2 if b == OUT['CELLAR'][0] else 1) and n in FREE and n not in blkx: return True
            if n not in s and n not in blkx and n in FREE: s.add(n); q.append(n)
    return False
for k in ['KANE', 'CHEST', 'CELLAR', 'WATER', 'STORE', 'DYNBOX'] + [p[0] for p in P if p[0].startswith('SPAWN')]:
    assert reach(OUT['HERO'][0], OUT[k][0], blk2), k
NSPAWN = sum(1 for p in P if p[0].startswith('SPAWN'))

o = ['// Сгенерировано tools/layout/lair_emit.py: точки на карте логова (f2mlair, копия mountn5). Не править руками.',
     '#ifndef F2MLAIRL_H', '#define F2MLAIRL_H']
for n, (t, c) in OUT.items():
    o.append(f'#define LAIR_{n:<8} ({t})   // {xy(t)[0]}, {xy(t)[1]}: {c}')
o.append(f'#define LAIR_SPAWNS     ({NSPAWN})')
o.append('procedure lair_spawn(variable i) begin')
for i in range(NSPAWN):
    o.append(f'   {"if" if i == 0 else "else if"} (i == {i}) then return LAIR_SPAWN{i};')
o += ['   return LAIR_SPAWN0;', 'end', '#endif', '']
open(os.path.join(ROOT, 'scripts_src/f2mlairl.h'), 'w', encoding='utf-8').write('\n'.join(o))

if os.environ.get('IMG'):
    from render import render
    marks = [(t, n, (255, 255, 0)) for n, (t, c) in OUT.items()]
    render(SRC, os.environ['IMG'], T(92, 98), rad_px=(800, 450), marks=marks)
