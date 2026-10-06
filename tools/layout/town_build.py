# Тестовая стройка города (песочница): все здания 1-4 уровня, деревья, мусор, свет, забор, турели.
# Вход: town_max.pkl (town_max.py, NOIMG=1), pieces.pkl (cut_pieces.py), карты F2/RPU.
# Выход: scripts_src/test/f2mtblay.h (расстановка для скриптов песочницы), build/test/maps/f2mtown.map,
# картинки уровней в OUT (town_lv1..4.jpg) и отчет.
# Использование: town_build.py [OUT]
import sys, os, pickle, struct, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render, mapparse
from render import hexxy, fidpath
from preprod import load, ov_origin, cut, main_part, place, rebuild
from hexlib import nearest
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/claude-0/tb/'
D = pickle.load(open(OUT + 'town_max.pkl', 'rb'))
P = pickle.load(open('/tmp/claude-0/m3/pieces.pkl', 'rb'))
def T(u, y): return y * 200 + (199 - u)
def U(t): return 199 - t % 200, t // 200
NOBLOCK = 0x10

# ---- прототипы: путь картинки -> PID, флаги и свет прототипа
KINDS = {0: 'items', 2: 'scenery', 3: 'walls'}
PROTO = {}      # pid -> (fid, flags, light dist, light intensity, subtype)
BYPATH = {}     # (тип, имя файла) -> pid
for t, k in KINDS.items():
    for i, n in enumerate(mapparse.lst(k)):
        n = n.strip()
        if not n: continue
        try: b = mapparse.rd(f'proto\\{k}\\{n}')
        except Exception: continue
        pid, _, fid, ld, li, fl = struct.unpack_from('>6i', b, 0)
        st = struct.unpack_from('>i', b, 32)[0] if t in (0, 2) else -1
        PROTO[pid] = (fid, fl & 0xffffffff, ld, li, st)
        try: name = (fidpath(fid) or '').split('\\')[-1].lower()
        except Exception: name = ''
        BYPATH.setdefault((t, name), pid)
def pid_of(path):
    kind = path.split('\\')[1]; t = {v: k for k, v in KINDS.items()}[kind]
    return BYPATH[(t, path.split('\\')[-1].lower())]

# Флаги, которые карта может менять у объекта: плоский, без блока, прозрачность, свет и выстрелы насквозь
FLAG_MASK = 0x8 | 0x10 | 0x0000C000 | 0x000F0000 | 0x10000000 | 0x20000000 | 0x80000000

def norm(o):
    """Объект для скрипта: pid, клетка, поворот, кадр и отличия от прототипа (картинка, флаги, свет)."""
    if o.get('path'):
        pid = pid_of(o['path']); fid = PROTO[pid][0]
        e = dict(pid=pid, tile=o['tile'], rot=o.get('rot', 0), frame=0, fid=None,
                 fset=o.get('flags', 0) & FLAG_MASK & ~PROTO[pid][1], fclr=0, light=None)
    else:
        pid = o['pid']; pf = PROTO[pid]
        e = dict(pid=pid, tile=o['tile'], rot=o.get('rot', 0) % 6, frame=o.get('frame', 0), fid=None, fset=0, fclr=0, light=None)
        if (o['fid'] & 0xffffff) != (pf[0] & 0xffffff): e['fid'] = o['fid']
        d = (o['flags'] ^ pf[1]) & FLAG_MASK
        e['fset'] = d & o['flags']; e['fclr'] = d & pf[1]
        if 'ld' in o and (o['ld'], o['li']) != (pf[2], pf[3]) and o['li'] > 0: e['light'] = (o['ld'], round(o['li'] * 100 / 65536))
    if e['frame'] < 0 or e['frame'] > 100: e['frame'] = 0
    return e

def keep(o):
    """Подбираемые вещи из чужих карт не берем: только контейнеры (сундуки, ящики, повозки), декорации и стены."""
    pid = o['pid'] if not o.get('path') else pid_of(o['path'])
    if pid >> 24 == 0: return PROTO[pid][4] == 1
    return pid >> 24 in (2, 3)

# ---- куски для уровней 1-3
SK = ('tree', 'weed', 'rock', 'eggs', 'bush', 'cac', 'drock')   # невидимые стены block.frm нужны: они держат проходимость
def comp_piece(mapname, tile, pad=1, rpu=False, walls_only=False):
    """Постройка из стен вокруг клетки tile (связная группа стен) и все декорации внутри ее рамки."""
    m = load(mapname, rpu)
    w = [o for o in m['objs'] if o['elev'] == 0 and o['pid'] >> 24 == 3]
    pts = {id(o): hexxy(o['tile']) for o in w}
    start = next(o for o in w if o['tile'] == tile)
    comp = [start]; seen = {id(start)}; k = 0
    while k < len(comp):
        a = pts[id(comp[k])]; k += 1
        for o in w:
            if id(o) not in seen and (pts[id(o)][0] - a[0]) ** 2 + (pts[id(o)][1] - a[1]) ** 2 <= 70 * 70:
                seen.add(id(o)); comp.append(o)
    xs = [o['tile'] % 200 for o in comp]; ys = [o['tile'] // 200 for o in comp]
    bb = (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)
    objs = [dict(o) for o in m['objs'] if o['elev'] == 0 and o['pid'] >> 24 in (0, 2, 3)
            and bb[0] <= o['tile'] % 200 <= bb[2] and bb[1] <= o['tile'] // 200 <= bb[3]
            and not any(s in (fidpath(o['fid']) or '').lower() for s in SK)]
    if walls_only: objs = [o for o in objs if o['pid'] >> 24 == 3]
    xs = [o['tile'] % 200 for o in objs]; ys = [o['tile'] // 200 for o in objs]
    return dict(objs=objs, floor={}, bb=(min(xs), min(ys), max(xs), max(ys)))
def spr_piece(items):
    """Набор отдельных объектов: (файл, du, dy[, вид]) относительно угла."""
    objs = []
    for it in items:
        name, du, dy = it[:3]; kind = it[3] if len(it) > 3 else 'scenery'
        objs.append(dict(tile=T(100 + du, 100 + dy), path=f'art\\{kind}\\{name}', pid=0, fid=0, flags=0))
    xs = [o['tile'] % 200 for o in objs]; ys = [o['tile'] // 200 for o in objs]
    return dict(objs=objs, floor={}, bb=(min(xs), min(ys), max(xs), max(ys)))
def tent_piece(beds=False):
    from tent import TENT
    a = 17505
    objs = [dict(tile=a + dy * 200 + dx, pid=p, fid=PROTO[p][0], flags=PROTO[p][1], rot=0, frame=0) for dx, dy, p in TENT]
    if beds:
        for t, p in ((a - 2 * 200 - 3, 0x20000d0), (a - 2 * 200 + 1, 0x20000d0)):
            objs.append(dict(tile=t, pid=p, fid=PROTO[p][0], flags=PROTO[p][1], rot=0, frame=0))
    xs = [o['tile'] % 200 for o in objs]; ys = [o['tile'] // 200 for o in objs]
    return dict(objs=objs, floor={}, bb=(min(xs), min(ys), max(xs), max(ys)))
def sub(piece, pred):
    objs = [o for o in piece['objs'] if pred((fidpath(o['fid']) or o.get('path') or '').split('\\')[-1].lower())]
    xs = [o['tile'] % 200 for o in objs]; ys = [o['tile'] // 200 for o in objs]
    return dict(objs=objs, floor={}, bb=(min(xs), min(ys), max(xs), max(ys)))
def with_extra(piece, items):
    """Кусок плюс отдельные объекты (du, dy от центра куска)."""
    bb = piece['bb']; cx, cy = (bb[0] + bb[2]) // 2, (bb[1] + bb[3]) // 2
    objs = list(piece['objs'])
    for it in items:
        name, du, dy = it[:3]; kind = it[3] if len(it) > 3 else 'scenery'
        objs.append(dict(tile=(cy + dy) * 200 + cx - du, path=f'art\\{kind}\\{name}', pid=0, fid=0, flags=0))
    xs = [o['tile'] % 200 for o in objs]; ys = [o['tile'] // 200 for o in objs]
    return dict(objs=objs, floor={}, bb=(min(xs), min(ys), max(xs), max(ys)))

def fit(piece, box, dx=0, dy=0):
    """Ставит кусок в середину участка box (u0, y0, u1, y1); сдвиг dx/dy в клетках u/y."""
    u0, y0, u1, y1 = box[:4]
    bx0, bx1 = 199 - u1, 199 - u0
    w = piece['bb'][2] - piece['bb'][0]; h = piece['bb'][3] - piece['bb'][1]
    tx = (bx0 + bx1) // 2 - w // 2 - dx; ty = (y0 + y1) // 2 - h // 2 + dy
    objs, _ = place(piece, tx, ty)
    return objs

B = D['build']
L4 = collections.defaultdict(list)
OTHER = collections.defaultdict(list)
for o in D['objs']:
    tg = o.get('tag')
    if tg and tg.startswith('b:'): L4[tg[2:]].append(o)
    else: OTHER[tg].append(o)
def at(name, u, y, kind='scenery'):
    return dict(tile=T(u, y), path=f'art\\{kind}\\{name}', pid=0, fid=0, flags=0)
def untagged(name):
    return [o for o in OTHER[None] if (o.get('path') or '').split('\\')[-1].lower() == name.lower()]

# куски из карт
mm = load('modmain'); om = ov_origin(mm)
# здания целиком (preprod.rebuild): рамка выреза только находит здание, стены берутся все, без чужих заборов
SHACK = rebuild(mm, main_part(cut(mm, (240, 150, 520, 360), om, SK), 90), skip=SK)              # дощатый сарай Модока
MHOUSE_BIG = rebuild(mm, main_part(cut(mm, (380, 260, 1180, 720), om, SK), 90), skip=SK)        # большой дощатый дом Модока
MHOUSE = comp_piece('modmain', 11518)                                   # дощатый дом Модока 11x10
MWARE = rebuild(mm, main_part(cut(mm, (210, 1000, 900, 1420), om, SK), 90), skip=SK)            # дощатый склад Модока
mi = load('modinn')
MBAR = rebuild(mi, main_part(cut(mi, (1110, 750, 1860, 1080), ov_origin(mi), SK), 90), skip=SK + ('corn',),
               clip=(90, 90, 116, 108))                                 # только зал бара Модока, без крыла с комнатами  # бар Модока со стенами
ARTENT = comp_piece('arvillag', 13306)                                  # шатер из шкур Арройо
ARTENT2 = comp_piece('arvillag', 22082)
RTENT = comp_piece('redment', 22086)                                    # палатка Реддинга
KPEN = comp_piece('klamall', 30276)                                     # загон из жердей (Кламат)
mv = load('vctyctyd'); VCCLINIC = rebuild(mv, main_part(cut(mv, (840, 230, 1500, 650), ov_origin(mv), SK), 90),
                                    excl=('adw', 'fen', 'block', 'ybk', 'ylf'), skip=SK + ('ypole', 'yrope'))   # без палатки рядом
def org_render(c, rad): X, Y = hexxy(c); return X - rad[0], Y - rad[1]
mn = load('navarro', rpu=True); NAVHOUSE = rebuild(mn, main_part(cut(mn, (150, 50, 480, 300), org_render(24696, (560, 300)), SK), 90), skip=SK)
m1 = load('ncr1'); NCRSMALL = rebuild(m1, main_part(cut(m1, (1350, 1330, 1680, 1560), ov_origin(m1), SK), 90), skip=SK)
TENT = tent_piece(); TENTBEDS = tent_piece(True)
LOW = dict(SHACK=('modmain', SHACK), MHOUSE_BIG=('modmain', MHOUSE_BIG), MWARE=('modmain', MWARE), MBAR=('modinn', MBAR),
           VCCLINIC=('vctyctyd', VCCLINIC), NAVHOUSE=('navarro', NAVHOUSE), NCRSMALL=('ncr1', NCRSMALL))   # для проверки (pathcheck)

def garden_lv(key, lv):
    g = L4[key]
    def nm(o): return (fidpath(o['fid']) or '').split('\\')[-1].lower()
    if lv == 1: return [o for o in g if nm(o) == 'cab1.frm']
    if lv == 2: return [o for o in g if nm(o) in ('cab1.frm', 'corn1.frm', 'corn3.frm')]
    if lv == 3: return [o for o in g if not nm(o).startswith('fen')]
    return g

# ---- здания: (имя в диалоге, ключи участков, функция уровня -> объекты)
BOX = lambda k: B[k]
BUILD = []
def bld(name, fn): BUILD.append((name, fn))

W1 = untagged('WELL001.frm'); TANK5 = untagged('gektank5.frm'); W2 = untagged('well1.frm')
bld('Старый колодец', lambda lv: W1 + ([at('pumpnec.frm', 49, 52)] if lv >= 2 and lv < 4 else []) + (TANK5 if lv >= 3 else [])   # насос рядом с колодцем, а не на нем (Егор)
    + (L4['1 Водокачка'] if lv == 4 else []))
bld('Новый колодец', lambda lv: W2 + ([at('watrtank.frm', 58, 46)] if lv == 2 else []) + (L4['Цистерна'] if lv >= 3 else [])
    + ([at('pipes1.frm', 51, 44), at('pipe003.frm', 50, 41)] if lv == 4 else []))
bld('Огороды', lambda lv: garden_lv('2 Огород', lv) + garden_lv('3 Огород', lv))
def houses(lv):
    out = []
    for i in range(8):
        bx = B[f'Дом {i + 1}']
        if lv == 1: out += fit(TENT, bx)
        elif lv == 2: out += fit(ARTENT, bx)
        elif lv == 3: out += fit(MHOUSE, bx)
        else: out += L4[f'Дом {i + 1}']
    return out
bld('Жилье (8 домов)', houses)
bld('Склад', lambda lv: fit(spr_piece([('CCART01.FRM', 0, 0, 'items'), ('CCART02.FRM', 0, 6, 'items')]), B['10 Склад']) if lv == 1
    else fit(SHACK, B['10 Склад']) if lv == 2 else fit(MWARE, B['10 Склад'], dx=5) if lv == 3 else L4['10 Склад'])
bld('Центр (староста)', lambda lv: fit(spr_piece([('firepit.frm', 0, 0), ('table1.frm', 3, -2), ('crate1.frm', 5, -2)]), B['12 Ратуша']) if lv == 1
    else fit(with_extra(ARTENT2, [('firepit.frm', 0, 7)]), B['12 Ратуша']) if lv == 2
    else fit(MHOUSE_BIG, B['12 Ратуша']) if lv == 3 else L4['12 Ратуша'])
CRAFTER = untagged('crafter1.frm')
bld('Мастерская', lambda lv: fit(spr_piece([('sttable.frm', 0, 0, 'items'), ('sttools.frm', 3, -2, 'items')]), B['9 Автомастерская']) if lv == 1
    else fit(with_extra(SHACK, [('sttable.frm', 0, 0, 'items')]), B['9 Автомастерская']) if lv == 2
    else fit(with_extra(MHOUSE, [('sttable.frm', -1, 0, 'items'), ('sttable.frm', 2, 1, 'items'), ('sttools.frm', 0, -3, 'items'),
                                 ('ltable1.frm', 7, 4), ('ltable2.frm', -6, 4)]), B['9 Автомастерская']) if lv == 3
    else L4['9 Автомастерская'] + CRAFTER)
GATEPOST = untagged('CONBAR01.frm') + untagged('vclight1.frm')
bld('Охрана', lambda lv: [at('CONBAR01.frm', 92, 164), at('BRAZR001.frm', 95, 164)] if lv == 1
    else GATEPOST + ([at('shack.frm', 89, 165)] if lv == 3 else [])   # будка охраны у ворот, как у военной базы (mbclose)
    + (L4['16 Казарма'] + OTHER['range'] if lv == 4 else []))
bld('Ферма браминов', lambda lv: fit(spr_piece([('HAYBED01.frm', 0, 0), ('barrel2.frm', 3, 2), ('HAYBED04.frm', 5, -1)]), B['4 Ранчо']) if lv == 1
    else fit(KPEN, B['4 Ранчо']) if lv == 2 else fit(P['stall'], B['4 Ранчо']) if lv == 3 else L4['4 Ранчо'])
STILLS = OTHER['still']
bld('Бар', lambda lv: fit(spr_piece([('barrel2.frm', 0, 0), ('table1.frm', 3, 1), ('barrel3.frm', 6, 0)]), B['11 Бар']) if lv == 1
    else fit(with_extra(RTENT, [('barrel2.frm', 7, 2), ('barrel3.frm', 8, 4), ('crate1.frm', -7, 3)]), B['11 Бар']) if lv == 2
    else fit(MBAR, B['11 Бар'], dy=-2) + STILLS if lv == 3 else L4['11 Бар'] + STILLS)
bld('Медпункт', lambda lv: fit(spr_piece([('medtbl01.frm', 0, 0), ('aybed2.frm', 4, 1)]), B['14 Госпиталь']) if lv == 1
    else fit(TENTBEDS, B['14 Госпиталь']) if lv == 2 else fit(VCCLINIC, B['14 Госпиталь']) if lv == 3
    else L4['14 Госпиталь'] + OTHER['autodoc'])
bld('Дом героя', lambda lv: fit(with_extra(ARTENT, [('footlkr1.frm', 0, 1, 'items')]), B['8 Дом героя']) if lv == 1
    else fit(with_extra(MHOUSE, [('footlkr1.frm', 0, 1, 'items')]), B['8 Дом героя']) if lv == 2 else fit(NCRSMALL, B['8 Дом героя']) if lv == 3 else L4['8 Дом героя'])
YARD = untagged('CCART01.FRM') + untagged('CCART02.FRM')
bld('Рынок', lambda lv: fit(spr_piece([('CCART01.FRM', 0, 0, 'items')]), B['18 Рынок']) if lv == 1
    else fit(spr_piece([('bigshlf1.frm', 0, 0), ('bigshlf2.frm', 4, 0), ('barrel.frm', 8, 2)]), B['18 Рынок']) if lv == 2
    else fit(sub(P['market'], lambda n: not n.startswith('bokcas') and n != 'aybed2.frm'), B['18 Рынок']) if lv == 3
    else L4['18 Рынок'] + YARD)

# ---- отдельные системы
def nm(o): return (o.get('path') or fidpath(o['fid']) or '').split('\\')[-1].lower()
TREES = [o for o in OTHER['deco'] + OTHER[None] if any(s in nm(o) for s in ('tree', 'bush'))]
TRASH = OTHER['trash']
LAMPS = [o for o in OTHER['deco'] if 'strlit' in nm(o)]
BARRELS = [dict(o, path='art\\scenery\\barrel.frm') for o in LAMPS]
F0, F1 = D['F']; M0, M1 = D['M']; GX0 = D['GX0']
GW = range(GX0 - 2, GX0 + 12)          # ворота (арка Города-Убежища) в линии забора: town_max.py
GATEF = OTHER['gateF']                  # арка с воротами в линии забора (север и юг), одна на все виды забора
WALL3 = OTHER['wall'] + GATEF
OUTER = OTHER['mesh'] + OTHER['gateM']
def mk(name, x, y, kind='walls'): return dict(tile=y * 200 + x, path=f'art\\{kind}\\{name}.frm', pid=0, fid=0, flags=0)
GAP = range(GX0, GX0 + 8)               # частокол и сетка: просто проем у ворот (Егор), арка только в стене Убежища
# Концы и углы — те же куски, что на картах F2 (статистика по всем картам): дерево — угол fen8000 (верх-лево) и fen1000
# (низ-право), концы рядов fen6000/fen9008 (ряд fen7), fen9001/fen9000 (ряд fen3); сетка — углы fence22/fence00,
# столбы fence12/fence13/fence23. Так заборы не висят в воздухе, а кончаются столбом.
PALISADE = {}
def pal(name, x, y): PALISADE[y * 200 + x] = mk(name, x, y)
for x in range(F0, F1 + 1):
    if x % 2 == 0: pal('fen7001', x, F0)
    else: pal('fen7000', x, F0 + 1)
    if x in GAP: continue
    if x % 2 == 0: pal('fen3001', x, F1 - 1)
    else: pal('fen3000', x, F1)
for y in range(F0 + 1, F1):                 # с F0 + 1: иначе в углу у (F0, F0 + 1) дыра (Егор нашел в игре)
    pal('fen2000' if y % 3 == 0 else 'fen2001', F1, y)
    pal('fen5000' if y % 3 == 0 else 'fen5001', F0, y)
for x in GAP:                               # северный проем
    PALISADE.pop((F0 if x % 2 == 0 else F0 + 1) * 200 + x, None)
def pal_end(x, ry, name): pal(name, x, ry(x))
r7 = lambda x: F0 if x % 2 == 0 else F0 + 1; r3 = lambda x: F1 - 1 if x % 2 == 0 else F1
pal('fen8000', F0, F0); pal('fen1000', F1, F1); pal('fen6000', F1, r7(F1)); pal('fen4000', F0, r3(F0))   # углы
pal_end(GAP[0] - 1, r7, 'fen6000'); pal_end(GAP[-1] + 1, r7, 'fen9008')      # столбы у проема на севере
pal_end(GAP[0] - 1, r3, 'fen9001'); pal_end(GAP[-1] + 1, r3, 'fen9000')      # и на юге
PALISADE = list(PALISADE.values())
MX = ['fence03', 'fence01', 'fence05', 'fence04']; MY = ['fence15', 'fence16', 'fence17', 'fence18']
MESH = {}
def ms(name, x, y): MESH[y * 200 + x] = mk(name, x, y)
for x in range(F0, F1 + 1):
    if x not in GAP: ms(MX[x % 4], x, F0); ms(MX[x % 4], x, F1)
for y in range(F0 + 1, F1):
    ms(MY[y % 4], F0, y); ms(MY[y % 4], F1, y)
ms('fence23', F0, F0); ms('fence23', F1, F0); ms('fence22', F0, F1); ms('fence00', F1, F1)   # углы
for y in (F0, F1): ms('fence12', GAP[0] - 1, y); ms('fence13', GAP[-1] + 1, y)             # столбы у проема
MESH = list(MESH.values())
TUR = D['TUR']

# ---- проверка: все PID есть, считаем объекты
def normall(objs): return [norm(o) for o in objs if keep(o)]
LEVELS = [[normall(fn(lv)) for lv in (1, 2, 3, 4)] for name, fn in BUILD]
SYS = dict(trees=normall(TREES), trash=normall(TRASH), lamps=normall(LAMPS), barrels=normall(BARRELS),
           palisade=normall(PALISADE), mesh=normall(MESH), wall=normall(WALL3), outer=normall(OUTER))
# ---- фонари, мусор, деревья и кусты не должны стоять на зданиях (любого уровня), друг на друге и на дорогах:
# мешающий объект переносим на ближайшую свободную клетку (Егор: кусты на мусоре — мусор оставить, кусты перенести)
from hexlib import tdir
def ring1(t): return {t} | {tdir(t, r, 1) for r in range(6)}
BUSY = set()
for L in LEVELS:
    for objs in L:
        for e in objs: BUSY |= ring1(e['tile'])
for k in ('palisade', 'mesh', 'wall', 'outer'):
    for e in SYS[k]: BUSY |= ring1(e['tile'])
for x, y in TUR: BUSY |= ring1(y * 200 + x)
BUSY |= ring1(T(*D['CAR']))
ROAD = set(D['PATH'])
def free(t):
    x, y = t % 200, t // 200
    return F0 + 3 <= x <= F1 - 3 and F0 + 3 <= y <= F1 - 3 and t not in BUSY and (x // 2, y // 2) not in ROAD
def settle(objs, also=()):
    moved = 0
    for e in objs:
        if not free(e['tile']) or e['tile'] in also:
            seen = {e['tile']}; q = [e['tile']]
            while q:
                t = q.pop(0)
                if free(t) and t not in also: break
                for r in range(6):
                    n = tdir(t, r, 1)
                    if n not in seen: seen.add(n); q.append(n)
            e['tile'] = t; moved += 1
        BUSY.update(ring1(e['tile']))
    return moved
for e in SYS['lamps']: e['light'] = (5, 100)     # у фонарей strlit в прототипе и на картах F2 света нет: даем свет, как у пилонов vclight1 (радиус 5 вместо 3)
MOVED = dict(lamps=settle(SYS['lamps']), trash=settle(SYS['trash']), trees=settle(SYS['trees']))
for a, b in zip(SYS['barrels'], SYS['lamps']): a['tile'] = b['tile']      # бочки-костры стоят там же, где фонари
rep = []
for (name, _), lv in zip(BUILD, LEVELS): rep.append(f'{name}: ' + ', '.join(str(len(x)) for x in lv))
for k, v in SYS.items(): rep.append(f'{k}: {len(v)}')
rep.append(f'турели: {len(TUR)}'); rep.append(f'перенесено: {MOVED}')
print('\n'.join(rep))

# ---- картинки: весь город на уровне N (для проверки глазами)
base = mapparse.parse(os.path.join(ROOT, 'base/rpu-2.4.34/maps/desert1.map'))
rr = random.Random(7)
TILES = [v if (v & 0xffff) not in (0, 1, 659, 179, 180) else (v & 0xffff0000) | rr.choice(range(191, 199)) for v in base['tiles'][0]]
rp = random.Random(9)
for sq in D['PATH']:
    if sq not in D['floor']: TILES[sq[1] * 100 + sq[0]] = (TILES[sq[1] * 100 + sq[0]] & 0xffff0000) | (2261 if rp.random() < 0.2 else 2274)
for (sx, sy), f in D['floor'].items(): TILES[sy * 100 + sx] = (TILES[sy * 100 + sx] & 0xffff0000) | (f & 0xffff)
TILES = [(1 << 16) | (v & 0xffff) for v in TILES]                      # без крыш: крыша 4 уровня висела бы над палатками
def draw(objs, out, marks=()):
    mm = dict(base); mm['tiles'] = {0: TILES}
    mm['objs'] = [dict(tile=e['tile'], pid=e['pid'], fid=e['fid'] or PROTO[e['pid']][0], elev=0, rot=e['rot']) for e in objs]
    render.parse = lambda f: mm
    pts = [hexxy(T(a, b)) for a in (M0, M1) for b in (M0, M1)]
    cx = (min(p[0] for p in pts) + max(p[0] for p in pts)) // 2; cy = (min(p[1] for p in pts) + max(p[1] for p in pts)) // 2
    c = nearest(cx, cy); rx = (max(p[0] for p in pts) - min(p[0] for p in pts)) // 2 + 120; ry = (max(p[1] for p in pts) - min(p[1] for p in pts)) // 2 + 260
    render.render('x', out, c, rad_px=(rx, ry), marks=marks)
    im = Image.open(out); return im, c, rx, ry
if os.environ.get('IMG'):
    lvls = [int(x) for x in os.environ['IMG'].split(',')]
    for lv in lvls:
        objs = [e for L in LEVELS for e in L[lv - 1]] + SYS['trees'] + SYS['trash']
        objs += (SYS['barrels'] if lv < 3 else SYS['lamps'])
        objs += {1: SYS['palisade'], 2: SYS['mesh'], 3: SYS['wall'], 4: SYS['wall'] + SYS['outer']}[lv]
        im, *_ = draw(objs, OUT + f'town_lv{lv}_full.png')
        sm = im.copy(); sm.thumbnail((2600, 2600)); sm.save(OUT + f'town_lv{lv}.jpg', quality=88)
        print('img', lv, im.size)
pickle.dump(LOW, open(OUT + 'low_pieces.pkl', 'wb'))
pickle.dump(dict(LEVELS=LEVELS, SYS=SYS, TUR=TUR, NAMES=[n for n, _ in BUILD], TILES=TILES, CAR=D['CAR'], F=D['F'], M=D['M'], GX0=GX0,
                 PROTO=PROTO), open(OUT + 'town_build.pkl', 'wb'))
open(OUT + 'town_build_report.txt', 'w', encoding='utf-8').write('\n'.join(rep))
