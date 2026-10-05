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
put('workshop', 35, 105, '9 Автомастерская'); spr('crafter1.frm', 33, 128)
put('storage', 36, 130, '10 Склад')
put('garden', 68, 35, '2 Огород', '2 Огород'); put('garden', 68, 64, '3 Огород', '3 Огород')
put('bar', 68, 108, '11 Бар'); put('clinic', 70, 124, '14 Госпиталь')
HOUSES = [(102 + i * 13, 35) for i in range(5)] + [(102 + i * 13, 51) for i in range(3)]
for i, (u, y) in enumerate(HOUSES): put('house', u, y, None, f'Дом {i + 1}')
labels.append(('6-7 Жилье', 128, 50))
put('hero', 143, 50, '8 Дом героя')
put('hall', 102, 68, '12 Ратуша')
put('barracks', 128, 116, '16 Казарма')
for i, (u, y) in enumerate([(84, 152), (92, 154), (108, 152), (116, 154)]): spr('CCART0%d.FRM' % (1 + i % 2), u, y, 'items')
labels.append(('15 Двор каравана', 100, 156))
spr('CONBAR01.frm', 92, 164); spr('vclight1.frm', 95, 164); spr('CONBAR01.frm', 107, 164); spr('vclight1.frm', 104, 164)
rnd = random.Random(3)
for u in range(70, 97, 6):
    for y in (94, 100): spr(rnd.choice(['tree11.frm', 'tree10.frm', 'TREE8.FRM']), u + rnd.randint(-1, 1), y)
labels.append(('13 Сквер', 83, 97)); labels.append(('17 Охрана, тир', 112, 140))
for y in range(36, 160, 8): spr('tree11.frm', 97, y)

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
# ---- 12 мест для мусора (по участкам из robots.md), выбираем свободные клетки, которые не мешают проходу
TRASH = ['junk2', 'njunk5', 'njunk6', 'trash1', 'trash3', 'trash4', 'pipes2', 'junk1']
def bxy(k): u0, y0, u1, y1, _ = build[k]; return u0, y0, u1, y1
SPOTS = []
for i in range(4):   # промежутки между домами северного ряда
    a = HOUSES[i]; SPOTS.append((f'между домами {i + 1} и {i + 2}', a[0] + 11, a[1] + 4, a[0] + 12, a[1] + 9))
for i in range(5, 7):
    a = HOUSES[i]; SPOTS.append((f'между домами {i + 1} и {i + 2}', a[0] + 11, a[1] + 4, a[0] + 12, a[1] + 9))
u0, y0, u1, y1 = bxy('11 Бар'); SPOTS.append(('у западной стены бара', u0 - 3, y0 + 2, u0 - 1, y1 - 2))
u0, y0, u1, y1 = bxy('10 Склад'); SPOTS.append(('за складом', u0 - 3, y0 + 2, u0 - 1, y1 - 2))
u0, y0, u1, y1 = bxy('9 Автомастерская'); SPOTS.append(('угол двора автомастерской', u0 + 1, y1 - 2, u0 + 6, y1))
u0, y0, u1, y1 = bxy('16 Казарма'); SPOTS.append(('за казармой', u1 + 1, y0 + 4, u1 + 3, y1 - 4))
SPOTS.append(('угол двора каравана', 80, 158, 86, 162))
u0, y0, u1, y1 = bxy('4 Ранчо'); SPOTS.append(('за загоном ранчо', u1 + 1, y0 + 30, u1 + 3, y1 - 2))
R, blk, res0 = check()
trash = []
for name, a0, b0, a1, b1 in SPOTS:
    pick = None
    for u in range(a0, a1 + 1):
        for y in range(b0, b1 + 1):
            t = T(u, y)
            if t in blk or t not in R or any(t == x[1] for x in trash): continue
            R2, _, r2 = check([x[1] for x in trash] + [t])
            if all(r2[k]['inner_ok'] >= res0[k]['inner_ok'] and (r2[k]['near'] or not res0[k]['near']) for k in r2):
                pick = t; break
        if pick: break
    trash.append((name, pick))
for i, (name, t) in enumerate(trash):
    if t: spr(TRASH[i % len(TRASH)] + '.frm', *U(t), tag='trash')
R, blk, res = check()

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
for (sx, sy), f in floor.items(): t[sy * 100 + sx] = f
mm['tiles'] = {0: t}
render.parse = lambda f: mm
pts = [hexxy(T(a, b)) for a in (M0, M1) for b in (M0, M1)]
cx = (min(p[0] for p in pts) + max(p[0] for p in pts)) // 2; cy = (min(p[1] for p in pts) + max(p[1] for p in pts)) // 2
c = nearest(cx, cy); rx = (max(p[0] for p in pts) - min(p[0] for p in pts)) // 2 + 120; ry = (max(p[1] for p in pts) - min(p[1] for p in pts)) // 2 + 260
render.render('x', OUT + 'town_max_full.png', c, rad_px=(rx, ry))
im = Image.open(OUT + 'town_max_full.png'); d = ImageDraw.Draw(im)
X0, Y0 = hexxy(c); X0 -= rx; Y0 -= ry
def scr(u, y): x, yy = hexxy(T(u, y)); return x + 16 - X0, yy + 8 - Y0
fnt = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 44)
fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 34)
for i, (name, tt) in enumerate(trash):
    if not tt: continue
    x, yy = scr(*U(tt)); d.ellipse((x - 26, yy - 26, x + 26, yy + 26), outline=(255, 60, 60), width=6)
    d.text((x + 30, yy - 20), f'М{i + 1}', font=fs, fill=(255, 90, 90), stroke_width=4, stroke_fill=(0, 0, 0))
for lb, u, y in labels:
    x, yy = scr(u, y); d.text((x - len(lb) * 12, yy - 140), lb, font=fnt, fill=(255, 255, 120), stroke_width=4, stroke_fill=(0, 0, 0))
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
L += ['', 'Места мусора:']
for i, (name, tt) in enumerate(trash):
    L.append(f'  М{i + 1} {name}: ' + (f'клетка {tt} (u{U(tt)[0]}, y{U(tt)[1]})' if tt else 'НЕ НАЙДЕНО'))
L.append(''); L.append(f'Турелей: {len(TUR)}')
open(OUT + 'town_max_report.txt', 'w', encoding='utf-8').write('\n'.join(L)); print('\n'.join(L)); print(im.size)
