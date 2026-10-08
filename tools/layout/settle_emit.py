# Лагерь у скал на карте города (Егор, 2026-10-08: лагерь переезжает с временной карты desert1 на карту песочницы).
# Берет 1-й уровень зданий из расстановки песочницы (scripts_src/test/f2mtblay.h, ее пишет town_emit.py) и пишет:
#   scripts_src/f2mtlay.h — расстановка лагеря для релиза: основание (костер со столом старосты, 3 армейские палатки,
#                           палатка героя с сундуком, заколоченный старый колодец, деревья) и постройки прораба по местам
#                           (0 новый колодец, 1-2 огороды, 3-6 палатки), как было в f2mlay.h;
#   mod/data/maps/f2mset.map — пол города (mod/test/maps/f2mtown.map) и кольцо выходов на карту мира у края карты.
# Использование: settle_emit.py
import os, re, struct, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
SRC = open(os.path.join(ROOT, 'scripts_src/test/f2mtblay.h'), encoding='utf-8').read().split('\n')

# ---- уровни 1-4 каждого здания песочницы: [(pid, tile, rf, [доп. строки tb_flg/tb_lit])]
names, LV, sys_ = {}, {}, {}
cur = None; level = None; sysk = None
for line in SRC:
    m = re.match(r'// (.+): объектов по уровням', line)
    if m: pending = m.group(1)
    m = re.match(r'procedure tb_b(\d+)\(variable lv\) begin', line)
    if m: cur = int(m.group(1)); names[cur] = pending; LV[cur] = {1: [], 2: [], 3: [], 4: []}; level = None; continue
    m = re.match(r'\s+(?:end else )?if \(lv == (\d)\) then begin', line)
    if m and cur is not None: level = int(m.group(1)); continue
    m = re.match(r'\s+(?:end else )?if \(s == (\d+)\) then begin', line)
    if m: sysk = int(m.group(1)); sys_[sysk] = []; cur = None; continue
    if line.startswith('end') or line.startswith('procedure tb_bld') or line.startswith('procedure tb_turrets'):
        cur = None; sysk = None
    m = re.match(r'\s+call tb_o\((\d+), (\d+), (\d+)\);', line)
    tgt = LV[cur][level] if cur is not None and level else sys_[sysk] if sysk is not None else None
    if m and tgt is not None: tgt.append([int(m.group(1)), int(m.group(2)), int(m.group(3)), []]); continue
    m = re.match(r'\s+call (tb_flg|tb_lit)\((.+)\);', line)
    if m and tgt is not None and tgt: tgt[-1][3].append((m.group(1), m.group(2)))
byname = {v: k for k, v in names.items()}
def B(prefix, lv=1): return LV[[k for n, k in byname.items() if n.startswith(prefix)][0]][lv]

def xy(t): return t % 200, t // 200
def clusters(objs, n):
    """Делим объекты на n построек: связные группы (соседи ближе 4 клеток)."""
    groups = []
    for o in objs:
        x, y = xy(o[1]); hit = [g for g in groups if any(abs(x - a) <= 4 and abs(y - b) <= 4 for a, b in g['pts'])]
        if hit:
            g = hit[0]
            for h in hit[1:]: g['pts'] += h['pts']; g['objs'] += h['objs']; groups.remove(h)
        else:
            g = dict(pts=[], objs=[]); groups.append(g)
        g['pts'].append((x, y)); g['objs'].append(o)
    assert len(groups) == n, (len(groups), n, [len(g['objs']) for g in groups])
    return [g['objs'] for g in groups]
def center(objs):
    xs = [xy(o[1])[0] for o in objs]; ys = [xy(o[1])[1] for o in objs]
    return sum(xs) / len(xs), sum(ys) / len(ys)

old_well = B('Старый колодец'); new_well = B('Новый колодец')
assert len(old_well) == 1 and len(new_well) == 1
gardens = clusters(B('Огороды'), 2)
centre = B('Центр'); hero = B('Дом героя')
fire = [o for o in centre if o[0] == 33555632][0][1]          # firepit
cx, cy = xy(fire)
# Участки жилья стоят вплотную, поэтому делим не по связности, а по участкам town_max.py:
# HOUSES = 5 участков в ряду y=35 и 3 в ряду y=51, через 13 клеток по u (u = 199 - x), с u=102
def house_of(o):
    x, y = xy(o[1]); u = 199 - x
    col = max(0, min(4, (u - 102) // 13)); return col if y < 50 else 5 + min(2, col)
houses = [[o for o in B('Жилье') if house_of(o) == i] for i in range(8)]
assert all(houses) and sum(map(len, houses)) == len(B('Жилье')), [len(h) for h in houses]
horder = sorted(range(8), key=lambda i: (center(houses[i])[0] - cx) ** 2 + (center(houses[i])[1] - cy) ** 2)
houses = [houses[i] for i in horder]
houses4 = [[o for o in B('Жилье', 4) if house_of(o) == i] for i in horder]   # те же участки на 4-м уровне
trees = sys_[0]
gardens.sort(key=lambda g: center(g)[1])

PID_WELL_OLD, PID_WELL_FIXED, PID_WELL_NEW = 33555425, 33556410, 33554815
table = [o for o in centre if o[0] == 33554732][0][1]
def T(x, y): return y * 200 + x
tx, ty = xy(table)
LAY = dict(
    FIRE=fire, TABLE=table, TED=T(tx, ty + 2), FOREMAN=T(cx - 6, cy + 4), CHIEF=T(98, 158),
    OLDWELL=old_well[0][1], NEWWELL=new_well[0][1], HEROTENT=hero[0][1])

# ---- развалины (Егор, 2026-10-08): на участках будущих зданий стоят стены их 4-го уровня с проломами, чтобы пол 4-го уровня
# не висел пустым. Под строящимся зданием развалины сносятся (lay_ruin_clear), бар на 1-2 уровне стоит внутри своих развалин
# (их сносят только к 3-му уровню). Проломы: выкидываем стены кусками 3x3 клетки (55%), блоки block.frm оставляем только
# рядом с уцелевшей стеной, в проломах мусор без блока (junk11-18). Ничего не ставим на основание, на стройки прораба,
# на бар 1-2 и рядом с местами людей; проходимость проверяем поиском пути (как pathcheck.py).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapparse, render
from hexlib import tdir
HIDDEN, NOBLOCK, MULTIHEX = 0x1, 0x10, 0x800
PI = {}
def pinfo(pid):
    if pid not in PI:
        b = mapparse.proto(pid); fid, fl = struct.unpack_from('>i', b, 8)[0], struct.unpack_from('>I', b, 20)[0]
        try: name = render.fidpath(fid).split('\\')[-1].lower()
        except Exception: name = '?'
        PI[pid] = (fid, fl, name)
    return PI[pid]
def ring(t, n):
    s = {t}
    for _ in range(n): s |= {tdir(u, r, 1) for u in s for r in range(6)}
    return s
def blocked(objs):
    out = set()
    for o in objs:
        if o[0] >> 24 not in (1, 2, 3): continue
        f = pinfo(o[0])[1]
        for fn, a in o[3]:
            if fn == 'tb_flg': fs, fc = map(int, a.split(',')); f = (f | fs) & ~fc
        if f & (HIDDEN | NOBLOCK): continue
        out |= ring(o[1], 1) if f & MULTIHEX else {o[1]}
    return out
def hsh(*a):
    h = 2166136261
    for v in a: h = ((h ^ (v & 0xffffffff)) * 16777619) & 0xffffffff
    return h
JUNK = list(range(33556258, 33556266))          # junk11-18 (RPU), без блока
PLOTS = [(f'Жилье {k + 1}', houses4[k]) for k in range(3, 8)] + \
        [(n, B(n, 4)) for n in ('Склад', 'Мастерская', 'Охрана', 'Ферма браминов', 'Бар', 'Медпункт')]
found = trees + centre + hero + sum(houses[:3], []) + old_well
slots = new_well + sum(gardens, []) + sum(houses[3:7], [])
bar12 = B('Бар', 1) + B('Бар', 2)
PTS = dict(TED=(LAY['TED'], 3), FOREMAN=(LAY['FOREMAN'], 3), CHIEF=(LAY['CHIEF'], 4), WAGONS=(T(87, 150), 9), CAR=(32283, 4),
           FIRE=(LAY['FIRE'], 7))
keepout = set()
for t, r in PTS.values(): keepout |= ring(t, r)
RUINS = []
for pi, (name, objs) in enumerate(PLOTS):
    own = houses[pi + 3] if pi < 4 else []        # своя палатка прораба: перед ней развалины сносятся
    near = set()
    for ob in found + [q for q in slots if q not in own] + (bar12 if name != 'Бар' else []): near |= ring(ob[1], 1)
    if name == 'Бар': near |= {ob[1] for ob in bar12}   # бар 1-2 внутри развалин: только не на тех же клетках
    near |= keepout
    walls = [ob for ob in objs if ob[0] >> 24 == 3 and pinfo(ob[0])[2] != 'block.frm']
    blocks = [ob for ob in objs if ob[0] >> 24 == 3 and pinfo(ob[0])[2] == 'block.frm']
    kept, gone = [], []
    for ob in walls:
        x, y = xy(ob[1])
        (gone if hsh(pi, x // 3, y // 3) % 100 < 55 or ob[1] in near else kept).append(ob)
    kt = set()
    for ob in kept: kt |= ring(ob[1], 1)
    kb = [ob for ob in blocks if ob[1] in kt and ob[1] not in near]
    junk, seen = [], set()
    for ob in gone:
        x, y = xy(ob[1]); k = (x // 3, y // 3)
        if k in seen or ob[1] in near: continue
        seen.add(k)
        if hsh(pi, *k, 7) % 100 < 60: junk.append([JUNK[hsh(pi, *k, 9) % 8], ob[1], 0, []])
    RUINS.append((name, [ob[:3] + [[]] for ob in kept + kb] + junk))
    print(f'развалины {name}: стен {len(kept)}/{len(walls)}, блоков {len(kb)}/{len(blocks)}, мусора {len(junk)}')

# проверка проходимости: от входа на карту до мест людей; закрытых пустых клеток в рамке развалин быть не должно
def flood(start, blk):
    seen = {start}; q = [start]
    while q:
        t = q.pop()
        for r in range(6):
            n = tdir(t, r, 1); x, y = xy(n)
            if n not in seen and n not in blk and 5 <= x <= 194 and 5 <= y <= 194: seen.add(n); q.append(n)
    return seen
ENTRANCE = 35301
def path_report(tag, objs, plots):
    blk = blocked(objs); reach = flood(ENTRANCE, blk); bad = []
    for k, (t, _) in PTS.items():
        if not ({t} | ring(t, 1)) & reach: bad.append(k)
    for name, r in plots:
        xs = [xy(ob[1])[0] for ob in r]; ys = [xy(ob[1])[1] for ob in r]
        box = {T(x, y) for x in range(min(xs) - 2, max(xs) + 3) for y in range(min(ys) - 2, max(ys) + 3)}
        red = box - reach - blk
        if red: bad.append(f'{name}: закрыто {len(red)}')
    return bad
ALLR = [ob for _, r in RUINS for ob in r]
base_bad = path_report('', found + slots + B('Бар', 2), RUINS)       # то же без развалин: палатки и бар 2 сами дают закутки
for tag, objs in (('основание + развалины', found + ALLR),
                  ('+ все стройки прораба + бар 1', found + [ob for n, r in RUINS[4:] for ob in r] + slots + B('Бар', 1)),
                  ('+ все стройки прораба + бар 2', found + [ob for n, r in RUINS[4:] for ob in r] + slots + B('Бар', 2))):
    bad = path_report(tag, objs, RUINS)
    print('проходимость', tag + ':', [b for b in bad if b not in base_bad] or 'ок', '(без развалин тоже:', base_bad, ')' if base_bad else ')')
    assert not [b for b in bad if b not in base_bad and not b.startswith('Бар')], bad

def calls(objs, ind='   '):
    out = []
    for pid, tile, rf, extra in objs:
        out.append(f'{ind}call lay_o({pid}, {tile}, {rf});')
        for fn, args in extra: out.append(f'{ind}call {fn.replace("tb_", "lay_")}({args});')
    return out

o = ['// Лагерь у скал на карте города: основание и постройки прораба (1-й уровень зданий песочницы).',
     '// Файл создан tools/layout/settle_emit.py из scripts_src/test/f2mtblay.h, руками не править.',
     '#ifndef F2MTLAY_H', '#define F2MTLAY_H', '']
for k, v in LAY.items(): o.append(f'#define LAY_{k:<10} ({v})')
o += ['#define LAY_CAR        (32283)   // стоянка машины у двора каравана', f'#define LAY_WAGONS     ({T(87, 150)})   // фургоны и брамины каравана: двор у южной дороги', '#define LAY_SLOTS      (7)    // 0 колодец, 1-2 огороды, 3-6 палатки', ''] + \
     [f'#define RUIN_{i:<2}        ({i})    // {n}' for i, (n, _) in enumerate(RUINS)] + \
     [f'#define RUIN_COUNT     ({len(RUINS)})', '#define RUIN_BAR       (9)    // бар 1-2 стоит в развалинах, сносить их к 3-му уровню', '',
      'variable lay_last;   // последний поставленный объект', '',
      'procedure lay_o(variable pid, variable tile, variable rf);', 'procedure lay_flg(variable fset, variable fclr);',
      'procedure lay_lit(variable dist, variable pct);', 'procedure lay_camp;', 'procedure lay_slot(variable slot);',
      'procedure lay_x(variable pid, variable tile);', 'procedure lay_ruins;', 'procedure lay_ruin_clear(variable plot);', '',
      '// Ставит объект, если на клетке такого еще нет. rf: поворот + 8 * кадр',
      'procedure lay_o(variable pid, variable tile, variable rf) begin',
      '   lay_last := 0;',
      '   if (tile_contains_pid_obj(tile, 0, pid)) then return;',
      '   lay_last := create_object(pid, tile, 0);',
      '   if (rf bwand 7) then anim(lay_last, 1000, rf bwand 7);',
      '   if (rf / 8) then anim(lay_last, 1010, rf / 8);',
      'end', '',
      'procedure lay_flg(variable fset, variable fclr) begin',
      '   if (lay_last) then set_flags(lay_last, (get_flags(lay_last) bwor fset) bwand bwnot(fclr));',
      'end', '',
      'procedure lay_lit(variable dist, variable pct) begin',
      '   if (lay_last) then obj_set_light_level(lay_last, pct, dist);',
      'end', '',
      f'// Основание: деревья {len(trees)}, костер со столом старосты {len(centre)}, палатка героя с сундуком {len(hero)},',
      f'// 3 армейские палатки переселенцев {", ".join(str(len(h)) for h in houses[:3])}, заколоченный старый колодец',
      'procedure lay_camp begin']
o += calls(trees) + calls(centre) + calls(hero)
for h in houses[:3]: o += calls(h)
o += ['   // старый колодец: заколоченный или уже починенный (сохранение с прежней карты лагеря)',
      '   if (not tile_contains_pid_obj(LAY_OLDWELL, 0, PID_WELL_OLD) and not tile_contains_pid_obj(LAY_OLDWELL, 0, PID_WELL_FIXED)) then begin',
      '      if (get_sfall_global_int(GV_WELL_OLD) == WELL_OLD_FIXED) then',
      '         create_object_sid(PID_WELL_FIXED, LAY_OLDWELL, 0, SCRIPT_F2MWELL);',
      '      else',
      '         create_object_sid(PID_WELL_OLD, LAY_OLDWELL, 0, SCRIPT_F2MWELL);',
      '   end', 'end', '',
      '// Постройки прораба: 0 новый колодец, 1-2 огороды, 3-6 палатки (4-7-й участки жилья)',
      'procedure lay_slot(variable slot) begin',
      '   if (slot >= 3) then call lay_ruin_clear(slot - 3);   // палатки 4-7 встают на участки жилья 4-7: сперва снос развалин',
      '   if (slot == 0) then begin',
      '      if (not tile_contains_pid_obj(LAY_NEWWELL, 0, PID_WELL_NEW)) then create_object_sid(PID_WELL_NEW, LAY_NEWWELL, 0, SCRIPT_F2MWELL);']
for i, g in enumerate(gardens):
    o.append(f'   end else if (slot == {1 + i}) then begin   // огород {i + 1}: {len(g)}')
    o += calls(g, '      ')
for i, h in enumerate(houses[3:7]):
    o.append(f'   end else if (slot == {3 + i}) then begin   // палатка {4 + i}: {len(h)}')
    o += calls(h, '      ')
o += ['   end', 'end', '',
      '// Убирает объект с клетки (снос развалин)',
      'procedure lay_x(variable pid, variable tile) begin',
      '   variable obj;',
      '   obj := tile_contains_pid_obj(tile, 0, pid);',
      '   if (obj) then destroy_object(obj);',
      'end', '',
      f'// Развалины на участках будущих зданий: стены 4-го уровня с проломами, блоки, мусор ({len(ALLR)} объектов)',
      'procedure lay_ruins begin']
for name, r in RUINS:
    o.append(f'   // {name}: {len(r)}'); o += calls(r)
o += ['end', '', '// Снос развалин одного участка (RUIN_*) перед стройкой здания на нем', 'procedure lay_ruin_clear(variable plot) begin']
for i, (name, r) in enumerate(RUINS):
    o.append(f'   {"if" if i == 0 else "end else if"} (plot == {i}) then begin   // {name}')
    o += [f'      call lay_x({pid}, {tile});' for pid, tile, rf, extra in r]
o += ['   end', 'end', '', '#endif', '']
open(os.path.join(ROOT, 'scripts_src/f2mtlay.h'), 'w', encoding='utf-8').write('\n'.join(o))
print('f2mtlay.h', len(o), 'lines;', 'LAY', LAY)

# ---- карта: пол города и кольцо выходов на карту мира (EXITGRID, как на пустынных картах: карта -2 = карта мира)
m = bytearray(open(os.path.join(ROOT, 'mod/test/maps/f2mtown.map'), 'rb').read())
assert m[-16:] == bytes(16), 'у карты песочницы есть объекты?'
m = m[:-16]
m[4:20] = b'F2MSET.MAP'.ljust(16, b'\0')
EDGE = 4
ring = [T(x, y) for x in range(EDGE, 200 - EDGE) for y in (EDGE, 199 - EDGE)] + \
       [T(x, y) for y in range(EDGE + 1, 199 - EDGE) for x in (EDGE, 199 - EDGE)]
recs = b''
for i, t in enumerate(ring):
    # поля объекта как у выходов desert1: id, клетка, смещения 0, кадр 0, поворот 0, FID 0x05000021, флаги, уровень 0,
    # PID 0x05000010, cid -1, свет 0, без скрипта; инвентарь пуст; misc: 0; выход: карта -2, клетка -1, уровень 0, поворот 0
    recs += struct.pack('>26i', 100000 + i, t, 0, 0, 0, 0, 0, 0, 0x05000021, -1610579944, 0, 0x05000010, -1, 0, 0, 0, -1, -1,
                        0, 0, 0, 0, -2, -1, 0, 0)
m += struct.pack('>2i', len(ring), len(ring)) + recs + struct.pack('>2i', 0, 0)
os.makedirs(os.path.join(ROOT, 'mod/data/maps'), exist_ok=True)
open(os.path.join(ROOT, 'mod/data/maps/f2mset.map'), 'wb').write(m)
print('f2mset.map', len(m), 'exit grids', len(ring))
