# Проверка проходимости стройки поиском пути (как движок: _obj_blocking_at в fallout2-ce).
# Для каждого здания и уровня: клетки, куда можно дойти снаружи при закрытых дверях (зеленые),
# только через двери (синие) и куда не попасть вообще (красные). Сквозная стена видна как зеленое внутри комнаты.
# Вход: town_build.pkl. Выход: OUT/path/<здание>_lv<N>.png, сводка в OUT/path/report.txt.
# Использование: pathcheck.py [папка с town_build.pkl] [IMG=1 — картинки]
import sys, os, pickle, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render, mapparse
from render import hexxy
from hexlib import tdir
from PIL import Image, ImageDraw

SRC = sys.argv[1] if len(sys.argv) > 1 else '/tmp/claude-0/tb/'
D = pickle.load(open(SRC + 'town_build.pkl', 'rb'))
PROTO = D['PROTO']
OUT = SRC + 'path/'; os.makedirs(OUT, exist_ok=True)
HIDDEN, NOBLOCK, MULTIHEX = 0x1, 0x10, 0x800

def flags(e): return (PROTO[e['pid']][1] | e['fset']) & ~e['fclr']
def is_door(e): return e['pid'] >> 24 == 2 and PROTO[e['pid']][4] == 0

def grid(objs):
    """Занятые клетки: блок (стены, декорации) и двери отдельно."""
    block, door = set(), set()
    for e in objs:
        if e['pid'] >> 24 not in (1, 2, 3): continue
        f = flags(e)
        if f & (HIDDEN | NOBLOCK): continue
        cells = [e['tile']] + ([tdir(e['tile'], r, 1) for r in range(6)] if f & MULTIHEX else [])
        (door if is_door(e) else block).update(cells)
    return block, door

def flood(start, ok):
    seen = set(start); q = collections.deque(start)
    while q:
        t = q.popleft()
        for r in range(6):
            n = tdir(t, r, 1)
            if n not in seen and ok(n): seen.add(n); q.append(n)
    return seen

def check(objs, ctx=(), margin=4):
    """Зеленые / синие / красные клетки в рамке здания (+margin). ctx — объекты вокруг (забор и т. п.)."""
    if not objs: return None
    xs = [e['tile'] % 200 for e in objs]; ys = [e['tile'] // 200 for e in objs]
    x0, x1, y0, y1 = min(xs) - margin, max(xs) + margin, min(ys) - margin, max(ys) + margin
    def inb(t): return x0 <= t % 200 <= x1 and y0 <= t // 200 <= y1
    block, door = grid(list(objs) + list(ctx))
    edge = [y * 200 + x for x in range(x0, x1 + 1) for y in (y0, y1)] + [y * 200 + x for y in range(y0, y1 + 1) for x in (x0, x1)]
    edge = [t for t in edge if t not in block and t not in door]
    green = flood(edge, lambda t: inb(t) and t not in block and t not in door)
    blue = flood(edge, lambda t: inb(t) and t not in block) - green - door
    allc = {y * 200 + x for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)}
    red = allc - green - blue - block - door
    return dict(green=green, blue=blue, red=red, block=block, door=door, bb=(x0, y0, x1, y1))

def draw(objs, res, out):
    x0, y0, x1, y1 = res['bb']
    cs = [hexxy(y * 200 + x) for x in (x0, x1) for y in (y0, y1)]
    cx = (min(p[0] for p in cs) + max(p[0] for p in cs)) // 2; cy = (min(p[1] for p in cs) + max(p[1] for p in cs)) // 2
    from hexlib import nearest
    c = nearest(cx, cy)
    rx = (max(p[0] for p in cs) - min(p[0] for p in cs)) // 2 + 40; ry = (max(p[1] for p in cs) - min(p[1] for p in cs)) // 2 + 160
    mm = dict(tiles={0: [0] * 10000}, objs=[dict(tile=e['tile'], pid=e['pid'], fid=e['fid'] or PROTO[e['pid']][0], elev=0, rot=e['rot']) for e in objs])
    render.parse = lambda f: mm
    render.render('x', out, c, rad_px=(rx, ry))
    im = Image.open(out).convert('RGB'); dr = ImageDraw.Draw(im)
    X0, Y0 = hexxy(c); X0 -= rx; Y0 -= ry
    for cells, col in ((res['green'], (0, 200, 0)), (res['blue'], (60, 120, 255)), (res['red'], (255, 0, 0)), (res['door'], (255, 255, 0))):
        for t in cells:
            x, y = hexxy(t); x += 16 - X0; y += 8 - Y0
            dr.ellipse((x - 2, y - 1, x + 2, y + 1), fill=col)
    im.save(out)

if __name__ == '__main__':
    rep = []
    img = os.environ.get('IMG')
    for name, L in zip(D['NAMES'], D['LEVELS']):
        for lv in range(4):
            res = check(L[lv])
            if not res: continue
            nb = len([e for e in L[lv] if is_door(e)])
            rep.append(f'{name} ур.{lv + 1}: дверей {nb}, за дверями {len(res["blue"])} кл., недоступно {len(res["red"])} кл.')
            if img: draw(L[lv], res, OUT + f'{D["NAMES"].index(name):02d}_lv{lv + 1}.png')
    open(OUT + 'report.txt', 'w', encoding='utf-8').write('\n'.join(rep))
    print('\n'.join(rep))

def overlaps():
    """Пары зданий, чьи объекты (на любых уровнях) стоят вплотную или друг на друге (ближе 2 клеток)."""
    cells = []
    for name, L in zip(D['NAMES'], D['LEVELS']):
        for lv in range(4):
            if not L[lv]: continue
            own = {e['tile'] for e in L[lv]}
            near = set(own)
            for t in own: near.update(tdir(t, r, 1) for r in range(6))
            cells.append((name, lv + 1, own, near))
    for k in ('trees', 'trash', 'lamps', 'palisade', 'mesh', 'wall', 'outer'):
        for e in D['SYS'][k]:          # каждый объект системы отдельно: дерево на мусоре, фонарь в стене и т. п.
            near = {e['tile']} | {tdir(e['tile'], r, 1) for r in range(6)}
            cells.append((k, e['tile'], {e['tile']}, near))
    out = []
    for i, (a, la, oa, na) in enumerate(cells):
        for b, lb, ob, nb in cells[i + 1:]:
            if a == b or not (na & ob or nb & oa): continue
            if {a, b} <= {'palisade', 'mesh', 'wall', 'outer', 'trees', 'trash', 'lamps'} and not ({a, b} & {'trees', 'trash', 'lamps'}): continue
            if a in ('palisade', 'mesh', 'wall', 'outer') and b in ('palisade', 'mesh', 'wall', 'outer'): continue
            out.append(f'{a} ур.{la} / {b} ур.{lb}')
    return out
if __name__ == '__main__': print('\n'.join(overlaps()) or 'пересечений нет')

def fence_check():
    """Забор целиком: снаружи внутрь при закрытых воротах не пройти, при открытых — пройти."""
    F0, F1 = D['F']; inside = (F0 + F1) // 2 * 201
    out = []
    for name, keys in (('частокол', ('palisade',)), ('сетка', ('mesh',)), ('стена', ('wall',)), ('стена+сетка', ('wall', 'outer')), ('сетка внешняя', ('outer',))):
        objs = [e for k in keys for e in D['SYS'][k]]
        block, door = grid(objs)
        if keys[0] in ('palisade', 'mesh'):     # у них проем без ворот: затыкаем проем, ищем дыры в остальном заборе
            G = D['GX0']; block |= {y * 200 + x for x in range(G - 1, G + 9) for y in (F0, F0 + 1, F1 - 1, F1)}
            name += ' (проем заткнут)'
        ok = lambda t: 0 <= t % 200 < 200 and 0 <= t < 40000 and t not in block
        closed = flood([5 * 200 + 5], lambda t: ok(t) and t not in door and 2 <= t % 200 <= 197 and 2 <= t // 200 <= 197)
        opened = flood([5 * 200 + 5], lambda t: ok(t) and 2 <= t % 200 <= 197 and 2 <= t // 200 <= 197)
        out.append(f'{name}: ворот {len(door)}, закрыто — внутрь {"ПРОХОД" if inside in closed else "нельзя"}, открыто — {"можно" if inside in opened else "НЕЛЬЗЯ"}')
    return out
if __name__ == '__main__': print('\n'.join(fence_check()))
