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
PLOTS = [(f'Жилье {k + 1}', houses4[k]) for k in range(3, 8)] + \
        [(n, B(n, 4)) for n in ('Склад', 'Мастерская', 'Охрана', 'Ферма браминов', 'Бар', 'Медпункт')]
found = trees + centre + hero + sum(houses[:3], []) + old_well
slots = new_well + sum(gardens, []) + sum(houses[3:7], [])
bar12 = B('Бар', 1) + B('Бар', 2)
PTS = dict(TED=(LAY['TED'], 3), FOREMAN=(LAY['FOREMAN'], 3), CHIEF=(LAY['CHIEF'], 4), WAGONS=(T(87, 150), 9), CAR=(32283, 4),
           FIRE=(LAY['FIRE'], 7))
keepout = set()
for t, r in PTS.values(): keepout |= ring(t, r)
# Куски руин берем целиком из карт развалин города (случайные встречи city1 и city2, стены nec*): связная группа стен
# со своими блоками block.frm и травой рядом. Для каждого участка ищем на этих картах окно размером с участок (рамка
# объектов 4-го уровня), где больше всего целых кусков, которые ничему не мешают, и переносим их со сдвигом
# (по x на четное число клеток: так шестиугольники ложатся как на карте игры). Кусок не режем: мешает — не берем.
FLAG_MASK = 0x8 | 0x10 | 0x0000C000 | 0x000F0000 | 0x10000000 | 0x20000000 | 0x80000000
def src_pieces(mapname):
    tmp = os.path.join('/tmp', mapname + '.map'); open(tmp, 'wb').write(mapparse.dat(f'maps\\{mapname}.map'))
    m = mapparse.parse(tmp)
    objs = []
    for e in m['objs']:
        if e['elev'] != 0 or e['pid'] >> 24 not in (2, 3) or e.get('sid', -1) not in (-1, None): continue
        pf = pinfo(e['pid'])[1]; d = (e['flags'] ^ pf) & FLAG_MASK
        extra = [('tb_flg', f'{e["flags"] & d}, {pf & d}')] if d else []
        objs.append([e['pid'], e['tile'], (e['rot'] & 7) + 8 * e['frame'], extra])
    walls = [o for o in objs if o[0] >> 24 == 3]
    groups = []
    for o in walls:
        x, y = xy(o[1]); hit = [g for g in groups if any(abs(x - a) <= 2 and abs(y - b) <= 2 for a, b in g['pts'])]
        g = hit[0] if hit else dict(pts=[], objs=[])
        if not hit: groups.append(g)
        for h in hit[1:]: g['pts'] += h['pts']; g['objs'] += h['objs']; groups.remove(h)
        g['pts'].append((x, y)); g['objs'].append(o)
    for o in objs:                                   # трава и прочие декорации рядом с куском — к нему
        if o[0] >> 24 != 2: continue
        x, y = xy(o[1])
        for g in groups:
            if any(abs(x - a) <= 2 and abs(y - b) <= 2 for a, b in g['pts']): g['objs'].append(o); break
    return [(mapname, i, g['objs']) for i, g in enumerate(groups)
            if any(pinfo(o[0])[2] != 'block.frm' for o in g['objs'] if o[0] >> 24 == 3)]
SRC_PIECES = src_pieces('city1') + src_pieces('city2')
print('кусков руин в city1/city2:', len(SRC_PIECES))
RUINS, used, taken = [None] * len(PLOTS), set(), set()
for pi in sorted(range(len(PLOTS)), key=lambda i: PLOTS[i][0] != 'Бар'):   # бар первым: ему руины нужнее всего
    name, objs = PLOTS[pi]
    own = houses[pi + 3] if pi < 4 else []        # своя палатка прораба: перед ней развалины сносятся
    near = set(taken)
    for ob in found + [q for q in slots if q not in own] + bar12: near |= ring(ob[1], 1)   # бар 1-2 стоит среди руин бара
    near |= keepout
    if name == 'Охрана': objs = [ob for ob in objs if 38 <= xy(ob[1])[0] <= 70 and 105 <= xy(ob[1])[1] <= 141]   # казарма, без постов у ворот
    xs = [xy(ob[1])[0] for ob in objs]; ys = [xy(ob[1])[1] for ob in objs]
    X0, X1, Y0, Y1 = min(xs), max(xs), min(ys), max(ys)
    r, npieces = [], 0
    for rnd in range(3):                           # до трех окон на участок: второе и третье добирают пустые места
        best = None
        for mapname in ('city1', 'city2'):
            P = [p for p in SRC_PIECES if p[0] == mapname and (p[0], p[1]) not in used]
            for sx in range(X0 % 2, 200 - (X1 - X0), 2):
                dx = X0 - sx
                for sy in range(0, 200 - (Y1 - Y0)):
                    dy = Y0 - sy; got = []; score = 0; occ = set()
                    for p in P:
                        ts = [o[1] for o in p[2]]
                        if not all(sx <= t % 200 <= sx + X1 - X0 and sy <= t // 200 <= sy + Y1 - Y0 for t in ts): continue
                        moved = [t + dx + 200 * dy for t in ts]
                        if any(t in near for t in moved): continue
                        got.append(p); score += sum(1 for o in p[2] if o[0] >> 24 == 3)
                    if got and (best is None or score > best[0]): best = (score, dx, dy, got)
        if not best or best[0] < (1 if rnd == 0 else 8): break
        score, dx, dy, got = best
        for p in got:
            used.add((p[0], p[1])); npieces += 1
            for o in p[2]:
                t = o[1] + dx + 200 * dy; r.append([o[0], t, o[2], o[3]]); near |= ring(t, 1); taken |= ring(t, 1)
    RUINS[pi] = (name, r)
    print(f'руины {name}: кусков {npieces}, объектов {len(r)}')

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
        if not r: continue
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

# развалины 0.5.1 (стены наших зданий, Егор отклонил): убираем из сохранений, где они уже стоят
OLD_RUINS = [(33556258, 13137), (33556258, 18753), (33556258, 23338), (33556258, 27728), (33556258, 7848), (33556258, 7870), (33556259, 12940), (33556259, 14559), (33556259, 16154), (33556259, 21505), (33556259, 21941), (33556259, 22908), (33556259, 23464), (33556259, 24154), (33556259, 26850), (33556259, 27110), (33556259, 7036), (33556259, 8456), (33556259, 9670), (33556260, 16359), (33556260, 17134), (33556260, 17542), (33556260, 18949), (33556260, 21516), (33556260, 22308), (33556260, 23046), (33556260, 27710), (33556260, 7069), (33556260, 7856), (33556261, 18160), (33556261, 19934), (33556261, 23060), (33556261, 23458), (33556261, 25250), (33556261, 27718), (33556261, 7496), (33556261, 7836), (33556261, 8470), (33556261, 9044), (33556262, 13149), (33556262, 15359), (33556262, 16355), (33556262, 17140), (33556262, 23508), (33556262, 24754), (33556262, 26356), (33556262, 28511), (33556262, 29160), (33556262, 7262), (33556262, 9644), (33556263, 12952), (33556263, 16142), (33556263, 18153), (33556263, 23054), (33556263, 23160), (33556263, 23538), (33556263, 24127), (33556263, 25244), (33556263, 25548), (33556263, 25864), (33556263, 26518), (33556263, 28326), (33556263, 7051), (33556263, 7248), (33556263, 8496), (33556263, 9036), (33556264, 13935), (33556264, 17753), (33556264, 18760), (33556264, 19534), (33556264, 21528), (33556264, 21938), (33556264, 24064), (33556264, 24644), (33556264, 25346), (33556264, 25510), (33556264, 25850), (33556264, 26451), (33556264, 28318), (33556264, 7076), (33556264, 7236), (33556264, 7896), (33556264, 9866), (33556265, 17534), (33556265, 18740), (33556265, 23048), (33556265, 23341), (33556265, 23912), (33556265, 7042), (33556265, 7456), (50331744, 19536), (50331744, 19540), (50331744, 19558), (50331744, 20338), (50331744, 20340), (50331745, 19535), (50331745, 19537), (50331745, 19539), (50331745, 19541), (50331745, 19543), (50331745, 19559), (50331745, 20339), (50331745, 20343), (50331746, 19556), (50331746, 23156), (50331747, 19557), (50331747, 23157), (50331748, 19546), (50331749, 19545), (50331753, 23158), (50331755, 24346), (50331756, 18134), (50331756, 23546), (50331757, 18334), (50331757, 23746), (50331758, 17560), (50331758, 18534), (50331758, 23946), (50331759, 17760), (50331759, 18734), (50331759, 24746), (50331760, 19944), (50331760, 22362), (50331760, 24946), (50331761, 20144), (50331761, 22162), (50331761, 22562), (50331761, 25146), (50331762, 21962), (50331762, 22762), (50331762, 23346), (50331762, 24546), (50331763, 19360), (50331768, 19134), (50331768, 21754), (50331768, 22154), (50331768, 22554), (50331768, 22754), (50331769, 22354), (50331774, 17155), (50331777, 17135), (50331777, 17137), (50331777, 17141), (50331777, 17149), (50331777, 17151), (50331777, 17159), (50331778, 17136), (50331778, 17150), (50331778, 17152), (50331779, 17154), (50331785, 19538), (50331785, 19542), (50331786, 17148), (50331790, 16339), (50331790, 16341), (50331790, 16349), (50331790, 16357), (50331790, 18945), (50331791, 16138), (50331791, 16140), (50331791, 16148), (50331791, 16156), (50331791, 16158), (50331791, 17552), (50331791, 18744), (50331791, 18746), (50331792, 13735), (50331792, 16743), (50331792, 17143), (50331793, 13759), (50331793, 14159), (50331793, 15759), (50331793, 16159), (50331793, 16947), (50331793, 17547), (50331795, 13335), (50331795, 13735), (50331795, 15335), (50331795, 16743), (50331795, 17143), (50331795, 18139), (50331796, 13359), (50331796, 13759), (50331796, 14159), (50331796, 15135), (50331796, 15535), (50331796, 15759), (50331796, 16159), (50331796, 16547), (50331796, 16947), (50331796, 17147), (50331796, 17343), (50331796, 17939), (50331796, 18339), (50331796, 18539), (50331798, 13141), (50331798, 13143), (50331798, 13145), (50331798, 13153), (50331798, 13155), (50331798, 17749), (50331798, 17751), (50331799, 12942), (50331799, 12944), (50331799, 12946), (50331799, 12954), (50331799, 17540), (50331799, 17548), (50331799, 17550), (50331800, 17739), (50331801, 19560), (50331896, 19544), (50331898, 21954), (50331998, 21937), (50331999, 21936), (50332015, 17142), (50332015, 17160), (50332015, 21562), (50332068, 17960), (50332074, 25354), (50332075, 25554), (50332076, 25753), (50332077, 25552), (50332078, 25751), (50332085, 25743), (50332086, 25542), (50332087, 25741), (50332088, 25540), (50332089, 25739), (50332090, 25538), (50332095, 23954), (50332096, 23754), (50332097, 23554), (50332104, 23344), (50332106, 23346), (50332107, 23345), (50332131, 23523), (50332132, 23723), (50332133, 23923), (50332134, 23722), (50332269, 17360), (50332269, 19334), (50332269, 19744), (50332269, 21503), (50332269, 21530), (50332269, 21762), (50332269, 22954), (50332269, 23045), (50332269, 23064), (50332269, 23144), (50332269, 23146), (50332269, 23702), (50332269, 23904), (50332269, 24252), (50332269, 25728), (50332269, 26263), (50332269, 26362), (50332269, 26562), (50332269, 26844), (50332269, 27044), (50332269, 27046), (50332269, 29152), (50332269, 29154), (50332269, 29156), (50332269, 7049), (50332269, 7056), (50332269, 7063), (50332269, 7075), (50332269, 7082), (50332269, 7089), (50332269, 7244), (50332269, 7270), (50332269, 9648), (50332269, 9662), (50332270, 13535), (50332270, 13559), (50332270, 13959), (50332270, 14359), (50332270, 15559), (50332270, 15959), (50332270, 16543), (50332270, 16747), (50332270, 16943), (50332270, 17337), (50332270, 17341), (50332270, 17347), (50332270, 17349), (50332270, 17351), (50332270, 17355), (50332270, 17359), (50332270, 17543), (50332270, 17547), (50332270, 18739), (50332270, 19735), (50332270, 19737), (50332270, 19739), (50332270, 19741), (50332270, 19743), (50332270, 19745), (50332270, 19747), (50332270, 19755), (50332270, 19757), (50332270, 19759), (50332270, 23322), (50332270, 23323), (50332270, 25338), (50332270, 25713), (50332270, 25715), (50332270, 25719), (50332270, 25721), (50332270, 25723), (50332270, 26353), (50332270, 26463), (50332270, 27249), (50332270, 28520), (50332270, 28522), (50332270, 28524), (50332270, 28526), (50332382, 20344), (50332390, 20342), (50332394, 18934), (50332497, 25064), (50332497, 26962), (50332497, 27562), (50332498, 22330), (50332498, 24664), (50332498, 26928), (50332498, 27128), (50332498, 27162), (50332499, 22530), (50332499, 24864), (50332499, 26128), (50332499, 27362), (50332500, 26328), (50332500, 8444), (50332500, 8482), (50332501, 26728), (50332501, 8844), (50332501, 8882), (50332502, 22730), (50332504, 27328), (50332505, 27528), (50332506, 7644), (50332506, 7670), (50332506, 9056), (50332506, 9070), (50332506, 9082), (50332506, 9096), (50332507, 7844), (50332507, 9256), (50332507, 9270), (50332507, 9282), (50332507, 9296), (50332508, 8044), (50332508, 9456), (50332508, 9470), (50332508, 9482), (50332508, 9496), (50332509, 8244), (50332509, 9656), (50332509, 9682), (50332510, 25928), (50332510, 26762), (50332510, 7444), (50332510, 7470), (50332511, 27050), (50332511, 9856), (50332511, 9882), (50332513, 23924), (50332513, 26260), (50332513, 27048), (50332513, 28322), (50332514, 24111), (50332514, 24115), (50332514, 24121), (50332514, 24123), (50332514, 27247), (50332514, 28523), (50332515, 23920), (50332515, 26252), (50332515, 26258), (50332515, 26262), (50332515, 28320), (50332515, 9854), (50332515, 9878), (50332515, 9880), (50332515, 9892), (50332515, 9894), (50332516, 24105), (50332516, 24109), (50332516, 24113), (50332516, 24117), (50332516, 24119), (50332516, 24125), (50332516, 26461), (50332516, 28521), (50332521, 26256), (50332522, 26254), (50332524, 28525), (50332525, 28324), (50332526, 27245), (50332526, 29353), (50332527, 21523), (50332527, 21529), (50332527, 23053), (50332527, 23059), (50332527, 25515), (50332527, 26361), (50332527, 7055), (50332527, 7081), (50332528, 21510), (50332528, 21522), (50332528, 23052), (50332528, 23058), (50332528, 25520), (50332528, 26360), (50332528, 7050), (50332528, 7064), (50332528, 7090), (50332529, 23051), (50332529, 23057), (50332529, 23063), (50332529, 25517), (50332529, 26359), (50332529, 7041), (50332529, 7067), (50332529, 7079), (50332530, 21508), (50332530, 25518), (50332530, 7040), (50332530, 7066), (50332530, 7078), (50332530, 7092), (50332531, 21525), (50332531, 25519), (50332531, 7039), (50332531, 7065), (50332531, 7091), (50332532, 21512), (50332532, 21518), (50332532, 21524), (50332532, 25516), (50332532, 7054), (50332532, 7068), (50332532, 7080), (50332533, 21517), (50332533, 25521), (50332534, 21504), (50332534, 25514), (50332534, 25522), (50332535, 21702), (50332535, 22502), (50332535, 23244), (50332535, 24044), (50332535, 26444), (50332535, 26510), (50332535, 28152), (50332535, 7274), (50332535, 7288), (50332535, 8062), (50332535, 8074), (50332535, 8088), (50332535, 8836), (50332535, 8848), (50332535, 8862), (50332536, 21902), (50332536, 22702), (50332536, 23444), (50332536, 24244), (50332536, 26644), (50332536, 26710), (50332536, 7474), (50332536, 7488), (50332536, 8262), (50332536, 8274), (50332536, 8288), (50332536, 9048), (50332536, 9062), (50332537, 22102), (50332537, 23502), (50332537, 23644), (50332537, 24444), (50332537, 26910), (50332537, 27752), (50332537, 7674), (50332537, 7688), (50332537, 8436), (50332537, 8448), (50332537, 8462), (50332537, 9248), (50332537, 9262), (50332538, 22302), (50332538, 23844), (50332538, 27952), (50332538, 7862), (50332538, 7874), (50332538, 7888), (50332538, 8636), (50332538, 8648), (50332538, 8662), (50332538, 9448), (50332538, 9462), (50332539, 23044), (50332539, 26352), (50332539, 7048), (50332539, 7062), (50332539, 7074), (50332546, 21708), (50332546, 23258), (50332546, 25718), (50332549, 21908), (50332549, 22514), (50332549, 23450), (50332549, 25858), (50332549, 27518), (50332550, 22108), (50332550, 23650), (50332550, 26058), (50332550, 27318), (50332551, 23850), (50332552, 24050), (50332553, 27118), (50332557, 22711), (50332557, 25049), (50332557, 25063), (50332558, 25048), (50332558, 25062), (50332559, 22713), (50332559, 24251), (50332559, 25061), (50332560, 22712), (50332560, 25060), (50332564, 24250), (50332565, 22714), (50332565, 25050), (50332807, 19134), (50332918, 16343), (50332919, 16347), (50332920, 17747), (50333178, 29355), (50333238, 24251), (50333239, 24450), (50333239, 25258), (50333240, 22314), (50333240, 24850), (50333240, 25658)]

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
      'procedure lay_x(variable pid, variable tile);', 'procedure lay_ruins;', 'procedure lay_ruins_old;', 'procedure lay_ruin_clear(variable plot);', '',
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
o += ['end', '', '// Развалины 0.5.1 (из стен наших зданий): убрать из сохранений, где они уже стоят', 'procedure lay_ruins_old begin']
o += [f'   call lay_x({a}, {b});' for a, b in OLD_RUINS]
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
