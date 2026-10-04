import sys; sys.path.insert(0, __import__('os').path.dirname(__file__) or '.')
from render import render, hexxy
from hexlib import tdir, nearest
from tent import TENT
S = 20100; SX, SY = hexxy(S)
def at(dx, dy, parity=None): return nearest(SX + dx, SY + dy, parity)
def tent_objs(anchor, beds=True):
    out = [(anchor + dy*200 + dx, p) for dx, dy, p in TENT]
    if beds: out += [(anchor - 4*200 - 2, 0x20000d1), (anchor - 2*200 - 3, 0x20000d0), (anchor - 2*200 + 1, 0x20000d0)]
    return out
SC = lambda i: 0x02000000 | i
L = {}   # name -> list of (tile, pid)
P = {}   # named points
def put(name, tile, pid): L.setdefault(name, []).append((tile, pid))
# --- основа лагеря ---
P['fire'] = at(400, -110)
put('base', P['fire'], SC(1200))
put('base', at(250, -40), SC(1))       # горящая бочка
put('base', at(600, -190), SC(1))
P['table'] = at(290, -170); put('base', P['table'], SC(61))
put('base', at(240, -200), SC(596))    # доска
P['ted'] = at(330, -150)
for i, (dx, dy) in enumerate([(120, -400), (430, -450), (740, -400)]):
    a = at(dx, dy, 1); P[f'tent{i}'] = a
    for t, p in tent_objs(a): put('base', t, p)
P['herotent'] = at(-250, -330, 1)
for t, p in tent_objs(P['herotent']): put('base', t, p)
P['locker'] = P['herotent'] - 3*200 - 1
P['oldwell'] = at(620, 150); put('oldwell', P['oldwell'], SC(993))
put('base', at(700, 260), SC(398)); put('base', at(740, 290), SC(401)); put('base', at(670, 300), SC(220))
P['foreman'] = at(170, 140)
P['chief'] = at(80, 40)
# --- места под стройку ---
P['newwell'] = at(260, 290)
P['garden0'] = at(-80, 330); P['garden1'] = at(-380, 360)
for i, (dx, dy) in enumerate([(-600, -130), (-620, 140), (-920, -300), (-930, 0)]):
    P[f'slot{i}'] = at(dx, dy, 1)
if __name__ == '__main__':
    extra = [dict(tile=t, pid=p, fid=0, path=None) for v in L.values() for t, p in v]
    from mapparse import proto
    import struct
    for e in extra: e['fid'] = struct.unpack_from('>i', proto(e['pid']), 8)[0]
    marks = [(t, k, (255,255,0)) for k, t in P.items()] + [(S, 'START', (0,255,255))]
    render('/home/claude/f2-rpu-mod/base/rpu-2.4.34/maps/desert1.map', 'camp.png', at(-50, -20), rad_px=(1300, 750), extra=extra, marks=marks)

def garden_objs(c):
    out = []; k = 0
    for row in range(3):
        for col in range(4):
            t = tdir(c, 1, col * 2 - 3 + (row % 2))
            t = tdir(tdir(t, 2, 2 * (row - 1)), 3, 2 * (row - 1))
            out.append((t, SC(366 + (k % 2)) if row == 1 else SC(963 + (k % 6)))); k += 1
    out.append((tdir(c, 4, 6), SC(381)))  # лопата
    return out
DONE = {'newwell': [(P['newwell'], SC(383))]}
for i in range(2): DONE[f'garden{i}'] = garden_objs(P[f'garden{i}'])
for i in range(4): DONE[f'slot{i}'] = tent_objs(P[f'slot{i}'])
