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
KINDS = {0: 'items', 1: 'critters', 2: 'scenery', 3: 'walls'}
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
        if t == 1: fl = 0                                       # у существ блок задает движок; флаги прототипа тут не нужны
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
    if o.get('crit'):                                           # существо (брамин): только pid, клетка, поворот
        return dict(pid=o['pid'], tile=o['tile'], rot=o.get('rot', 0) % 6, frame=0, fid=None, fset=0, fclr=0, light=None)
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
    if o.get('lit'): e['light'] = o['lit']                      # горящие бочки бара: свет задаем сами
    return e

def keep(o):
    """Подбираемые вещи из чужих карт не берем: только контейнеры (сундуки, ящики, повозки), декорации и стены."""
    if o.get('crit'): return True
    pid = o['pid'] if not o.get('path') else pid_of(o['path'])
    if pid >> 24 == 0: return PROTO[pid][4] == 1
    return pid >> 24 in (2, 3)

# ---- куски для уровней 1-3
SK = ('tree', 'weed', 'rock', 'eggs', 'bush', 'cac', 'drock')   # невидимые стены block.frm нужны: они держат проходимость
def comp_piece(mapname, tile, pad=1, rpu=False):
    """Постройка из стен вокруг клетки tile (связная группа стен без невидимых блоков, блоки вплотную к ней) и все
    декорации внутри ее рамки (preprod.building). Через блоки группа не растет: иначе цепляла соседние заборы."""
    from preprod import building
    return building(load(mapname, rpu), [tile], excl=('block',), skip=SK, pad=pad)
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
SHACK = rebuild(mm, main_part(cut(mm, (240, 150, 520, 360), om, SK), 90), skip=SK + ('toilet',))   # дощатый сарай Модока, без унитаза (Егор)
MHOUSE_BIG = rebuild(mm, main_part(cut(mm, (380, 260, 1180, 720), om, SK), 90), skip=SK)        # большой дощатый дом Модока
MHOUSE = comp_piece('modmain', 11518)                                   # дощатый дом Модока 11x10
MWARE = rebuild(mm, main_part(cut(mm, (210, 1000, 900, 1420), om, SK), 90), skip=SK)            # дощатый склад Модока
mi = load('modinn')
MBAR = rebuild(mi, main_part(cut(mi, (1110, 750, 1860, 1080), ov_origin(mi), SK), 90), skip=SK + tuple(f'corn{i}.frm' for i in range(1, 10)),   # кукуруза; угол стены corn001 оставляем (без него дыра в стене, Егор)
              
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
TENT = tent_piece()
JUNK = ('trash', 'njunk', 'junk', 'blood', 'dedbrom', 'bone', 'radslimb', 'still', 'tum1000', 'bib', 'hole')
def house_piece(mapname, seed, drop=()):
    """Дом целиком (preprod.building) без чужих заборов, мусора и трупов."""
    from preprod import building
    return building(load(mapname), [seed], excl=('adw', 'fen', 'block', 'rl0', 'rl1', 'tfenc'), skip=SK + JUNK + tuple(drop), pad=1)
def tent_at(mapname, seed, drop=()):
    """Палатка целиком: брезент или шкуры, колья и веревки (рамка шире на 3 клетки), без мусора."""
    from preprod import building
    return building(load(mapname), [seed], excl=('block',), skip=SK + JUNK + tuple(drop), pad=3)
TENTBEDS = tent_at('desert7', 16100, ('ccart',))                                  # палатка пустыни целиком, с тремя кроватями, без мусора
MILTENT = [tent_at('mbclose', t) for t in (19321, 19339, 24139)]       # армейские палатки у военной базы (mbclose): брезент, койки
HIDETENT = [tent_at('arvillag', t, ('sklpole',)) for t in (13306, 18112, 18896, 20532, 22082, 24920)] + \
           [tent_at('coast12', t, ('sklpole',)) for t in (18484, 22896)]             # палатки из шкур Арройо и побережья, у всех своя начинка
HOUSE3 = [MHOUSE, house_piece('sfchina', 10642), house_piece('geckjunk', 27122), house_piece('broken2', 23124),
          house_piece('klagraz', 23522), house_piece('klatrap', 19528), house_piece('broken2', 18644), house_piece('broken2', 23108)]
CLINIC2 = house_piece('redment', 24740)                                # маленький дощатый дом (Реддинг, 11x11, койки), 2 стола добавляем (Егор)
WARE2 = house_piece('klamall', 12666)                                  # дощатый склад Кламата 13x17 (бочки, покрышки)
HERO3 = house_piece('reddown', 24724)                                  # дощатый дом Реддинга: кровать, печь, полки, сундук

# ---- расстановка вещей внутри постройки: свободная клетка, проход не перекрывается (как pathcheck.py)
from hexlib import tdir
def ring1(t): return {t} | {tdir(t, r, 1) for r in range(6)}
def opid(o): return o['pid'] if not o.get('path') else pid_of(o['path'])
def blockmap(objs):
    blk, door = set(), set()
    for o in objs:
        if o.get('crit'): blk.add(o['tile']); continue
        pid = opid(o)
        if pid >> 24 not in (2, 3): continue
        f = PROTO[pid][1] | o.get('flags', 0) if o.get('path') else o['flags']
        if f & 0x11: continue                                   # HIDDEN, NO_BLOCK
        cells = [o['tile']] + ([tdir(o['tile'], r, 1) for r in range(6)] if f & 0x800 else [])
        (door if pid >> 24 == 2 and PROTO[pid][4] == 0 else blk).update(cells)
    return blk, door
def reach(objs, bb):
    """Клетки рамки bb, куда можно дойти снаружи (двери открываются)."""
    blk, door = blockmap(objs); x0, y0, x1, y1 = bb
    edge = [y * 200 + x for x in range(x0, x1 + 1) for y in (y0, y1)] + [y * 200 + x for y in range(y0, y1 + 1) for x in (x0, x1)]
    seen = {t for t in edge if t not in blk}; q = list(seen)
    while q:
        t = q.pop()
        for r in range(6):
            n = tdir(t, r, 1)
            if n not in seen and n not in blk and x0 <= n % 200 <= x1 and y0 <= n // 200 <= y1: seen.add(n); q.append(n)
    return seen, blk, door
def wallbb(objs):
    w = [o['tile'] for o in objs if not o.get('crit') and opid(o) >> 24 == 3] or [o['tile'] for o in objs]
    xs = [t % 200 for t in w]; ys = [t // 200 for t in w]
    return min(xs), min(ys), max(xs), max(ys)
def inside_cells(objs):
    """Клетки внутри стен: в ряду и в столбце клетки есть стены с обеих сторон (рамка стен захватывает и клетки
    перед зигзагом фасада — туда ставить нельзя: вещь окажется на улице)."""
    W = {o['tile'] for o in objs if not o.get('crit') and opid(o) >> 24 == 3}
    x0, y0, x1, y1 = wallbb(objs); out = set()
    rows = collections.defaultdict(list); cols = collections.defaultdict(list)
    for t in W: rows[t // 200].append(t % 200); cols[t % 200].append(t // 200)
    for x in range(x0 + 2, x1):                                  # у переднего фасада (малые x, большие y) не ставим:
        for y in range(y0 + 1, y1 - 1):                          # высокая вещь вылезает из-за стены на улицу
            r, c = rows.get(y, ()), cols.get(x, ())
            if any(v < x for v in r) and any(v > x for v in r) and any(v < y for v in c) and any(v > y for v in c): out.add(y * 200 + x)
    return out
BIGN = ('bed', 'aybed', 'sstove', 'fridge', 'desk', 'tbl', 'table')
BACK = {n: 'ur' for n in ('bokcas1', 'bokcas5', 'bkshlf5', 'locker5', 'dresr1', 'dresr3')}; BACK['abkshlf1'] = 'ul'   # к какой стене прижата спина
def back_nb(t, side):
    """Соседняя клетка в сторону верха-вправо ('ur') или верха-влево ('ul') на экране."""
    x0, y0 = hexxy(t); best = None
    for r in range(6):
        n = tdir(t, r, 1); x, y = hexxy(n); dx, dy = x - x0, y - y0
        sc = {'ur': dx - dy, 'ul': -dx - dy, 'dl': -dx + dy, 'dr': dx + dy}[side]
        if best is None or sc > best[0]: best = (sc, n)
    return best[1]
def furnish(objs, items, seed, mode='wall', region=None):
    """Ставит items (файл, вид) или ('crit', pid) на свободные клетки внутри постройки (или в region): у стены (mode='wall')
    или на открытом месте ('open'), не у дверей, не вплотную к другим вещам; каждый раз проверяем, что проход не перекрыт."""
    rnd = random.Random(seed); objs = list(objs)
    if region is None: region = inside_cells(objs)
    if not region: print('  пустое здание:', len(objs)); return objs
    xs = [t % 200 for t in region]; ys = [t // 200 for t in region]
    bb = (min(xs) - 4, min(ys) - 4, max(xs) + 4, max(ys) + 4)
    R0, blk, door = reach(objs, bb)
    busy = set()
    for o in objs:
        if mode == 'free' and (o.get('path') or fidpath(o['fid']) or '').lower().split('\\')[-1].startswith('haybed'): continue   # сено не мешает
        busy.add(o['tile'])
        if o.get('crit') or opid(o) >> 24 == 2: busy |= ring1(o['tile'])
    for d in door: busy |= {n for m in ring1(d) for n in ring1(m)}
    blk0 = set(blk); WALLS = {o['tile'] for o in objs if not o.get('crit') and opid(o) >> 24 == 3}
    for it in items:
        c = [t for t in region if t in R0 and t not in blk and t not in busy]
        nm0 = it[0][:-4].lower()
        if nm0.startswith(BIGN):                       # высокие и широкие вещи не вплотную к стенам: текстура торчала за стену (Егор)
            c2 = [t for t in c if not any(n in WALLS for m in ring1(t) for n in ring1(m))]
            if c2 or not nm0.startswith(('bed', 'aybed')): c = c2
            else: print('  кровать без отступа от стен:', it)
        def shown(t):                                     # перед полкой (к зрителю) в 2 клетках нет стены: иначе ее закрывает часть здания
            for sd in ('dl', 'dr'):
                n1 = back_nb(t, sd); n2 = back_nb(n1, sd)
                if n1 in WALLS or n2 in WALLS: return False
            return True
        base = list(c); wall = mode in ('wall', 'wall+')
        if it[0][:-4] in BACK and wall:
            c = [t for t in base if back_nb(t, BACK[it[0][:-4]]) in WALLS]     # шкаф и полка только спиной вплотную к стене (Егор)
            c = [t for t in c if shown(t)] or c                               # лучше там, где не закрыты зданием, но стена важнее
        elif it[0][:-4] in BACK: c = [t for t in base if shown(t)]
        nb = lambda t: any(n in blk0 for n in ring1(t) - {t})
        c = sorted(t for t in c if mode == 'free' or nb(t) == wall); rnd.shuffle(c)
        if not c and mode == 'wall+' and it[0][:-4] not in BACK:                                          # у стены нет места: чуть дальше, но проход вокруг (ring1 свободен)
            c = sorted(t for t in base if not nb(t)); rnd.shuffle(c)
        for t in c:
            o = dict(tile=t, pid=it[1], rot=rnd.randrange(6), crit=True, fid=0, flags=0) if it[0] == 'crit' else \
                dict(tile=t, path=f'art\\{it[1] if len(it) > 1 else "scenery"}\\{it[0]}', pid=0, fid=0, flags=0)
            R1, blk1, _ = reach(objs + [o], bb)
            if (R0 - {t}) <= R1:
                objs.append(o); R0, blk = R1, blk1
                small = (it[0].startswith(('char', 'chair', 'bokcas', 'bkshlf', 'locker', 'dresr', 'abkshlf', 'chest', 'footlkr', 'ss1')))
                busy |= {t} if small else ring1(t); break
        else: print('  не влезло:', it)
    return objs
PID_BRAHMIN = 16777226
def brahmins(objs, n, seed, region=None): return furnish(objs, [('crit', PID_BRAHMIN)] * n, seed, 'open', region)
def area(box, w, h):
    """Клетки w x h в середине участка box."""
    u0, y0, u1, y1 = box[:4]; cu, cy = (u0 + u1) // 2, (y0 + y1) // 2
    return {T(u, y) for u in range(cu - w // 2, cu + w // 2) for y in range(cy - h // 2, cy + h // 2)}

def outdoor_bar():
    """Уличный бар (Егор): стойка буквой Г из Кафе разбитых грез (rndcafe, стены bar011-020), за ней бочки и полка,
    сзади закрыта ящиками; перед стойкой столы-катушки со стульями, горящие бочки по углам, два костра для готовки."""
    m = load('rndcafe')
    objs = [dict(o) for o in m['objs'] if o['elev'] == 0 and o['pid'] >> 24 == 3 and 118 <= o['tile'] % 200 <= 127 and 122 <= o['tile'] // 200 <= 127]
    def s(name, x, y, kind='scenery', **kw): objs.append(dict(tile=y * 200 + x, path=f'art\\{kind}\\{name}', pid=0, fid=0, flags=0, **kw))
    s('brl1000.frm', 121, 126); s('barrel2.frm', 125, 126); s('bigshlf1.frm', 123, 127)
    for x in (119, 121, 123, 125): s(('crate1.frm', 'boxes2.frm')[x % 4 == 1], x, 128 + x % 2)      # задняя сторона: ящики
    s('crate1.frm', 128, 125); s('boxes3.frm', 128, 127)                                          # левый край стойки, проход за стойку у (127, 128)
    for x in (121, 124): s('char02.frm', x, 120)                                                  # стулья у стойки
    for tx, ty in ((111, 116), (119, 115), (127, 116), (115, 119)):                               # столы-катушки со стульями
        s('tbl2000.frm', tx, ty); s('char01.frm', tx + 1, ty); s('char03.frm', tx - 1, ty + 1)
    for x, y in ((108, 115), (133, 115), (108, 127), (134, 126)): s('barrel.frm', x, y, lit=(4, 100))   # горящие бочки
    s('firepit.frm', 111, 123); s('bucket1.frm', 109, 121)                                        # костры для готовки
    s('woodfire.frm', 132, 120, lit=(3, 80)); s('brl1000.frm', 134, 122)
    xs = [o['tile'] % 200 for o in objs]; ys = [o['tile'] // 200 for o in objs]
    return dict(objs=objs, floor={}, bb=(min(xs), min(ys), max(xs), max(ys)))
OUTBAR = outdoor_bar()
LOW = dict(SHACK=('modmain', SHACK), MHOUSE_BIG=('modmain', MHOUSE_BIG), MWARE=('modmain', MWARE), MBAR=('modinn', MBAR),
           VCCLINIC=('vctyctyd', VCCLINIC), NAVHOUSE=('navarro', NAVHOUSE), NCRSMALL=('ncr1', NCRSMALL))   # для проверки (pathcheck)

def garden_lv(key, lv):
    g = L4[key]
    def nm(o): return (fidpath(o['fid']) or '').split('\\')[-1].lower()
    if lv == 1: return [o for o in g if nm(o) == 'cab1.frm']
    if lv == 2: return [o for o in g if nm(o) in ('cab1.frm', 'corn1.frm', 'corn3.frm')]
    plants = [o for o in g if not nm(o).startswith(('fen', 'gate'))]            # ворота и забор НКР рвались на куски (Егор): свой забор
    if lv == 3: return plants
    gate = [o for o in g if nm(o).startswith('gate')]                           # ворота НКР оставляем (Егор), забор вокруг свой и цельный
    ts = [o['tile'] for o in plants]; xs = [t % 200 for t in ts]; ys = [t // 200 for t in ts]
    X0 = (min(xs) - 3) & ~1; X1 = ((max(xs) + 3) | 1)
    if gate:
        gx, gy = gate[0]['tile'] % 200, gate[0]['tile'] // 200
        Y0 = gy if gx % 2 == 0 else gy - 1                                     # северный ряд забора проходит через ворота
    else: gx = (X0 + X1) // 2; Y0 = (min(ys) - 3) & ~1
    Y1 = ((max(ys) + 3) | 1)
    gx = max(X0 + 2, min(X1 - 3, gx))
    return plants + gate + wood_rect(X0, X1, Y0, Y1, gapN=range(gx - 1, gx + 2))

# ---- здания: (имя в диалоге, ключи участков, функция уровня -> объекты)
BOX = lambda k: B[k]
BUILD = []
def bld(name, fn): BUILD.append((name, fn))

W1 = untagged('WELL001.frm'); TANK5 = untagged('gektank5.frm'); W2 = untagged('well1.frm')
bld('Старый колодец', lambda lv: W1 + ([at('pumpnec.frm', 49, 52)] if lv >= 2 and lv < 4 else []) + (TANK5 if lv == 3 else [])   # на 4 уровне бак стоял в стене водокачки (Егор)   # насос рядом с колодцем, а не на нем (Егор)
    + (L4['1 Водокачка'] if lv == 4 else []))
bld('Новый колодец', lambda lv: W2 + ([at('watrtank.frm', 58, 46)] if lv == 2 else []) + (L4['Цистерна'] if lv >= 3 else [])
    + ([at('pipes1.frm', 51, 44), at('pipe003.frm', 50, 41)] if lv == 4 else []))
bld('Огороды', lambda lv: garden_lv('2 Огород', lv) + garden_lv('3 Огород', lv))
# 4 уровень: тот же дом НКР, начинка у каждого своя (Егор). 0 и 6 — фермеры (грабли, плуг), остальные без них
FARM = ('rake', 'plow', 'vase1', 'aybed2')
# мебель 4 ур. (Егор: «поиграй в симс», жителям нужно где спать, есть и хранить вещи): у каждого дома по 3-4 кровати, 2-3 полки или
# шкафа у стен, стол со стульями посередине и своя «изюминка» (печь, холодильник, письменный стол, сундук, сушилка)
BEDS = ['bed3.frm', 'bed4.frm', 'bed8.frm', 'aybed1.frm', 'aybed2.frm']        # прямые, невысокие (без спинок, торчащих за стену)
STORE = [('bokcas1.frm', 'items'), ('bokcas5.frm', 'items'), ('bkshlf5.frm', 'items'), ('locker5.frm', 'items'), ('dresr1.frm', 'items'),
         ('dresr3.frm', 'items'), ('abkshlf1.frm', 'items'), ('chest1.frm', 'items')]        # полки, шкафы, комоды, сундук
CHAIRS = ['char01.frm', 'char02.frm', 'char03.frm', 'chair3.frm']
TABLES = ['tbl1000.frm', 'tbl2000.frm', 'table3.frm']
EXTRA = [[('sstove2.frm',), ('fridge.frm', 'items')], [('desk1.frm', 'items'), ('chair3.frm',)], [('sstove2.frm',), ('footlkr1.frm', 'items')],
         [('fridge.frm', 'items'), ('ss118.frm',)], [('desk1.frm', 'items'), ('ss105.frm',)], [('sstove2.frm',), ('ss118.frm',)],
         [('footlkr1.frm', 'items'), ('ss105.frm',)], [('fridge.frm', 'items'), ('sstove2.frm',)]]   # печь, холодильник, письменный стол, сундук-ноги кровати
def free_share(objs):
    """Доля внутренних клеток, куда еще можно поставить вещь: дойти можно, клетка не занята и не вплотную к вещи."""
    ins = inside_cells(objs); bb = tuple(v + d for v, d in zip(wallbb(objs), (-4, -4, 4, 4)))
    R, blk, door = reach(objs, bb); busy = set()
    for o in objs:
        if opid(o) >> 24 == 2 or o.get('crit'): busy |= ring1(o['tile'])
    return len([c for c in ins if c in R and c not in blk and c not in busy]) / max(1, len(ins))
def house4(i):
    """Обязательно только кровати и стулья (Егор 2026-10-06); остальное (стол, шкафы, печь и т. д.) — пока есть свободное место:
    ставим вещи по одной, пока свободно больше трети внутренних клеток; набор и порядок у каждого дома свои."""
    objs = L4[f'Дом {i + 1}']
    drop = ('aybed2',) if i in (0, 6) else FARM               # кровать у двери (в НКР стояла на пороге) убираем у всех
    objs = [o for o in objs if not (fidpath(o['fid']) or '').split('\\')[-1].lower().startswith(drop)]
    r = random.Random(900 + i)
    objs = furnish(objs, [(b,) for b in r.sample(BEDS, 3)], seed=40 + i, mode='open')            # кровати у стен: 3 места для сна
    objs = furnish(objs, [(c,) for c in r.sample(CHAIRS, 2)], seed=60 + i, mode='open')           # и стулья
    opt = [([(r.choice(TABLES),)], 'open'), ([x if isinstance(x, tuple) else (x,) for x in [r.choice(STORE)]], 'wall'),
           (EXTRA[i][:1], 'wall'), ([x if isinstance(x, tuple) else (x,) for x in [r.choice(STORE)]], 'wall'), (EXTRA[i][1:], 'open')]
    r.shuffle(opt)
    for k, (items, mode) in enumerate(opt[:(1, 3, 2, 4, 2, 3, 1, 4)[i]]):          # у каждого дома своё число добавок (1-4)
        if free_share(objs) <= 0.3: break
        objs = furnish(objs, items, seed=80 + i * 7 + k, mode=mode)
    return objs
def houses(lv):
    """1 ур. — армейские палатки (можно одинаковые, Егор), 2 — палатки из шкур, у каждой своя начинка,
    3 — 8 разных дощатых и кирпичных домов, 4 — дом НКР с разной начинкой."""
    out = []
    for i in range(8):
        bx = B[f'Дом {i + 1}']
        if lv == 1: out += fit(MILTENT[i % 3], bx)
        elif lv == 2: out += fit(HIDETENT[i], bx)
        elif lv == 3: out += fit(HOUSE3[i], bx)
        else: out += house4(i)
    return out
bld('Жилье (8 домов)', houses)
bld('Склад', lambda lv: fit(spr_piece([('CCART01.FRM', 0, 0, 'items'), ('CCART02.FRM', 0, 6, 'items')]), B['10 Склад']) if lv == 1
    else fit(WARE2, B['10 Склад']) if lv == 2 else fit(MWARE, B['10 Склад'], dx=5) if lv == 3 else L4['10 Склад'])
bld('Центр (староста)', lambda lv: fit(spr_piece([('firepit.frm', 0, 0), ('table1.frm', 3, -2), ('crate1.frm', 5, -2)]), B['12 Ратуша']) if lv == 1
    else fit(with_extra(ARTENT2, [('firepit.frm', 0, 7)]), B['12 Ратуша']) if lv == 2
    else fit(MHOUSE_BIG, B['12 Ратуша']) if lv == 3 else L4['12 Ратуша'])
CRAFTER = untagged('crafter1.frm')
# в мастерской были вещи-предметы sttable/sttools (доска с инструментами висит на стене, без стены — в воздухе, Егор):
# теперь только декорации — верстаки ltable, покрышки, бочки, ящики
bld('Мастерская', lambda lv: fit(spr_piece([('ltable2.frm', 0, 0), ('TIRE001.frm', 4, -2), ('TIRE002.frm', 6, 1), ('crate1.frm', -4, 2),
                                            ('brl1000.frm', -5, -1)]), B['9 Автомастерская']) if lv == 1
    else furnish(fit(SHACK, B['9 Автомастерская']), [('ltable2.frm',), ('TIRE001.frm',)], seed=21) if lv == 2
    else furnish(fit(with_extra(MHOUSE, [('ltable1.frm', 7, 4), ('ltable2.frm', -6, 4)]), B['9 Автомастерская']),
                 [('ltable2.frm',), ('ltable1.frm',), ('TIRE001.frm',), ('brl1000.frm',)], seed=22) if lv == 3
    else [o for o in L4['9 Автомастерская'] if (fidpath(o['fid']) or '').split('\\')[-1].lower() not in ('trapdr.frm', 'hole1.frm')] + CRAFTER)   # люк в малом здании лишний (Егор)
GATEPOST = untagged('CONBAR01.frm') + untagged('vclight1.frm')
bld('Охрана', lambda lv: [at('CONBAR01.frm', 92, 164), at('BRAZR001.frm', 95, 164)] if lv == 1
    else GATEPOST + ([at('shack.frm', 89, 165)] if lv == 3 else [])   # будка охраны у ворот, как у военной базы (mbclose)
    + (L4['16 Казарма'] + OTHER['range'] if lv == 4 else []))
def ranch_pen():
    """Загон из жердей (те же куски, что у частокола) с проемом внизу, сено и бочка с водой внутри."""
    u0, y0, u1, y1 = B['4 Ранчо'][:4]
    cx, cy = 199 - (u0 + u1) // 2, (y0 + y1) // 2
    X0 = (cx - 7) & ~1; Y0 = (cy - 6) & ~1; X1 = X0 + 15; Y1 = Y0 + 13
    gx = X0 + 6
    return wood_rect(X0, X1, Y0, Y1, gapS=range(gx, gx + 3)) + [
        at('HAYBED01.frm', 199 - (X0 + 4), Y0 + 4), at('HAYBED04.frm', 199 - (X0 + 9), Y0 + 5), at('barrel2.frm', 199 - (X1 - 2), Y0 + 3)]
def pen_inside():
    u0, y0, u1, y1 = B['4 Ранчо'][:4]; cx, cy = 199 - (u0 + u1) // 2, (y0 + y1) // 2
    X0 = (cx - 7) & ~1; Y0 = (cy - 6) & ~1
    return {y * 200 + x for x in range(X0 + 1, X0 + 15) for y in range(Y0 + 1, Y0 + 13)}
# брамины на каждом уровне (Егор): 2, 3, 4, 6
def stall_brahmins(objs, n, seed):
    """Брамины стоят в стойлах: на сене (haybed) между жердями; клетки сена вдоль дальней стены и в двух нижних рядах."""
    hay = {o['tile'] for o in objs if (fidpath(o['fid']) or str(o.get('path'))).lower().split('\\')[-1].startswith('haybed')}
    return furnish(objs, [('crit', PID_BRAHMIN)] * n, seed, 'free', hay)
bld('Ферма браминов', lambda lv: brahmins(fit(spr_piece([('HAYBED01.frm', 0, 0), ('barrel2.frm', 3, 2), ('HAYBED04.frm', 5, -1)]), B['4 Ранчо']), 2, 81,
                                          area(B['4 Ранчо'], 14, 12)) if lv == 1
    else brahmins(ranch_pen(), 3, 82, pen_inside()) if lv == 2
    else stall_brahmins(fit(P['stall'], B['4 Ранчо']), 4, 83) if lv == 3
    else brahmins(L4['4 Ранчо'], 6, 84, area(B['4 Ранчо'], 26, 40)))
STILLS = OTHER['still']
BAR2 = house_piece('gecksetl', 19470)                                     # дощатый бар Геккo: Г-образная стойка, столы, стулья, бочки (Егор: нормальный бар на 2 ур.)
bld('Бар', lambda lv: fit(OUTBAR, B['11 Бар']) if lv == 1
    else fit(BAR2, B['11 Бар']) if lv == 2
    else fit(MBAR, B['11 Бар'], dy=-2) + STILLS if lv == 3 else L4['11 Бар'] + STILLS)
# 1 ур. — армейская палатка с хирургическим столом, 2 — палатка пустыни с кроватями и двумя столами (Егор);
# автодок на 3 и 4 уровне не стоит: его ставит квест (Егор), место под него на 4 уровне свободно (town_max.py)
def hospital4(autodoc=bool(os.environ.get('AUTODOC'))):
    """Госпиталь 4 ур. (дом Реддинга): полку, наполовину скрытую перегородкой, переставляем на видное место; место автодока —
    на месте хирургического стола medtbl03 (автодок появится по квесту: стол заменяется). autodoc=True — только для картинки."""
    def nm(o): return (fidpath(o['fid']) or '').split('\\')[-1].lower()
    objs = [o for o in L4['14 Госпиталь'] if nm(o) != 'bkshlf3.frm']
    if autodoc:
        tbl = [o for o in objs if nm(o) == 'medtbl03.frm']
        objs = [o for o in objs if nm(o) != 'medtbl03.frm'] + [dict(o, path='art\\scenery\\holo.frm', pid=0, fid=0) for o in tbl]
    return furnish(objs, [('bkshlf3.frm', 'items')], seed=131, mode='wall')
bld('Медпункт', lambda lv: furnish(fit(MILTENT[2], B['14 Госпиталь']), [('medtbl01.frm',)], seed=101) if lv == 1
    else furnish(fit(CLINIC2, B['14 Госпиталь']), [('medtbl01.frm',), ('medtbl01.frm',)], seed=102) if lv == 2
    else fit(sub(VCCLINIC, lambda n: n != 'holo.frm'), B['14 Госпиталь']) if lv == 3
    else hospital4())
HD = [0, 0]                             # сдвиг палатки 1 ур., чтобы люк подвала был внутри нее (ниже)
def hero4():
    """Дом героя 4 ур. (Убежище): убираем таблички «Центр распределения слуг» и полку, наполовину скрытую стеной; добавляем
    вместительные (250 ед.) шкафы вдоль стен: полки, шкафчик, сундуки (Егор: 3-4 на этаж, остальное хранить ниже, в подвале)."""
    def nm(o): return (fidpath(o['fid']) or '').split('\\')[-1].lower()
    objs = [o for o in L4['8 Дом героя'] if nm(o) not in ('sign36.frm', 'sign37.frm', 'bkshlf5.frm', 'footlkr4.frm')]
    reg = inside_cells(objs) | {t for t in inner_cells(objs, loose=True) if t // 200 < wallbb(objs)[3] - 2}   # шире обычного, но не у фасада
    return furnish(objs, [('bkshlf5.frm', 'items'), ('locker5.frm', 'items'), ('abkshlf1.frm', 'items'), ('bkshlf5.frm', 'items'),
                          ('locker5.frm', 'items'), ('chest1.frm', 'items'), ('chest1.frm', 'items')], seed=121, mode='wall+', region=reg)
bld('Дом героя', lambda lv: fit(with_extra(ARTENT, [('footlkr1.frm', 0, 1, 'items')]), B['8 Дом героя'], *HD) if lv == 1
    else fit(with_extra(MHOUSE, [('footlkr1.frm', 0, 1, 'items')]), B['8 Дом героя']) if lv == 2
    else furnish(fit(HERO3, B['8 Дом героя']), [('footlkr1.frm', 'items'), ('locker5.frm', 'items')], seed=111) if lv == 3   # был туалет НКР (Егор)
    else hero4())
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
def wood_rect(X0, X1, Y0, Y1, gapN=(), gapS=()):
    """Деревянный забор прямоугольником (X0, Y0 четные, X1, Y1 нечетные, как у частокола), с проемами в верхнем (gapN)
    и нижнем (gapS) ряду; у проемов и в углах столбы."""
    out = {}
    def put(name, x, y): out[y * 200 + x] = mk(name, x, y)
    r7 = lambda x: Y0 if x % 2 == 0 else Y0 + 1; r3 = lambda x: Y1 - 1 if x % 2 == 0 else Y1
    for x in range(X0, X1 + 1):
        if x not in gapN: put('fen7001' if x % 2 == 0 else 'fen7000', x, r7(x))
        if x not in gapS: put('fen3001' if x % 2 == 0 else 'fen3000', x, r3(x))
    for y in range(Y0 + 1, Y1):                 # с Y0 + 1: иначе в углу у (X0, Y0 + 1) дыра (Егор нашел в игре)
        put('fen2000' if y % 3 == 0 else 'fen2001', X1, y)
        put('fen5000' if y % 3 == 0 else 'fen5001', X0, y)
    put('fen8000', X0, Y0); put('fen1000', X1, Y1); put('fen6000', X1, r7(X1)); put('fen4000', X0, r3(X0))   # углы
    for g, r, a, b in ((gapN, r7, 'fen6000', 'fen9008'), (gapS, r3, 'fen9001', 'fen9000')):
        if g: put(a, g[0] - 1, r(g[0] - 1)); put(b, g[-1] + 1, r(g[-1] + 1))                               # столбы у проема
    return list(out.values())
PALISADE = wood_rect(F0, F1, F0, F1, GAP, GAP)

MX = ['fence03', 'fence01', 'fence05', 'fence04']; MY = ['fence15', 'fence16', 'fence17', 'fence18']
MESH = {}
def ms(name, x, y): MESH[y * 200 + x] = mk(name, x, y)
for x in range(F0, F1 + 1):
    if x not in GAP: ms(MX[x % 4], x, F0); ms(MX[x % 4], x, F1)
for y in range(F0 + 1, F1):
    ms(MY[y % 4], F0, y); ms(MY[y % 4], F1, y)
ms('fence03', F0, F0); ms('fence12', F1, F0); ms('fence22', F0, F1); ms('fence00', F1, F1)   # углы (верхние подобраны по картинке: замкнуты, один столб)
for y in (F0, F1): ms('fence12', GAP[0] - 1, y); ms('fence13', GAP[-1] + 1, y)             # столбы у проема
MESH = list(MESH.values())
TUR = D['TUR']

# ---- люк в подвал дома героя (Егор): одна клетка на всех 4 уровнях, чтобы люк не переезжал при перестройке.
# Ищем клетку внутри дома на каждом уровне: свободна, проходима, не у стены и не у двери; из таких — ближе к середине участка.
# Люк — trapdr.frm (дверь-люк, без блока): лестница-переход (ladrdwn) без места назначения перекинула бы героя в угол карты
def inner_cells(objs, loose=False):
    x0, y0, x1, y1 = wallbb(objs); bb = (x0 - 4, y0 - 4, x1 + 4, y1 + 4)
    R, blk, door = reach(objs, bb)
    busy = set()
    for o in objs: busy |= {o['tile']} if loose else ring1(o['tile'])
    for d in door: busy |= {n for m in ring1(d) for n in ring1(m)}
    return {y * 200 + x for x in range(x0 + 1, x1) for y in range(y0 + 1, y1)} & R - busy
HERO_FN = dict(BUILD)['Дом героя']
_hc = [inner_cells(HERO_FN(lv)) for lv in (2, 3, 4)]       # дома 2-4 уровня; палатку 1 уровня потом двигаем к люку
_u0, _y0, _u1, _y1 = B['8 Дом героя'][:4]
_ctr = T((_u0 + _u1) // 2, (_y0 + _y1) // 2)
def _d(t): return abs(t % 200 - _ctr % 200) + abs(t // 200 - _ctr // 200)
def _find():
    offs = sorted(((a, b) for a in range(-8, 9, 2) for b in range(-8, 9, 2)), key=lambda p: abs(p[0]) + abs(p[1]))
    for t in sorted(set.intersection(*_hc), key=_d):
        for o in offs:
            HD[:] = list(o)
            if t in inner_cells(HERO_FN(1), loose=True): return t
    raise SystemExit('люк не попал в палатку 1 уровня')
HATCH_T = _find()
print('люк', HATCH_T, 'сдвиг палатки 1 ур.', HD)
HATCH = [dict(tile=HATCH_T, path='art\\scenery\\hole1.frm', pid=0, fid=0, flags=0)]

# ---- проверка: все PID есть, считаем объекты
def normall(objs): return [norm(o) for o in objs if keep(o)]
LEVELS = [[normall(fn(lv)) for lv in (1, 2, 3, 4)] for name, fn in BUILD]
SYS = dict(trees=normall(TREES), trash=normall(TRASH), lamps=normall(LAMPS), barrels=normall(BARRELS),
           palisade=normall(PALISADE), mesh=normall(MESH), wall=normall(WALL3), outer=normall(OUTER), hatch=normall(HATCH))
# ---- фонари, мусор, деревья и кусты не должны стоять на зданиях (любого уровня), друг на друге и на дорогах:
# мешающий объект переносим на ближайшую свободную клетку (Егор: кусты на мусоре — мусор оставить, кусты перенести)
from hexlib import tdir
def ring1(t): return {t} | {tdir(t, r, 1) for r in range(6)}
BUSY = set()
for L in LEVELS:
    for objs in L:
        for e in objs: BUSY |= ring1(e['tile'])
for k in ('palisade', 'mesh', 'wall', 'outer', 'hatch'):
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
