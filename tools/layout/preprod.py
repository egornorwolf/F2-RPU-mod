# Предпродакшн: вырезаем готовые здания из карт F2/RPU и ставим их на участки лагеря.
import sys, os, subprocess
sys.path.insert(0, os.path.dirname(__file__))
from mapparse import parse, dat0
from render import hexxy, fidpath
from hexlib import nearest
CACHE = '/tmp/claude-0/m3/'
def load(name, rpu=False):
    p = CACHE + name + ('_rpu' if rpu else '') + '.map'
    if not os.path.exists(p):
        if rpu:
            open(p, 'wb').write(subprocess.check_output(['git', '-C', '/home/claude/rpu', 'show', f'HEAD:data/maps/{name}.map']))
        else:
            open(p, 'wb').write(dat0(f'maps\\{name}.map'))
    return parse(p)
def ov_origin(m):
    # то же, что overview.py: левый верхний угол полного рендера в мировых пикселях
    sb = [o['tile'] for o in m['objs'] if o['pid'] == 0x500000c]
    pts = [hexxy(t) for t in sb] if sb else [hexxy(t) for t in (0, 199, 39800, 39999)]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    cx = (min(xs) + max(xs)) // 2; cy = (min(ys) + max(ys)) // 2
    rx = (max(xs) - min(xs)) // 2 + 400; ry = (max(ys) - min(ys)) // 2 + 300
    c = nearest(cx, cy); X, Y = hexxy(c)
    return X - rx, Y - ry
def cut(m, box, origin, skip=()):
    """Объекты и пол из прямоугольника box (пиксели полного рендера)."""
    x0, y0 = origin
    L, T, R, B = box[0] + x0, box[1] + y0, box[2] + x0, box[3] + y0
    objs = []
    for o in m['objs']:
        if o['elev'] != 0 or (o['pid'] >> 24) in (1, 5): continue
        x, y = hexxy(o['tile']); x += 16; y += 8
        if not (L <= x < R and T <= y < B): continue
        p = fidpath(o['fid']) or ''
        if any(s in p.lower() for s in skip): continue
        objs.append(dict(o))
    tiles = [t for t in [o['tile'] for o in objs]]
    xs = [t % 200 for t in tiles]; ys = [t // 200 for t in tiles]
    bb = (min(xs), min(ys), max(xs), max(ys))
    floor = {}
    for sy in range(bb[1] // 2, bb[3] // 2 + 1):
        for sx in range(bb[0] // 2, bb[2] // 2 + 1):
            f = m['tiles'][0][sy * 100 + sx]
            if f & 0xffff > 1: floor[(sx, sy)] = f
    return dict(objs=objs, floor=floor, bb=bb)
def place(piece, tx, ty):
    """Сдвиг так, чтобы левый верх (по клеткам) встал в (tx, ty). Сдвиг четный, чтобы форма не ломалась."""
    x0, y0 = piece['bb'][0], piece['bb'][1]
    dx = (tx - x0) & ~1; dy = (ty - y0) & ~1
    objs = []
    for o in piece['objs']:
        x, y = o['tile'] % 200 + dx, o['tile'] // 200 + dy
        if 0 <= x < 200 and 0 <= y < 200:
            n = dict(o); n['tile'] = y * 200 + x; objs.append(n)
    floor = {(sx + dx // 2, sy + dy // 2): f for (sx, sy), f in piece['floor'].items()}
    return objs, floor
def main_part(piece, gap=90):
    """Оставить самую большую связную группу объектов (соседи ближе gap пикселей), пол — только под ней."""
    objs = piece['objs']; pts = [hexxy(o['tile']) for o in objs]; n = len(objs)
    seen = [False] * n; best = []
    for i in range(n):
        if seen[i]: continue
        comp = [i]; seen[i] = True; k = 0
        while k < len(comp):
            a = pts[comp[k]]; k += 1
            for j in range(n):
                if not seen[j] and (pts[j][0] - a[0]) ** 2 + (pts[j][1] - a[1]) ** 2 <= gap * gap:
                    seen[j] = True; comp.append(j)
        if len(comp) > len(best): best = comp
    objs = [objs[i] for i in best]
    xs = [o['tile'] % 200 for o in objs]; ys = [o['tile'] // 200 for o in objs]
    bb = (min(xs), min(ys), max(xs), max(ys))
    floor = {k: v for k, v in piece['floor'].items() if bb[0] // 2 <= k[0] <= bb[2] // 2 and bb[1] // 2 <= k[1] <= bb[3] // 2}
    return dict(objs=objs, floor=floor, bb=bb)
