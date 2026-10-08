#!/usr/bin/env python3
"""Погреб логова (квест 1.4, Егор 2026-10-08: лаз с лестницей вниз, как в доме героя).
Карта f2mcell = копия пещеры CAVE7 из F2 без выходов на карту мира (из погреба только по лестнице наверх).
Пишет mod/data/maps/f2mcell.map и scripts_src/f2mcelll.h (точки людей и предметов).
С IMG=путь рисует карту с отметками."""
import os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapparse
from hexlib import tdir

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
SRC_NAME = 'CAVE7.MAP'
HIDDEN, NOBLOCK, MULTIHEX = 0x1, 0x10, 0x800


def T(x, y): return y * 200 + x
def xy(t): return t % 200, t // 200
def ring(t, n):
    s = {t}
    for _ in range(n): s |= {tdir(u, r, 1) for u in s for r in range(6)}
    return s


class R:
    def __init__(s, b, o=0): s.b, s.o = b, o
    def i(s, n=1):
        if n == 0: return ()
        v = struct.unpack_from(f'>{n}i', s.b, s.o); s.o += 4 * n
        return v if n > 1 else v[0]


def parse_spans(b):
    """Как mapparse.parse, но помнит, где в файле лежит каждый объект верхнего уровня."""
    r = R(b); r.o = 20
    ent, el, rot, nlv, scr, flags, dark, ngv = r.i(8)
    r.o = 0xEC
    if ngv: r.i(ngv)
    if nlv: r.i(nlv)
    for e in range(3):
        if not flags & (2 << e): r.i(10000)
    for t in range(5):
        n = r.i()
        if n:
            for _ in range((n + 15) // 16):
                for _ in range(16):
                    sid = r.i(); r.i(); st = (sid >> 24) & 0xff
                    if st == 1: r.i(2)
                    elif st == 2: r.i(1)
                    r.i(14)
                r.i(2)
    total_off = r.o; total = r.i()

    def read_obj():
        st = r.o
        f = r.i(18)
        o = dict(tile=f[1], fid=f[8], flags=f[9], elev=f[10], pid=f[11], sid=f[16], rot=f[7])
        inv = r.i(); r.i(2)
        t = o['pid'] >> 24
        if t == 1: r.i(11)
        else:
            r.i()
            if t == 0: r.i({3: 2, 4: 1, 5: 1, 6: 1}.get(mapparse.subtype(o['pid']), 0))
            elif t == 2: r.i({0: 1, 1: 2, 2: 2, 3: 2, 4: 2}.get(mapparse.subtype(o['pid']), 0))
            elif t == 5 and 0x5000010 <= o['pid'] <= 0x5000017: o['exit'] = r.i(4)
        for _ in range(inv):
            r.i(); read_obj()
        o['span'] = (st, r.o)
        return o

    objs = []; counts = []
    for e in range(3):
        co = r.o; n = r.i(); counts.append([n, co])
        for _ in range(n): objs.append(read_obj())
    assert r.o == len(b), (r.o, len(b))
    return dict(objs=objs, counts=counts, total=total, total_off=total_off, ent=ent, flags=flags)


src = mapparse.dat(f'maps\\{SRC_NAME}')
m = parse_spans(src)

# ---- выходы на карту мира убираем: из погреба только наверх по лестнице
cut = [o for o in m['objs'] if 'exit' in o]
out = bytearray(src[:m['total_off']])
out += struct.pack('>i', m['total'] - len(cut))
for e in range(3):
    objs_e = [o for o in m['objs'] if o['elev'] == e and 'exit' not in o]   # порядок в файле сохраняем
    out += struct.pack('>i', len(objs_e))
    for o in objs_e: out += src[o['span'][0]:o['span'][1]]
out[4:20] = b'F2MCELL.MAP'.ljust(16, b'\0')
os.makedirs(os.path.join(ROOT, 'mod/data/maps'), exist_ok=True)
open(os.path.join(ROOT, 'mod/data/maps/f2mcell.map'), 'wb').write(bytes(out))
print('f2mcell.map', len(out), 'байт, убрано выходов', len(cut))

# ---- точки на карте: считаем по исходной карте (объекты те же, кроме выходов)
objs = [o for o in m['objs'] if o['elev'] == 0 and o['tile'] >= 0 and 'exit' not in o]
blk = set()
for o in objs:
    if o['pid'] >> 24 not in (1, 2, 3): continue
    f = o['flags']
    if f & (HIDDEN | NOBLOCK): continue
    blk |= ring(o['tile'], 1) if f & MULTIHEX else {o['tile']}

START = T(100, 100)
seen = {START}; q = [START]
while q:
    t = q.pop()
    for r in range(6):
        n = tdir(t, r, 1)
        if n not in seen and n not in blk and 0 <= n % 200 < 200 and 0 <= n // 200 < 200:
            seen.add(n); q.append(n)
FREE = seen
print('доступно клеток', len(FREE))

used = set()
def snap(x, y, keep=1):
    t0 = T(x, y)
    for d in range(0, 14):
        for t in sorted(ring(t0, d) - (ring(t0, d - 1) if d else set())):
            if t in FREE and not (ring(t, keep) & used):
                used.add(t); return t
    sys.exit(f'нет места у {x},{y}')

# name: (x, y, комментарий)
P = [
    ('HERO',    100, 100, 'герой спускается сюда, у лестницы наверх'),
    ('LADDER',   99,  99, 'лестница наверх, в карьер'),
    ('GUARD0',   95,  95, 'охранник у прохода'),
    ('GUARD1',  105, 103, 'охранник у запасов'),
    ('STACK',   108, 106, 'штабель с запасами банды: сюда закладывают заряд'),
    ('BOX0',    106, 108, 'ящик с едой'),
    ('BOX1',    110, 103, 'ящик с водой'),
    ('BOX2',    103, 107, 'ящик с мелочью банды'),
    ('DYN',      97, 103, 'ящик с динамитом'),
]
OUT = {}
for n, x, y, c in P:
    OUT[n] = (snap(x, y), c)

blk2 = blk | {OUT[k][0] for k in ('LADDER', 'STACK', 'BOX0', 'BOX1', 'BOX2', 'DYN')}
def reach(a, b, blkx):
    s = {a}; q = [a]
    while q:
        t = q.pop()
        for r in range(6):
            n = tdir(t, r, 1)
            if n in ring(b, 1): return True
            if n not in s and n not in blkx and n in FREE: s.add(n); q.append(n)
    return False
for k in OUT:
    if k == 'HERO': continue
    assert reach(OUT['HERO'][0], OUT[k][0], blk2), k

o = ['// Сгенерировано tools/layout/cellar_emit.py: точки в погребе логова (f2mcell, копия пещеры CAVE7).',
     '// Не править руками.', '#ifndef F2MCELLL_H', '#define F2MCELLL_H']
for n, (t, c) in OUT.items():
    o.append(f'#define CELL_{n:<8} ({t})   // {xy(t)[0]}, {xy(t)[1]}: {c}')
o += ['#endif', '']
open(os.path.join(ROOT, 'scripts_src/f2mcelll.h'), 'w', encoding='utf-8').write('\n'.join(o))
print('f2mcelll.h', {n: xy(t) for n, (t, c) in OUT.items()})

if os.environ.get('IMG'):
    from render import render
    tmp = os.path.join(ROOT, 'mod/data/maps/f2mcell.map')
    marks = [(t, n, (255, 255, 0)) for n, (t, c) in OUT.items()]
    render(tmp, os.environ['IMG'], T(102, 101), rad_px=(800, 450), marks=marks)
