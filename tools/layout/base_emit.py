#!/usr/bin/env python3
"""Военная база на месте логова (квест 1.5, Егор 2026-10-15). Карта f2mlair = копия горной карты mountn5.
Уровень 1 — расчистка: палатки, ящики, бочки, мусор банды под снос (сундук Кейна и лаз в погреб остаются,
ценности из ящиков и с тел — в сундук), армейская палатка командира и казарма. Уровень 2 — мастерская и гараж,
уровень 3 — арсенал. Постройки — куски из карт игры (mbclose — военная база у Наварро, сарай Модока из песочницы).
Пишет scripts_src/f2mbasel.h. С IMG=папка рисует базу на каждом уровне с отметками.
Проверки: новые постройки не налезают на скалы и друг на друга, сундук, лаз, въезд, места командира, Хэнка и
гарнизона проходимы и достижимы от входа героя на каждом уровне."""
import os, sys, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapparse
from hexlib import tdir
from render import fidpath, render
from preprod import load, building, place
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
SRC = os.path.join(ROOT, 'base/rpu-2.4.34/maps/mountn5.map')
OUTH = os.path.join(ROOT, 'scripts_src/f2mbasel.h')
HIDDEN, NOBLOCK, MULTIHEX = 0x1, 0x10, 0x800
def T(x, y): return y * 200 + x
def xy(t): return t % 200, t // 200
def ring(t, n):
    s = {t}
    for _ in range(n): s |= {tdir(u, r, 1) for u in s for r in range(6)}
    return s
def _cube(t):
    x, y = xy(t); q = x; r = y - (x + (x & 1)) // 2; return q, r, -q - r
def _td(a, b):
    """Расстояние в клетках (проверено против ring на случайных клетках)."""
    a, b = _cube(a), _cube(b); return max(abs(a[i] - b[i]) for i in range(3))
def name(o): return (fidpath(o['fid']) or '').split('\\')[-1].lower()
PF = {}
def pflags(pid):
    if pid not in PF: PF[pid] = struct.unpack_from('>I', mapparse.proto(pid), 20)[0]
    return PF[pid]
def pfid(pid): return struct.unpack_from('>I', mapparse.proto(pid), 8)[0]
def oflags(o): return o.get('flags', pflags(o['pid']))
def blk_of(objs):
    out = set()
    for o in objs:
        if o['pid'] >> 24 not in (1, 2, 3): continue
        if o['pid'] >> 24 == 2 and mapparse.subtype(o['pid']) == 0: continue   # двери проходимы
        f = oflags(o)
        if f & (HIDDEN | NOBLOCK): continue
        out |= ring(o['tile'], 1) if f & MULTIHEX else {o['tile']}
    return out
def flood(start, blk):
    seen = {start}; q = [start]
    while q:
        t = q.pop()
        for r in range(6):
            n = tdir(t, r, 1); x, y = xy(n)
            if n not in seen and n not in blk and 55 <= x <= 135 and 70 <= y <= 125: seen.add(n); q.append(n)
    return seen

# ---- точки логова (f2mlairl.h) и наши объекты на карте
LAIRL = open(os.path.join(ROOT, 'scripts_src/f2mlairl.h'), encoding='utf-8').read()
def lp(n): import re; return int(re.search(rf'#define LAIR_{n}\s+\((\d+)\)', LAIRL).group(1))
HERO, CHEST, CELLAR, WATER, STORE = lp('HERO'), lp('CHEST'), lp('CELLAR'), lp('WATER'), lp('STORE')
CELL_OUT = T(114, 93)    # f2mlair.h LAIR_CELL_OUT
m = mapparse.parse(SRC)
ORIG = [o for o in m['objs'] if o['elev'] == 0 and o['tile'] >= 0 and o['pid'] >> 24 in (0, 2, 3)]

# ---- уровень 1: что сносим. Лагерь банды — прямоугольник x 66..120, y 82..100; скалы, деревья, кусты, камни, трава остаются
JUNK = ('aybed', 'barrel', 'bed', 'bowl', 'boxes', 'bucket', 'cab', 'ccart', 'corn', 'crate', 'junk', 'njunk', 'maryj',
        'pot', 'rug', 'tirs', 'trash', 'woodfire', 'ypole', 'yrope', 'char')
TENTW = ('yar', 'ybk', 'ylf', 'yrt')
def in_camp(t): x, y = xy(t); return 66 <= x <= 120 and 82 <= y <= 100
clear = [o for o in ORIG if in_camp(o['tile']) and (name(o).startswith(JUNK) or name(o).startswith(TENTW))]
ct = {o['tile'] for o in clear}
near = set(); [near.update(ring(t, 1)) for t in ct]
keepw = {o['tile'] for o in ORIG if name(o).startswith(('mount', 'black')) or o['pid'] >> 24 == 5}
for o in ORIG:
    if name(o) == 'block.frm' and in_camp(o['tile']) and o['tile'] in near and not (ring(o['tile'], 1) & keepw):
        clear.append(o)
cid = {id(o) for o in clear}
KEEP = [o for o in ORIG if id(o) not in cid]
print('сносим', len(clear), 'остается', len(KEEP))

# ---- куски построек из карт игры
SK = ('tree', 'weed', 'rock', 'eggs', 'bush', 'cac', 'drock', 'roks')
mb = load('mbclose')
def mbt(x, y): return T(x, y)
TENT = [building(mb, [mbt(121, 96)], excl=('block',), skip=SK + ('njunk', 'arwls'), pad=3),
        building(mb, [mbt(139, 96)], excl=('block',), skip=SK + ('njunk', 'arwls'), pad=3)]
HUT = building(mb, [mbt(72, 84)], excl=('block', 'fence', 'mbw', 'vb4'), skip=SK + ('mbpip', 'njunk'), pad=1)
def around(m_, tiles, r, names_):
    out = []
    for o in m_['objs']:
        if o['elev'] != 0 or o['tile'] < 0 or o['pid'] >> 24 in (1, 5): continue
        if any(o['tile'] in ring(t, r) for t in tiles) and (name(o).startswith(names_)):
            out.append(dict(o))
    xs = [o['tile'] % 200 for o in out]; ys = [o['tile'] // 200 for o in out]
    return dict(objs=out, floor={}, bb=(min(xs), min(ys), max(xs), max(ys)))
TRUCK = around(mb, [mbt(86, 86)], 3, ('truck', 'block'))
BOOTH = around(mb, [mbt(102, 102)], 2, ('shack', 'block'))
for k, p in (('палатка', TENT[0]), ('сарай', HUT), ('грузовик', TRUCK), ('будка', BOOTH)):
    print(k, len(p['objs']), p['bb'], sorted({name(o) for o in p['objs']}))

# ---- картинка: пол mountn5 и данный список объектов
def draw(objs, out, marks=(), center=T(92, 92), rad=(760, 380)):
    import render as R
    from PIL import Image, ImageDraw
    cx, cy = R.hexxy(center); x0, y0 = cx - rad[0], cy - rad[1]
    im = Image.new('RGB', (2 * rad[0], 2 * rad[1]), (0, 0, 0))
    tl = R.dat('art\\tiles\\tiles.lst').decode('cp1251').split('\n')
    for s in range(10000):
        f = m['tiles'][0][s] & 0xffff
        if f in (0, 1): continue
        x, y = R.sqxy(s); x -= x0; y -= y0
        if -100 < x < im.width + 20 and -50 < y < im.height + 20:
            r = R.frm('art\\tiles\\' + tl[f].strip())
            if r: im.paste(r[0], (x, y), r[0])
    def key(o): x, y = R.hexxy(o['tile']); return ((oflags(o) & 0x8) == 0, y, -x)
    for o in sorted(objs, key=key):
        if o['pid'] >> 24 == 5: continue
        p = R.fidpath(o['fid'])
        if not p or p.lower().endswith('block.frm'): continue
        r = R.frm(p, o.get('rot', 0))
        if not r: continue
        a, ox, oy = r
        x, y = R.hexxy(o['tile']); x += 16 + ox - x0; y += 8 + oy - y0
        im.paste(a, (x - a.width // 2, y - a.height + 1), a)
    dr = ImageDraw.Draw(im)
    for t, lbl, col in marks:
        x, y = R.hexxy(t); x += 16 - x0; y += 8 - y0
        dr.ellipse((x - 4, y - 3, x + 4, y + 3), outline=col); dr.text((x + 5, y - 6), lbl, fill=col)
    im.convert('RGB').save(out, quality=88)
IMG = os.environ.get('IMG')
if IMG and os.environ.get('STEP') == 'clear':
    marks = [(T(x, y), f'{x},{y}', (255, 255, 0)) for x in range(65, 125, 5) for y in range(80, 105, 5)]
    draw(KEEP, IMG + '/clear.jpg', marks)

# ---- расстановка: кусок ставим ближе всего к желаемой клетке, не налезая на скалы, сундук, лаз и другие постройки
BLK_KEEP = blk_of(KEEP)
RESERVED = ring(CHEST, 1) | ring(CELLAR, 2) | ring(CELL_OUT, 1) | {WATER}
def norm_piece(objs):
    out = []
    for o in objs:
        n = dict(o); n['flags'] = o.get('flags', pflags(o['pid'])); out.append(n)
    return out
def try_place(piece, want, taken, extra_free=()):
    bb = piece['bb']; w = bb[2] - bb[0]; h = bb[3] - bb[1]
    wx, wy = xy(want); best = None
    for ty in range(wy - h // 2 - 12, wy - h // 2 + 13):
        for tx in range(wx - w // 2 - 12, wx - w // 2 + 13):
            objs, _ = place(piece, tx, ty)
            objs = norm_piece(objs)
            tiles = {o['tile'] for o in objs}
            b = blk_of(objs)
            if not all(in_camp(t) or xy(t)[1] > 82 for t in tiles): continue
            if (b | tiles) & (BLK_KEEP | taken | RESERVED - set(extra_free)): continue
            if ring_any(b, BLK_KEEP): continue
            cx = sum(xy(t)[0] for t in tiles) / len(tiles); cy = sum(xy(t)[1] for t in tiles) / len(tiles)
            d = (cx - wx) ** 2 + (cy - wy) ** 2
            if best is None or d < best[0]: best = (d, objs)
    if not best: print('нет места', xy(want)); return []
    return best[1]
def ring_any(b, other):
    # между постройкой и скалой хотя бы клетка прохода
    for t in b:
        for r in range(6):
            if tdir(t, r, 1) in other: return True
    return False
def occ(objs):
    s = set()
    for o in objs: s |= ring(o['tile'], 1)
    return s
taken = set()
L1 = []
CMD_TENT = try_place(TENT[0], T(90, 89), taken); taken |= occ(CMD_TENT); L1 += CMD_TENT
BAR_TENT = try_place(TENT[1], T(75, 88), taken); taken |= occ(BAR_TENT); L1 += BAR_TENT
L2 = []
WORK = try_place(HUT, T(104, 89), taken); taken |= occ(WORK); L2 += WORK
GAR = try_place(TRUCK, T(82, 96), taken); taken |= occ(GAR); L2 += GAR
L3 = []
ARS = try_place(BOOTH, T(106, 96), taken); taken |= occ(ARS); L3 += ARS
for k, v in (('командир', CMD_TENT), ('казарма', BAR_TENT), ('мастерская', WORK), ('гараж', GAR), ('арсенал', ARS)):
    if not v: print(k, 'НЕ ВСТАЛ'); continue
    xs = [xy(o['tile'])[0] for o in v]; ys = [xy(o['tile'])[1] for o in v]
    print(k, (min(xs), min(ys), max(xs), max(ys)))
if IMG and os.environ.get('STEP') == 'place':
    marks = [(CHEST, 'сундук', (255, 255, 0)), (CELLAR, 'лаз', (255, 255, 0)), (CELL_OUT, 'выход', (0, 255, 255))]
    draw(KEEP + L1 + L2 + L3, IMG + '/place.jpg', marks)

# ---- проходимость: от входа героя до сундука, лаза, выхода из погреба, на каждом уровне
FLAG_MASK = 0x8 | 0x10 | 0x0000C000 | 0x000F0000 | 0x10000000 | 0x20000000 | 0x80000000
LEVELS = {1: L1, 2: L1 + L2, 3: L1 + L2 + L3}
ROCKS = [dict(pid=33555705, tile=CELLAR, flags=pflags(33555705))]   # завал над лазом (после взрыва), худший случай
REACH = {}
for lv, objs in LEVELS.items():
    blk = BLK_KEEP | blk_of(objs) | blk_of(ROCKS)
    rr = flood(HERO, blk)
    REACH[lv] = rr
    assert ring(CHEST, 1) & rr, ('сундук недостижим', lv)
    assert CELL_OUT in rr, ('выход из погреба недостижим', lv)
    assert (ring(CELLAR, 2) - ring(CELLAR, 1)) & rr, ('к лазу не подойти', lv)
    assert CHEST not in blk_of(objs), ('сундук под стеной', lv)
print('проходимость: сундук, лаз, выход из погреба достижимы на уровнях 1-3')
R3 = REACH[3]
# снаружи построек: дошли, не открывая дверей (внутри сарая гарнизон не виден)
DOORS3 = {o['tile'] for o in L1 + L2 + L3 if o['pid'] >> 24 == 2 and mapparse.subtype(o['pid']) == 0}
OUT3 = flood(HERO, BLK_KEEP | blk_of(L1 + L2 + L3) | blk_of(ROCKS) | DOORS3)
OCC3 = set(); [OCC3.update(ring(o['tile'], 1)) for o in L1 + L2 + L3]
OCC3W = set(); [OCC3W.update(ring(o['tile'], 2)) for o in L1 + L2 + L3 if o['pid'] >> 24 in (2, 3)]
# командир: внутри своей палатки (открытой стороной к зрителю), ближе к середине и к переду
xs = [xy(o['tile'])[0] for o in CMD_TENT]; ys = [xy(o['tile'])[1] for o in CMD_TENT]
tb = (min(xs), min(ys), max(xs), max(ys)); tc = T((tb[0] + tb[2]) // 2, (tb[1] + tb[3]) // 2)
inside = [t for t in R3 if tb[0] + 2 <= xy(t)[0] <= tb[2] - 2 and tb[1] + 2 <= xy(t)[1] <= tb[3] - 2 and t != CHEST and t not in ring(CHEST, 1)]
assert inside, 'в палатке командира нет места'
CMD = min(inside, key=lambda t: (_td(t, tc), -xy(t)[1]))
# Хэнк на базе: перед палаткой командира, снаружи
front = [t for t in R3 if t not in OCC3 and xy(t)[1] >= tb[3] + 1 and t not in RESERVED]
HANK = min(front, key=lambda t: (_td(t, T((tb[0] + tb[2]) // 2, tb[3] + 2)), xy(t)))
# гарнизон: 12 мест по лагерю, друг от друга не ближе 3 клеток, не вплотную к постройкам
cand = sorted([t for t in OUT3 if in_camp(t) and t not in OCC3W and t not in RESERVED and t not in ring(CMD, 1) and t not in ring(HANK, 1)
               and 84 <= xy(t)[1] <= 99 and 68 <= xy(t)[0] <= 112], key=lambda t: (xy(t)[1], xy(t)[0]))
# по лагерю равномерно: каждое следующее место — самое далекое от уже выбранных (первое — у входа в лагерь)
SPAWN = [min(cand, key=lambda t: _td(t, T(88, 98)))]
while len(SPAWN) < 12:
    SPAWN.append(max(cand, key=lambda t: (min(_td(t, s) for s in SPAWN + [CMD, HANK]), -t)))
assert len(SPAWN) == 12, len(SPAWN)
print('командир', xy(CMD), 'Хэнк', xy(HANK), 'гарнизон', [xy(t) for t in SPAWN])
if IMG:
    for lv in (1, 2, 3):
        mk = [(CHEST, 'сундук', (255, 255, 0)), (CELLAR, 'лаз', (255, 255, 0)), (CMD, 'командир', (0, 255, 0)), (HANK, 'Хэнк', (0, 255, 255))]
        mk += [(t, f'g{i}', (255, 128, 0)) for i, t in enumerate(SPAWN)]
        draw(KEEP + LEVELS[lv], IMG + f'/base_lv{lv}.jpg', mk if os.environ.get('MARKS') else [])

# ---- заголовок для скриптов
def emit_obj(o, ind='   '):
    pid = o['pid']; rf = (o.get('rot', 0) % 6) + 8 * (o.get('frame', 0) if 0 <= o.get('frame', 0) <= 100 else 0)
    out = [f'{ind}call lay_o({pid}, {o["tile"]}, {rf});']
    if 'fid' in o and (o['fid'] & 0xffffff) != (pfid(pid) & 0xffffff): FIDDIFF.append((name(o), xy(o['tile'])))
    d = (oflags(o) ^ pflags(pid)) & FLAG_MASK
    fs, fc = d & oflags(o), d & pflags(pid)
    if fs or fc: out.append(f'{ind}call lay_flg({fs}, {fc});')
    return out
FIDDIFF = []
h = ['// Сгенерировано tools/layout/base_emit.py: военная база на месте логова (карта f2mlair, копия mountn5). Не править руками.',
     '// Уровень 1: расчистка лагеря банды (сундук Кейна и лаз в погреб остаются) и две армейские палатки (командир, казарма),',
     '// 2: мастерская (дощатый сарай) и гараж (грузовик), 3: арсенал (будка). Постройки из карты mbclose (военная база у Наварро).',
     '// Проходимость проверена поиском пути: сундук, лаз, выход из погреба, командир, Хэнк и гарнизон достижимы от входа на всех уровнях.',
     '// Подключать после f2mtlay.h (lay_o, lay_flg).',
     '#ifndef F2MBASEL_H', '#define F2MBASEL_H', '',
     f'#define BASE_CMD      ({CMD})   // {xy(CMD)}: командир в своей палатке',
     f'#define BASE_HANK     ({HANK})   // {xy(HANK)}: Хэнк на базе, пока идет стройка',
     f'#define BASE_SPAWNS   ({len(SPAWN)})', '',
     'procedure base_spawn(variable i);', 'procedure base_clear_x(variable pid, variable tile);', 'procedure base_clear_list;',
     'procedure base_lv1;', 'procedure base_lv2;', 'procedure base_lv3;', '']
h.append('// Места гарнизона (по лагерю, у построек)')
h.append('procedure base_spawn(variable i) begin')
for i, t in enumerate(SPAWN): h.append(f'   {"if" if i == 0 else "else if"} (i == {i}) then return {t};   // {xy(t)}')
h.append(f'   return {SPAWN[0]};'); h.append('end'); h.append('')
h.append(f'// Расчистка (уровень 1): {len(clear)} объектов лагеря банды. base_clear_x убирает объект (вещи из ящиков — в сундук, f2mlair.ssl)')
h.append('procedure base_clear_list begin')
for o in sorted(clear, key=lambda o: o['tile']): h.append(f'   call base_clear_x({o["pid"]}, {o["tile"]});   // {name(o)}')
h.append('end'); h.append('')
for lv, objs, txt in ((1, L1, 'армейские палатки командира и казармы'), (2, L2, 'мастерская (сарай) и гараж (грузовик)'), (3, L3, 'арсенал (будка)')):
    h.append(f'// Уровень {lv}: {txt}, объектов {len(objs)}')
    h.append(f'procedure base_lv{lv} begin')
    for o in objs: h += emit_obj(o)
    h.append('end'); h.append('')
h.append('#endif')
open(OUTH, 'w', encoding='utf-8').write('\n'.join(h) + '\n')
print('записан', OUTH, 'объектов', len(L1), len(L2), len(L3), 'картинка отличается от прототипа:', FIDDIFF[:10])
