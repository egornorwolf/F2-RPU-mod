# Город на максимальном уровне: все здания 4 уровня, стена с аркой и внешняя сетка Города-Убежища, турели,
# 12 мест для мусора. Проверяет, что все стоит внутри забора, и поиском пути — что в каждое здание можно зайти.
# Вход: pieces.pkl (cut_pieces.py). Выход: town_max_full.png, town_max.jpg, town_max_report.txt в OUT.
import sys, os, pickle, random, collections, io, contextlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from preprod import place
import render, mapparse, dat2
from render import hexxy
from hexlib import nearest, DT
from PIL import Image, ImageDraw, ImageFont
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/claude-0/m3/'
P = pickle.load(open('/tmp/claude-0/m3/pieces.pkl', 'rb'))
base = mapparse.parse('/home/claude/f2-rpu-mod/build/data/maps/f2mcamp.map')

# картинки существ (турели) лежат в critter.dat
CDAT = '/mnt/project-files/f2mod/game-data/critter.dat'
_odat = render.dat
def _dat(name):
    try: return _odat(name)
    except KeyError:
        if not name.lower().startswith('art\\critters'): raise
        tmp = '/tmp/claude-0/crit_' + name.split('\\')[-1]
        if not os.path.exists(tmp):
            with contextlib.redirect_stdout(io.StringIO()): dat2.extract(CDAT, name, tmp)
        return open(tmp, 'rb').read()
render.dat = _dat

def T(u, y): return y * 200 + (199 - u)
def U(t): return 199 - t % 200, t // 200
objs = []; floor = {}; labels = []; build = {}
NOBLOCK = 0x10
def put(name, u0, y0, label=None, key=None):
    p = P[name]; w = p['bb'][2] - p['bb'][0] + 1; h = p['bb'][3] - p['bb'][1] + 1
    o, f = place(p, 199 - u0 - w + 1, y0); objs.extend(o); floor.update(f)
    if label: labels.append((label, u0 + w // 2, y0 + h // 2))
    build[key or label or name] = (u0, y0, u0 + w - 1, y0 + h - 1, label)
    return w, h
def spr(path, u, y, kind='scenery', flags=0, pid=0x2000001, tag=None):
    objs.append(dict(tile=T(u, y), pid=pid, fid=0, elev=0, flags=flags, sid=-1, path=f'art\\{kind}\\{path}', tag=tag))

# ---- здания 4 уровня (раскладка из town_preview.py)
put('pump', 35, 35, '1 Водокачка'); put('cistern', 52, 38, None, 'Цистерна')
spr('WELL001.frm', 47, 49); spr('well1.frm', 55, 49); spr('gektank5.frm', 44, 46)
put('ranch', 35, 58, '4 Ранчо')
put('workshop', 35, 107, '9 Автомастерская'); spr('crafter1.frm', 33, 130)
put('storage', 36, 132, '10 Склад')
put('garden', 68, 35, '2 Огород', '2 Огород'); put('garden', 68, 64, '3 Огород', '3 Огород')
put('bar', 68, 108, '11 Бар'); put('clinic', 70, 124, '14 Госпиталь')
HOUSES = [(102 + i * 13, 35) for i in range(5)] + [(102 + i * 13, 51) for i in range(3)]
for i, (u, y) in enumerate(HOUSES): put('house', u, y, None, f'Дом {i + 1}')
labels.append(('6-7 Жилье', 128, 50))
put('hero', 143, 50, '8 Дом героя')
put('hall', 102, 68, '12 Ратуша')
put('barracks', 134, 116, '16 Казарма')
for i, (u, y) in enumerate([(84, 152), (92, 154), (108, 152), (116, 154)]): spr('CCART0%d.FRM' % (1 + i % 2), u, y, 'items')
labels.append(('15 Двор каравана', 100, 156))
spr('CONBAR01.frm', 92, 164); spr('vclight1.frm', 95, 164); spr('CONBAR01.frm', 107, 164); spr('vclight1.frm', 104, 164)
rnd = random.Random(3)
for u in range(70, 97, 6):
    for y in (94, 100): spr(rnd.choice(['tree11.frm', 'tree10.frm', 'TREE8.FRM']), u + rnd.randint(-1, 1), y)
labels.append(('13 Сквер', 83, 97))

# ---- стена Города-Убежища (adw) с аркой, внешняя сетка (fence), турели
F0, F1 = 30, 169                       # линия стены: u и y от 30 до 169
XRUN = ['adw1002', 'adw1001', 'adw1000', 'adw1009', 'adw1008', 'adw1007', 'adw1006', 'adw1007', 'adw1004', 'adw1003']
YRUN = ['adw1013', 'adw1014', 'adw1015', 'adw1010', 'adw1011', 'adw1012']
MX = ['fence03', 'fence01', 'fence05', 'fence04']; MY = ['fence15', 'fence16', 'fence17', 'fence18']
ARCH = ['adw1027', 'adw1026', 'adw1025', 'adw1024', 'adw1023', 'adw1022', 'adw1021', 'adw1020']   # x растет
ARCH_NB = {2, 3, 4, 5, 6}; ARCH_BLOCK = {2, 6}   # 1021–1025 без блока, по краям прохода невидимые блоки
GX0 = 96                                          # x первой клетки арки на южной стене
wall = {}
for x in range(F0, F1 + 1):
    for y in (F0, F1): wall[(x, y)] = (XRUN[x % 10], 0)
for y in range(F0, F1 + 1):
    for x in (F0, F1): wall[(x, y)] = (YRUN[y % 6], 0)
for i, a in enumerate(ARCH):
    wall[(GX0 + i, F1)] = (a, NOBLOCK if i in ARCH_NB else 0)
for (x, y), (a, fl) in wall.items():
    objs.append(dict(tile=y * 200 + x, pid=0x3000001, fid=0, elev=0, flags=fl, sid=-1, path=f'art\\walls\\{a}.frm', tag='wall'))
for i in ARCH_BLOCK:
    objs.append(dict(tile=F1 * 200 + GX0 + i, pid=0x5000002, fid=0, elev=0, flags=0, sid=-1, path=None, tag='block'))
M0, M1 = F0 - 4, F1 + 4                 # внешняя сетка в 4 клетках от стены, как в Городе-Убежище
mesh = {}
for x in range(M0, M1 + 1):
    for y in (M0, M1):
        if not (y == M1 and GX0 - 2 <= x <= GX0 + 11): mesh[(x, y)] = MX[x % 4]
for y in range(M0, M1 + 1):
    for x in (M0, M1): mesh[(x, y)] = MY[y % 4]
for y in range(F1 + 1, M1):             # коридор от арки стены к воротам в сетке закрыт с боков: в коридор турелей не пройти
    mesh[(GX0 + 2, y)] = MY[y % 4]; mesh[(GX0 + 6, y)] = MY[y % 4]
# большие ворота Города-Убежища в линии сетки (vctydwtn: vgat001–014 и створки valtgate/valtgat2), x растет
VGAT = [('vgat014', 0), ('vgat013', 0), ('vgat012', 0), ('vgat011', 0), ('vgat010', NOBLOCK), ('vgat009', NOBLOCK), ('vgat008', NOBLOCK),
        ('vgat007', 0), ('vgat006', 0), ('vgat005', 0), ('vgat004', 0), ('vgat003', 0), ('vgat002', 0), ('vgat001', 0)]
for i, (a, fl) in enumerate(VGAT):
    objs.append(dict(tile=M1 * 200 + GX0 - 2 + i, pid=0x3000004, fid=0, elev=0, flags=fl, sid=-1, path=f'art\\walls\\{a}.frm', tag='wall'))
for dx, a in ((2, 'valtgat2'), (4, 'valtgate')):
    objs.append(dict(tile=M1 * 200 + GX0 - 2 + dx, pid=0x2000005, fid=0, elev=0, flags=NOBLOCK, sid=-1, path=f'art\\scenery\\{a}.frm', tag='gate'))
for (x, y), a in mesh.items():
    objs.append(dict(tile=y * 200 + x, pid=0x3000003, fid=0, elev=0, flags=0, sid=-1, path=f'art\\walls\\{a}.frm', tag='mesh'))
TUR = []
R0, R1 = F0 - 2, F1 + 2                 # линия турелей между стеной и сеткой
ring = [(x, R0) for x in range(R0, R1 + 1, 12)] + [(x, R1) for x in range(R0, R1 + 1, 12)] + \
       [(R0, y) for y in range(R0 + 12, R1, 12)] + [(R1, y) for y in range(R0 + 12, R1, 12)]
for x, y in ring:
    if y == R1 and GX0 - 3 <= x <= GX0 + 12: continue
    TUR.append((x, y))
TUR += [(GX0 - 4, R1), (GX0 + 13, R1)]   # по одной у ворот
for x, y in TUR:
    objs.append(dict(tile=y * 200 + x, pid=0x1000001, fid=0, elev=0, flags=0, sid=-1, path='art\\critters\\MAGUNNAA.FRM', rot=3, tag='turret'))

# ---- проходимость
def nbrs(t):
    for d in DT[(t % 200) & 1]:
        n = t + d
        if 0 <= n < 40000 and abs(n % 200 - t % 200) <= 1: yield n
DOORS = set()
def blocked_set(extra=()):
    b = set()
    for o in objs:
        if o.get('elev', 0) != 0 or o.get('tag') == 'turret' and False: pass
        if o['flags'] & NOBLOCK: continue
        if o['pid'] >> 24 == 2 and 'path' not in o:
            try:
                if mapparse.subtype(o['pid']) == 0: DOORS.add(o['tile']); continue   # двери открываются
            except Exception: pass
        b.add(o['tile'])
    b.update(extra); return b
def reach(start, blk):
    seen = {start}; q = collections.deque([start])
    while q:
        t = q.popleft()
        for n in nbrs(t):
            if n not in seen and n not in blk: seen.add(n); q.append(n)
    return seen
START = (M1 + 3) * 200 + GX0 + 4        # снаружи, напротив арки
def check(extra=()):
    blk = blocked_set(extra); R = reach(START, blk)
    shut = blk | DOORS; Rshut = reach(START, shut)
    res = {}
    for k, (u0, y0, u1, y1, lab) in build.items():
        tiles = [T(u, y) for u in range(u0, u1 + 1) for y in range(y0, y1 + 1)]
        free = [t for t in tiles if t not in blk]
        inner = [t for t in free if t not in Rshut]          # закрытые помещения (за дверями или без входа)
        ok_in = [t for t in inner if t in R]
        near = any(t in R for t in free)
        res[k] = dict(inner=len(inner), inner_ok=len(ok_in), near=near)
    return R, blk, res

# ---- закрытые комнаты без двери: прорубаем проход (убираем один пролет внутренней стены)
FIXED = []
def open_passage(k):
    u0, y0, u1, y1, _ = build[k]
    blk = blocked_set(); R = reach(START, blk); Rshut = reach(START, blk | DOORS)
    box = {T(u, y) for u in range(u0, u1 + 1) for y in range(y0, y1 + 1)}
    closed = {t for t in box if t not in blk and t not in R}
    if not closed: return False
    cu, cy = (u0 + u1) / 2, (y0 + y1) / 2
    best = None
    for o in objs:
        t = o['tile']
        if t not in box or o['pid'] >> 24 != 3 or o['flags'] & NOBLOCK: continue
        ns = list(nbrs(t))
        if any(n in closed for n in ns) and any(n in R for n in ns):
            u, y = U(t); d = (u - cu) ** 2 + (y - cy) ** 2
            if best is None or d < best[0]: best = (d, o)
    if not best: return False
    t = best[1]['tile']
    objs[:] = [o for o in objs if not (o['tile'] == t and o['pid'] >> 24 in (3, 5))]
    FIXED.append((k, t)); return True
for k in list(build):
    for _ in range(3):
        if not open_passage(k): break
# ---- дорожки: плитка Города-Убежища (brick33, BRICK20), 1 квадрат пола = 2x2 клетки
def inbox(u, y, m=0):
    for k, (u0, y0, u1, y1, _) in build.items():
        if u0 - m <= u <= u1 + m and y0 - m <= y <= y1 + m: return k
    return None
def sq_hexes(sx, sy): return [(199 - (2 * sx + dx), 2 * sy + dy) for dx in (0, 1) for dy in (0, 1)]
def sq_ok(sx, sy): return all(F0 < u < F1 and F0 < y < F1 and not inbox(u, y) for u, y in sq_hexes(sx, sy))
MAIN = set()
for sy in range(16, 85):                      # главная дорога от ворот на север, клетки u 98–101 (4 клетки)
    for sx in (49, 50):
        if sq_ok(sx, sy): MAIN.add((sx, sy))
for sx in range(16, 84):                      # поперечная, клетки y 104–107 (4 клетки, у мастерской 2)
    for sy in (52, 53):
        if sq_ok(sx, sy): MAIN.add((sx, sy))
PATH = set(MAIN); BRANCH = set()
blocked_set()                                 # заполняет DOORS
def bfs_sq(starts):
    prev = {s: None for s in starts}; q = collections.deque(starts)
    while q:
        s = q.popleft()
        if s in PATH:
            out = []
            while s is not None and s not in starts: out.append(s); s = prev[s]
            if s is not None: out.append(s)
            return [x for x in out if x not in PATH]
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (s[0] + dx, s[1] + dy)
            if n not in prev and (n in PATH or sq_ok(*n)): prev[n] = s; q.append(n)
    return []
for k, (u0, y0, u1, y1, _) in build.items():
    if k == 'Цистерна': continue
    ds = [t for t in DOORS if u0 <= U(t)[0] <= u1 and y0 <= U(t)[1] <= y1]
    seeds = set()
    for t in ds:                              # двери на краю здания: клетки снаружи рядом с дверью
        for n in list(nbrs(t)) + [m for n in nbrs(t) for m in nbrs(n)]:
            u, y = U(n)
            if not inbox(u, y):
                sq = ((199 - u) // 2, y // 2)
                if sq_ok(*sq): seeds.add(sq)
    if not seeds:                             # открытые постройки: любой квадрат вплотную к зданию
        for u in range(u0 - 2, u1 + 3):
            for y in range(y0 - 2, y1 + 3):
                sq = ((199 - u) // 2, y // 2)
                if sq_ok(*sq): seeds.add(sq)
    br = bfs_sq(list(seeds))
    if len(br) <= 30: BRANCH.update(br); PATH.update(br)
PATHHEX = {h for sq in PATH for h in sq_hexes(*sq)}

_, _, res_ref = check()
# ---- убранство: фонари, деревья, кусты, стрельбище; ничего не ставим на дорожки и вплотную к зданиям
occupied = {o['tile'] for o in objs}
DOORUY = [U(t) for t in DOORS]
DECO = []
def free_spot(u, y, m=1, door=3, gap=0):
    if not (F0 + 1 < u < F1 - 1 and F0 + 1 < y < F1 - 1): return False
    if inbox(u, y, m) or (u, y) in PATHHEX or T(u, y) in occupied: return False
    if gap and any((u + a, y + b) in PATHHEX for a in range(-gap, gap + 1) for b in range(-gap, gap + 1)): return False
    return all(abs(u - a) + abs(y - b) > door for a, b in DOORUY)
def deco(name, u, y, m=1, kind='scenery', tag='deco', tries=((0, 0),), gap=0):
    if gap == 0 and ('tree' in name): gap = 2                   # деревья не закрывают дорожки
    for du, dy in tries:
        if free_spot(u + du, y + dy, m, gap=gap):
            spr(name, u + du, y + dy, kind, tag=tag); occupied.add(T(u + du, y + dy)); DECO.append(objs[-1]); return (u + du, y + dy)
    return None
NEAR = [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (0, 2), (0, -2), (2, 0), (-2, 0)]
LIGHT = os.environ.get('LIGHT', 'electric')
LAMP = ('strlit1.frm', 'strlit3.frm') if LIGHT == 'electric' else ('barrel.frm', 'barrel.frm')
lamps = []
# фонарь НКР нарисован в 4 поворотах: плечо (на экране) влево-назад, влево-вперед, вправо-назад, вправо-вперед
ARM = {'strlit1.frm': (-2, -1), 'strlit2.frm': (-2, 1), 'strlit3.frm': (2, -1), 'strlit4.frm': (2, 1)}
def orient(p):
    """Поворачивает только что поставленный фонарь плечом к ближайшей клетке дорожки."""
    if not p or LIGHT != 'electric': return
    u, y = p
    pu, py = min(PATHHEX, key=lambda h: (h[0] - u) ** 2 + (h[1] - y) ** 2)
    (x0, y0), (x1, y1) = hexxy(T(u, y)), hexxy(T(pu, py))
    vx, vy = x1 - x0, y1 - y0
    best = max(ARM, key=lambda k: ARM[k][0] * vx + ARM[k][1] * 2 * vy)
    DECO[-1]['path'] = 'art\\scenery\\' + best
for i, y in enumerate(range(38, 168, 12)):                      # вдоль главной дороги, через сторону
    p = deco(LAMP[i % 2], 97 if i % 2 == 0 else 102, y, tries=NEAR); orient(p)
    if p: lamps.append(p)
for i, u in enumerate(range(36, 166, 12)):                      # вдоль поперечной
    if 94 <= u <= 105: continue
    p = deco(LAMP[i % 2], u, 103 if i % 2 == 0 else 108, tries=NEAR); orient(p)
    if p: lamps.append(p)
for u, y in [(88, 160), (112, 160), (150, 150), (130, 150), (78, 150), (60, 150), (140, 82), (66, 36), (40, 52), (166, 112)]:
    p = deco(LAMP[0], u, y, tries=NEAR); orient(p)             # двор каравана, стрельбище, углы
    if p: lamps.append(p)
# правки Егора по номерам фонарей (Ф1…Ф23 на town_lamps.jpg, 2026-10-05)
if LIGHT == 'electric':
    CW = {'strlit1.frm': 'strlit3.frm', 'strlit3.frm': 'strlit4.frm', 'strlit4.frm': 'strlit2.frm', 'strlit2.frm': 'strlit1.frm'}   # по часовой
    CCW = {v: k for k, v in CW.items()}
    ROT = {5: CW, 16: lambda n: CW[CW[n]], 17: CCW, 18: CCW}
    def lamp_obj(i): return next(o for o in DECO if o['tile'] == T(*lamps[i - 1]))
    for i, r in ROT.items():
        o = lamp_obj(i); n = o['path'].split('\\')[-1]
        o['path'] = 'art\\scenery\\' + (r(n) if callable(r) else r[n])
    def near_path(u0, y0):
        """Ближайшая к точке свободная клетка вплотную к дорожке (не в здании, не у двери)."""
        sp = set()
        for (u, y) in PATHHEX:
            for du, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p = (u + du, y + dy)
                if free_spot(*p, m=0, door=2): sp.add(p)
        return min(sp, key=lambda p: (p[0] - u0) ** 2 + (p[1] - y0) ** 2)
    # куда перенести: Ф8 и Ф19 — западная часть поперечной дороги, Ф22 — поперечная у сквера,
    # Ф14 и Ф15 — восточная сторона главной дороги на севере, Ф20 — главная дорога у ворот, восточная сторона, Ф23 — к дорожке
    MOVE = {8: (44, 103), 19: (60, 103), 22: (78, 103), 14: (102, 50), 15: (102, 74), 20: (102, 162), 23: None}
    for i, tgt in MOVE.items():
        o = lamp_obj(i); DECO.remove(o); objs.remove(o); occupied.discard(o['tile'])
        best = near_path(*(tgt or lamps[i - 1]))
        lamps[i - 1] = best
        q = deco('strlit1.frm', *best, m=0); orient(q)
# стрельбище у южной стены (юго-восточный угол): мишени — дверь машины на бочке (weed05) у самой стены,
# за ними сено (HAYBED), огневой рубеж — столы с ящиками патронов; стреляют в сторону стены
range_parts = []
for u in range(128, 166, 6):
    for name, uu, yy, kind in (('posts.frm' if u % 12 == 8 else 'weed05.frm', u, 163, 'scenery'), ('HAYBED05.frm', u + 1, 166, 'scenery'),
                               ('table6.frm', u, 153, 'scenery'), ('ammobox1.frm' if u % 12 else 'ammobox3.frm', u + 2, 152, 'items')):
        p = deco(name, uu, yy, m=0, kind=kind, tag='range')
        if p: range_parts.append((name, p))
deco('wepnbox.frm', 124, 152, m=0, kind='items', tag='range'); deco('boxes1.frm', 124, 156, m=0, tag='range')
labels.append(('17 Стрельбище', 146, 160))
# деревья и кусты: вторая аллея вдоль главной дороги, вдоль поперечной, по свободным местам
TREES = ['tree10.frm', 'tree11.frm', 'treea.frm', 'tree10.frm', 'tree11.frm', 'tree7.frm', 'tree8.frm']
trees = 0
for y in range(36, 166, 7):                                     # аллея по обе стороны главной дороги
    for u in (95, 104):
        if deco(rnd.choice(TREES), u, y + (3 if u == 104 else 0), tries=NEAR): trees += 1
for u in range(40, 166, 10):
    for y in (101, 110):
        if deco(rnd.choice(TREES), u + (5 if y == 110 else 0), y, tries=NEAR): trees += 1
rt = random.Random(11); placed = []
for _ in range(900):
    u, y = rt.randint(F0 + 3, F1 - 3), rt.randint(F0 + 3, F1 - 3)
    if 120 <= u and 148 <= y: continue                          # стрельбище
    if 78 <= u <= 118 and 148 <= y: continue                    # двор каравана
    if any(abs(u - a) + abs(y - b) < 7 for a, b in placed): continue
    bush = rt.random() < 0.4
    if deco(rt.choice(['bush1.frm', 'bush2.frm', 'bush3.frm']) if bush else rt.choice(TREES), u, y, m=2):
        placed.append((u, y)); trees += 0 if bush else 1
bushes = len(placed)
# всё убранство не должно перекрывать входы: если перекрыло, снимаем последнее поставленное
def worse(r): return any(r[k]['inner_ok'] < res_ref[k]['inner_ok'] or (res_ref[k]['near'] and not r[k]['near']) for k in r)
removed = 0
while worse(check()[2]):
    o = DECO.pop(); objs.remove(o); removed += 1

# ---- мусор: на видных местах у дорог, не на проходе и не у дверей; во дворе каравана большая куча из 5
TRASH = ['junk2', 'njunk5', 'njunk6', 'trash1', 'trash3', 'trash4', 'pipes2', 'junk1']
def near_label(u, y):
    best = min(build.items(), key=lambda kv: (max(kv[1][0] - u, 0, u - kv[1][2]) ** 2 + max(kv[1][1] - y, 0, y - kv[1][3]) ** 2))
    return best[0]
def road_of(u, y):
    for sq in MAIN:
        if any(abs(u - a) <= 1 and abs(y - b) <= 1 for a, b in sq_hexes(*sq)): return 'у главной дороги' if sq[0] in (49, 50) and sq[1] not in (52, 53) else 'у поперечной дороги'
    return 'у дорожки'
cand = []
for (u, y) in PATHHEX:
    for du, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        a, b = u + du, y + dy
        if free_spot(a, b, m=1, door=4) and (a, b) not in cand:
            score = 0 if road_of(a, b) != 'у дорожки' else 1
            cand.append((a, b, score))
rt2 = random.Random(5); rt2.shuffle(cand); cand.sort(key=lambda c: c[2])
R, blk, res_ref = check()
trash = []; WANT = 30
for a, b, sc in cand:
    if len(trash) >= WANT: break
    if any(abs(a - x) + abs(b - y) < 10 for _, (x, y) in trash): continue
    if 78 <= a <= 118 and 148 <= b: continue
    t = T(a, b)
    if t in blk or t not in R: continue
    r2 = check([T(*p) for _, p in trash] + [t])[2]
    if worse(r2): continue
    trash.append((f'{road_of(a, b)}, {near_label(a, b)}', (a, b)))
for i, (name, (a, b)) in enumerate(trash):
    spr(TRASH[i % len(TRASH)] + '.frm', a, b, tag='trash'); occupied.add(T(a, b))
PILE = []
for a, b in [(84, 162), (85, 161), (85, 163), (86, 162), (84, 164), (86, 160), (83, 163)]:
    if len(PILE) >= 5: break
    if free_spot(a, b, m=0, door=2):
        r2 = check([T(a, b)])[2]
        if not worse(r2):
            spr(['junk2', 'pipes2', 'njunk5', 'junk1', 'njunk6'][len(PILE)] + '.frm', a, b, tag='trash'); occupied.add(T(a, b)); PILE.append((a, b))
R, blk, res = check()
# свободное место внутри стены
inside = [(u, y) for u in range(F0 + 1, F1) for y in range(F0 + 1, F1)]
n_box = sum(1 for u, y in inside if inbox(u, y)); n_path = sum(1 for h in inside if h in PATHHEX)
n_free = sum(1 for u, y in inside if not inbox(u, y) and (u, y) not in PATHHEX and T(u, y) not in blk)


# ---- все ли внутри забора
out_of = []
for o in objs:
    if o.get('tag') in ('wall', 'mesh', 'turret', 'block', 'gate'): continue
    u, y = U(o['tile'])
    if not (F0 < u < F1 and F0 < y < F1): out_of.append((o.get('path') or render.fidpath(o['fid']), u, y))

# ---- картинка
mm = dict(base); mm['objs'] = objs
t = list(base['tiles'][0]); rr = random.Random(7)
t = [v if (v & 0xffff) not in (0, 1, 659, 179, 180) else (v & 0xffff0000) | rr.choice(range(191, 199)) for v in t]
rp = random.Random(9)
for sq in PATH:
    if sq not in floor: t[sq[1] * 100 + sq[0]] = (t[sq[1] * 100 + sq[0]] & 0xffff0000) | (2261 if rp.random() < 0.2 else 2274)
for (sx, sy), f in floor.items(): t[sy * 100 + sx] = f
mm['tiles'] = {0: t}
render.parse = lambda f: mm
pts = [hexxy(T(a, b)) for a in (M0, M1) for b in (M0, M1)]
cx = (min(p[0] for p in pts) + max(p[0] for p in pts)) // 2; cy = (min(p[1] for p in pts) + max(p[1] for p in pts)) // 2
c = nearest(cx, cy); rx = (max(p[0] for p in pts) - min(p[0] for p in pts)) // 2 + 120; ry = (max(p[1] for p in pts) - min(p[1] for p in pts)) // 2 + 260
render.render('x', OUT + 'town_max_full.png', c, rad_px=(rx, ry))
im = Image.open(OUT + 'town_max_full.png'); clean = im.copy(); d = ImageDraw.Draw(im)
X0, Y0 = hexxy(c); X0 -= rx; Y0 -= ry
def scr(u, y): x, yy = hexxy(T(u, y)); return x + 16 - X0, yy + 8 - Y0
fnt = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 44)
fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 34)
for i, (name, tt) in enumerate(trash + [('куча у каравана', p) for p in PILE[:1]]):
    lbl = f'М{i + 1}' if i < len(trash) else 'Куча'
    x, yy = scr(*tt); d.ellipse((x - 26, yy - 26, x + 26, yy + 26), outline=(255, 60, 60), width=6)
    d.text((x + 30, yy - 20), lbl, font=fs, fill=(255, 90, 90), stroke_width=4, stroke_fill=(0, 0, 0))
for lb, u, y in labels:
    x, yy = scr(u, y); d.text((x - len(lb) * 12, yy - 140), lb, font=fnt, fill=(255, 255, 120), stroke_width=4, stroke_fill=(0, 0, 0))
# фонари с номерами: общий план и лист крупных вырезок (номер = Ф1…, в подписи поворот)
fl = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 26)
LAMPOBJ = {o['tile']: o['path'].split('\\')[-1] for o in objs if o.get('tag') == 'deco' and ('strlit' in o['path'] or 'barrel.frm' in o['path'])}
lampov = clean.copy(); dl = ImageDraw.Draw(lampov); cells = []
for i, (u, y) in enumerate(lamps):
    x, yy = scr(u, y)
    dl.ellipse((x - 30, yy - 30, x + 30, yy + 30), outline=(80, 200, 255), width=7)
    dl.text((x + 34, yy - 24), f'Ф{i + 1}', font=fs, fill=(120, 220, 255), stroke_width=4, stroke_fill=(0, 0, 0))
    c = clean.crop((x - 220, yy - 230, x + 220, yy + 90)).copy(); dc = ImageDraw.Draw(c)
    dc.ellipse((220 - 12, 230 - 9, 220 + 12, 230 + 9), outline=(80, 200, 255), width=3)
    dc.text((8, 6), f'Ф{i + 1}  {LAMPOBJ.get(T(u, y), "?")[:-4]}  u{u} y{y}', font=fl, fill=(120, 220, 255), stroke_width=4, stroke_fill=(0, 0, 0))
    cells.append(c)
sm2 = lampov.copy(); sm2.thumbnail((2600, 2600)); sm2.save(OUT + 'town_lamps_map.jpg', quality=88)
W = 5; sheet = Image.new('RGB', (440 * W, 320 * ((len(cells) + W - 1) // W)), (0, 0, 0))
for i, c in enumerate(cells): sheet.paste(c, ((i % W) * 440, (i // W) * 320))
sheet.save(OUT + 'town_lamps.jpg', quality=88)
im.save(OUT + 'town_max_full.png')
sm = im.copy(); sm.thumbnail((2600, 2600)); sm.save(OUT + 'town_max.jpg', quality=88)
gx, gy = scr(199 - (GX0 + 5), M1 - 2); im.crop((gx - 700, gy - 450, gx + 700, gy + 300)).save(OUT + 'town_max_gate.jpg', quality=90)

# ---- отладочные вырезки по зданиям без входа
DBG = os.environ.get('DBG')
if DBG:
    blk2 = blocked_set(); shut = blk2 | DOORS; Rshut = reach(START, shut)
    for k, (u0, y0, u1, y1, lab) in build.items():
        if res[k]['inner'] and res[k]['inner_ok'] < res[k]['inner']:
            mk = []
            for u in range(u0 - 3, u1 + 4):
                for y in range(y0 - 3, y1 + 4):
                    tt = T(u, y)
                    if tt in DOORS: mk.append((tt, 'D', (80, 160, 255)))
                    elif tt in blk2: continue
                    elif tt in R: mk.append((tt, '', (60, 255, 60)))
                    else: mk.append((tt, '', (255, 40, 40)))
            cu, cy2 = (u0 + u1) // 2, (y0 + y1) // 2
            render.render('x', OUT + f'dbg_{k}.png', T(cu, cy2), rad_px=(520, 380), marks=mk)
# ---- отчет
L = ['Город 4 уровня: проверка', '']
L.append(f'Вне забора (кроме стены, сетки, турелей, ворот): {len(out_of)}')
for p, u, y in out_of[:20]: L.append(f'  {p} u{u} y{y}')
L += ['', 'Входы (поиск пути от ворот, двери открываются):']
for k, r in res.items():
    if r['inner']: st = 'вход есть' if r['inner_ok'] == r['inner'] else f'НЕТ входа в {r["inner"] - r["inner_ok"]} из {r["inner"]} клеток помещений'
    else: st = 'открытая постройка, подход есть' if r['near'] else 'НЕТ подхода'
    L.append(f'  {k}: {st} (помещения {r["inner"]} кл.)')
L += ['', 'Прорублены проходы (убран пролет стены):']
for k, t in FIXED: L.append(f'  {k}: клетка {t} (u{U(t)[0]}, y{U(t)[1]})')
L += ['', f'Свободное место внутри стены: {n_free} клеток из {len(inside)} ({100 * n_free // len(inside)}%); здания {n_box}, дорожки {n_path}',
      f'Дорожки: главная и поперечная по 4 клетки (2 квадрата пола), к зданиям по 2 клетки; квадратов {len(PATH)}',
      f'Фонари ({LIGHT}): {len(lamps)}; деревья и кусты: {len([o for o in DECO if "tree" in o["path"] or "bush" in o["path"]])}; снято из-за проходов: {removed}',
      f'Стрельбище: {len(range_parts)} предметов (мишени, сено, столы, патроны)', '', f'Места мусора ({len(trash)} + куча из {len(PILE)} у каравана):']
for i, (name, (a, b)) in enumerate(trash):
    L.append(f'  М{i + 1} {name}: клетка {T(a, b)} (u{a}, y{b})')
L.append('  Куча у каравана: ' + ', '.join(f'{T(a, b)} (u{a}, y{b})' for a, b in PILE))
L.append(''); L.append(f'Турелей: {len(TUR)}')
open(OUT + 'town_max_report.txt', 'w', encoding='utf-8').write('\n'.join(L)); print('\n'.join(L)); print(im.size)
