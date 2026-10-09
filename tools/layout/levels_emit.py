# Уровни зданий поселения (0.7.0): стройка Хэнка выше 1-го уровня и 1-й уровень мастерской, поста охраны, бара и медпункта.
# Берет уровни зданий из песочницы (scripts_src/test/f2mtblay.h), делит их по зданиям лагеря (как settle_emit.py) и пишет
#   scripts_src/f2mlvl.h — переход каждого здания на следующий уровень: снос развалин участка, перенос вещей из сундуков
#                          старого уровня в сундук нового, снос старых объектов, установка новых;
#                          места людей по уровням (днем у дома и на огороде, ночью у кровати), место старосты и костра.
# Проверяет: новые объекты не встают на основание, бочки, частокол, могилу и места людей; проходимость от въезда до мест
# людей при всех уровнях 1 и 2 и при случайных смесях. Номера зданий (U_*) — как в scripts_src/f2mbld.h.
# Использование: levels_emit.py
import random
from levels_lib import *

LAYF = os.path.join(ROOT, 'scripts_src/f2mtlay.h')
CAMP = read_calls(LAYF, r'^procedure lay_camp begin', r'^end', 'lay')
SLOTS = read_calls(LAYF, r'^procedure lay_slot\(.*begin', r'^end', 'lay')
LIGHTS = read_calls(LAYF, r'^procedure lay_lights begin', r'^end', 'lay')
PAL = [o for o in SYS[4]]
defs = {m.group(1): int(m.group(2)) for m in re.finditer(r'#define LAY_(\w+)\s+\((\d+)\)', open(LAYF, encoding='utf-8').read())}
RUINP = {}                                       # развалины по участкам RUIN_*
cur = None
for line in open(LAYF, encoding='utf-8'):
    m = re.search(r'if \(plot == (\d+)\) then begin', line)
    if m: cur = int(m.group(1)); RUINP[cur] = []; continue
    m = re.match(r'\s+call lay_x\((\d+), (\d+)\);', line)
    if m and cur is not None: RUINP[cur].append([int(m.group(1)), int(m.group(2)), 0, []])
    if line.startswith('end') and cur is not None: break
RUINS_ALL = read_calls(LAYF, r'^procedure lay_ruins begin', r'^end', 'lay')
assert sum(map(len, RUINP.values())) == len(RUINS_ALL), (sum(map(len, RUINP.values())), len(RUINS_ALL))
GRAVE = 31760
PID_WELLS = {33555425, 33556410, 33554815}
FIRE1 = defs['FIRE']
cx, cy = xy(FIRE1)

def clean(objs): return [o for o in objs if o[0] >> 24 != 1 and o[0] not in PID_WELLS]

# ---- здания лагеря (номера как U_* в f2mbld.h)
def house_of(o):
    x, y = xy(o[1]); u = 199 - x
    col = max(0, min(4, (u - 102) // 13)); return col if y < 50 else 5 + min(2, col)
H1 = [[o for o in B('Жилье') if house_of(o) == i] for i in range(8)]
horder = sorted(range(8), key=lambda i: (center(H1[i])[0] - cx) ** 2 + (center(H1[i])[1] - cy) ** 2)
def houses(lv): return [[o for o in B('Жилье', lv) if house_of(o) == i] for i in horder]
def gardens(lv): return sorted(clusters(B('Огороды', lv), 2), key=lambda g: center(g)[1])
LEVELS = (1, 2)
U = {}   # u -> dict(name, lv={1: objs or [], 2: objs}, ruin=plot or None, placed1=True если 1-й уровень ставит старый код)
U[0] = dict(name='Старый колодец', key='Старый колодец', old1=True)
U[1] = dict(name='Новый колодец', key='Новый колодец', old1=True)
U[2] = dict(name='Огород 1', garden=0, old1=True)
U[3] = dict(name='Огород 2', garden=1, old1=True)
for i in range(8): U[4 + i] = dict(name=f'Жилье {i + 1}', house=i, old1=True, ruin=(i - 3) if i >= 3 else None)
U[12] = dict(name='Склад', key='Склад', empty1=True, ruin=5)
U[13] = dict(name='Центр', key='Центр', old1=True)
U[14] = dict(name='Мастерская', key='Мастерская', ruin=6)
U[15] = dict(name='Охрана', key='Охрана')
U[16] = dict(name='Ферма браминов', key='Ферма браминов', empty1=True, ruin=8)
U[17] = dict(name='Бар', key='Бар')                      # 1-2 стоят в развалинах бара, снос к 3-му уровню
U[18] = dict(name='Медпункт', key='Медпункт', ruin=10)
U[19] = dict(name='Дом героя', key='Дом героя', old1=True)
for u, d in U.items():
    d['lv'] = {}
    for lv in LEVELS:
        if 'garden' in d: objs = gardens(lv)[d['garden']]
        elif 'house' in d: objs = houses(lv)[d['house']]
        else: objs = B(d['key'], lv)
        d['lv'][lv] = clean(objs)
    if d.get('empty1'): d['lv'][1] = []
# Охрана 2 (buildings-levels.md): «Пост с прожектором» — тот же пост у южных ворот плюс прожектор vclight1.
# В песочнице 2-й уровень — посты у обоих ворот (это ближе к караулке), поэтому собираем уровень здесь.
SEARCHLIGHT = T(*[int(v) for v in os.environ.get('GUARD_LIGHT', '110,164').split(',')])
U[15]['lv'][2] = [list(o) for o in U[15]['lv'][1]] + [[33555818, SEARCHLIGHT, 0, [('lit', '6, 100')]]]
# сверка с тем, что уже ставит f2mtlay.h (основание и стройки прораба)
have = {(o[0], o[1]) for o in CAMP + SLOTS}
for u, d in U.items():
    if d.get('old1'):
        miss = [o for o in d['lv'][1] if (o[0], o[1]) not in have]
        assert not miss, (d['name'], len(miss))
# Огороды 2-го уровня — те же грядки плюс новые: 1-й уровень целиком внутри 2-го
for u in (2, 3):
    a = {(o[0], o[1]) for o in U[u]['lv'][1]}; b = {(o[0], o[1]) for o in U[u]['lv'][2]}
    assert a <= b, U[u]['name']

# Бар 1 и медпункт 1 — тоже стройки Хэнка «на коленке»
# ---- костер и староста на 2-м уровне центра: шатер встает на место стола, костер — перед шатром
fire2 = [o for o in U[13]['lv'][2] if o[0] == 33555632]
assert len(fire2) == 1
FIRE2 = fire2[0][1]
assert f'#define BLD_FIRE2       ({FIRE2})' in open(os.path.join(ROOT, 'scripts_src/f2mbld.h'), encoding='utf-8').read(), FIRE2

# ---- что уже стоит на карте и чего новые уровни касаться не должны
def oset(objs): return {o[1] for o in objs}
fixed_blk = blocked(LIGHTS + PAL) | {GRAVE}
PEOPLE = {k: defs[k] for k in ('TED', 'FOREMAN', 'CHIEF')}
PEOPLE['HANK'] = tdir(defs['CHIEF'], 5, 2)
PEOPLE['WAGONS'] = T(87, 150); PEOPLE['CAR'] = 32283
PEOPLE['GATE_IN'] = 32500; PEOPLE['GATE_OUT'] = 34500     # ополчение и главарь у южных ворот (1.3)
for i in range(6): PEOPLE[f'MIL{i}'] = tdir(32500, i, 2)
for d in range(6): PEOPLE[f'GRAVE{d}'] = tdir(GRAVE, d, 1)
SARA = tdir(defs['CHIEF'], 2, 3)
# старые места людей (f2mspots.h) — для 1-го уровня оставляем как есть
SP_SRC = open(os.path.join(ROOT, 'scripts_src/f2mspots.h'), encoding='utf-8').read()
DAY1 = {int(a): (int(b), int(c)) for a, b, c in re.findall(r'if \(slot == (\d+)\) then begin if \(k == 0\) then return (\d+); return (\d+); end', SP_SRC)}
NIGHT1 = {int(a): (int(b), int(c), int(d)) for a, b, c, d in re.findall(r'if \(tent == (\d+)\) then begin if \(k == 0\) then return (\d+); if \(k == 1\) then return (\d+); return (\d+); end', SP_SRC)}

errs = []
for u, d in U.items():
    for lv in LEVELS:
        if lv == 1 and d.get('old1'): continue
        nb = blocked(d['lv'][lv])
        for k, t in list(PEOPLE.items()) + [('SARA', SARA), ('FIRE1', FIRE1)]:
            if k == 'TED' and u == 13: continue
            if k == 'FIRE1' and u == 13: continue
            if t in nb: errs.append(f'{d["name"]} {lv}: на месте {k}')
        hit = nb & fixed_blk
        if hit: errs.append(f'{d["name"]} {lv}: на бочке/частоколе/могиле {[xy(t) for t in hit]}')
        hit = oset(d['lv'][lv]) & (oset(LIGHTS) | {GRAVE})
        if hit: errs.append(f'{d["name"]} {lv}: объект на бочке или могиле {[xy(t) for t in hit]}')
        # с основанием (кроме своих объектов 1-го уровня) и с чужими зданиями любого уровня
        own1 = oset(d['lv'][1]) if d.get('old1') else set()
        others = blocked([o for o in CAMP if o[1] not in own1])
        for v, e in U.items():
            if v == u: continue
            for lv2 in LEVELS:
                hit = nb & blocked(e['lv'][lv2])
                if hit: errs.append(f'{d["name"]} {lv} и {e["name"]} {lv2}: {len(hit)} клеток, {[xy(t) for t in list(hit)[:3]]}')
        # развалины чужих участков (свой участок сносится перед стройкой; бар 1-2 стоит в своих развалинах)
        rb = blocked([q for p, objs in RUINP.items() if p != d.get('ruin') for q in objs])
        hit = nb & rb
        if hit: errs.append(f'{d["name"]} {lv}: на развалинах {[xy(t) for t in list(hit)[:4]]}')
        hit = oset(d['lv'][lv]) & oset([q for p, objs in RUINP.items() if p != d.get('ruin') for q in objs])
        if hit: errs.append(f'{d["name"]} {lv}: объект на клетке развалин {len(hit)}')
        hit = nb & others
        if hit and u != 13: errs.append(f'{d["name"]} {lv}: на основании {[xy(t) for t in list(hit)[:4]]}')
print('\n'.join(sorted(set(errs))) or 'наложений нет')
errs = [e for e in errs if 'FOREMAN' not in e]   # Хэнк на 2-м уровне центра убегает к новому месту (LVL_SAFE2)
assert not errs, errs

# ---- проходимость и места людей
ENTRANCE = 35301
def tdist(a, b):
    for r in range(0, 12):
        if a in ring(b, r): return r
    return 99
BED = None
def is_bed(pid):
    global BED
    if BED is None:
        t = mapparse.dat0('text\\english\\game\\pro_scen.msg').decode('cp1251', 'replace')
        BED = {int(m.group(1)) for m in re.finditer(r'\{(\d+)\}\{[^}]*\}\{Bed\}', t)}
    return pid >> 24 == 2 and struct.unpack_from('>i', mapparse.proto(pid), 4)[0] in BED
def ruins_left(cfg):
    """развалины, что еще стоят при уровнях cfg: участок сносится, когда на нем встают первые объекты здания"""
    left = []
    for p, objs in RUINP.items():
        owner = [u for u, d in U.items() if d.get('ruin') == p]
        if owner and cfg[owner[0]] >= (2 if U[owner[0]].get('empty1') else 1): continue
        left += objs
    return left
def world(cfg):
    """все объекты при уровнях cfg (u -> 0..2)"""
    objs = [o for o in CAMP if not any(cfg[u] >= 2 and (o[0], o[1]) in {(q[0], q[1]) for q in d['lv'][1]} for u, d in U.items() if d.get('old1'))]
    objs += LIGHTS + PAL + ruins_left(cfg)
    for u, d in U.items():
        lv = cfg[u]
        if lv == 0: continue
        if lv == 1 and d.get('old1') and u in (0, 1, 13) or (lv == 1 and 4 <= u <= 6): continue   # уже в CAMP
        objs += d['lv'][lv]
    for t in range(8):   # слоты прораба 1-го уровня (палатки 4-8, огороды, палатка героя) — уже в d['lv'][1]
        pass
    return objs
def people(cfg):
    p = dict(PEOPLE); p['SARA'] = SARA
    if cfg[13] >= 2: p['TED'] = TED2; p['FOREMAN'] = SAFE2; p['FIRE'] = FIRE2
    else: p['FIRE'] = FIRE1
    return p
CFG1 = {u: 1 for u in U}; CFG1.update({14: 0, 15: 0, 17: 0, 18: 0})
CFG2 = {u: 2 for u in U}
blk_all = set()
for u, d in U.items():
    for lv in LEVELS: blk_all |= blocked(d['lv'][lv])
blk_all |= blocked(CAMP + LIGHTS + PAL) | {GRAVE}
reach2 = flood(ENTRANCE, blocked(world(CFG2)) | {GRAVE})
def near_free(anchor, rmin, rmax, avoid):
    for r in range(rmin, rmax + 1):
        for t in sorted(ring(anchor, r) - ring(anchor, r - 1), key=lambda t: xy(t)):
            if t in reach2 and t not in blk_all and not (ring(t, 1) & avoid): return t
TED2 = near_free(tdir(FIRE2, 0, 1), 1, 4, {FIRE2})
SAFE2 = near_free(tdir(FIRE2, 2, 3), 0, 4, {FIRE2, TED2})
print('костер 2', xy(FIRE2), 'староста', xy(TED2), 'Хэнк в бою', xy(SAFE2))

# Радио у старосты (радист Сэм, 0.7.1): стол ltable2 с пультом comp5 (картинка pictures-radio/radio_stol.png),
# рядом место радиста. Одно место на любом уровне центра: свободно при уровнях 1 и 2 всех зданий, не на местах людей
PID_RTABLE, PID_RCOMP = 33554926, 33554487
reach1 = flood(ENTRANCE, blocked(world(CFG1)) | {GRAVE})
pp = set(people(CFG1).values()) | {T(x, y) for x, y in []} | set(people(CFG2).values())
RADIO = SAM = None
for r in range(3, 9):
    for t in sorted(ring(FIRE1, r) - ring(FIRE1, r - 1), key=lambda t: (tdist(t, FIRE2), xy(t))):
        if t in blk_all or ring(t, 1) & pp or t not in reach1 or t not in reach2: continue
        sam = [n for n in sorted(ring(t, 1) - {t}) if n not in blk_all and n in reach1 and n in reach2 and not ring(n, 1) & pp]
        if not sam: continue
        b1 = blocked(world(CFG1)) | {GRAVE, t}; b2 = blocked(world(CFG2)) | {GRAVE, t}
        r1 = flood(ENTRANCE, b1); r2 = flood(ENTRANCE, b2)
        if all((ring(q, 1) - {q}) & r1 for q in people(CFG1).values()) and all((ring(q, 1) - {q}) & r2 for q in people(CFG2).values()) \
           and sam[0] in r1 and sam[0] in r2:
            RADIO, SAM = t, sam[0]; break
    if RADIO: break
assert RADIO
blk_all |= {RADIO}
_b = open(os.path.join(ROOT, 'scripts_src/f2mbld.h'), encoding='utf-8').read()
assert f'#define BLD_RADIO       ({RADIO})' in _b and f'#define BLD_SAM         ({SAM})' in _b, (RADIO, SAM)
print('радио', xy(RADIO), 'радист', xy(SAM))

def check(cfg, tag):
    blk = blocked(world(cfg)) | {GRAVE}
    reach = flood(ENTRANCE, blk)
    bad = [k for k, t in people(cfg).items() if not ((ring(t, 1) - {t}) & reach)]
    return bad
for tag, cfg in (('уровень 1', CFG1), ('уровень 2', CFG2)):
    print('проходимость', tag, check(cfg, tag) or 'ок')
    assert not check(cfg, tag)
rnd = random.Random(5)
for i in range(40):
    cfg = {u: rnd.choice([1, 2]) for u in U}
    for u in (14, 15, 17, 18): cfg[u] = rnd.choice([0, 1, 2])
    b = check(cfg, 'смесь')
    assert not b, (cfg, b)
print('смеси: ок')

# ---- места людей на 2-м уровне: днем у дома и на огороде (2), ночью у кровати (3)
used = set()
for v in list(DAY1.values()) + list(NIGHT1.values()): used |= set(v)
def pick(anchor, n, inside_ok, rad=6):
    got = []
    cand = sorted((t for t in ring(anchor, rad) if t not in blk_all and t not in used and not (ring(t, 1) & set(people(CFG2).values()))),
                  key=lambda t: (tdist(t, anchor), xy(t)))
    for t in cand:
        if any(t in ring(g, 1) for g in got): continue
        if t not in reach2 and not inside_ok: continue
        if t in reach2:
            r2 = flood(ENTRANCE, blocked(world(CFG2)) | {GRAVE} | used | set(got) | {t})
            if not all((ring(p, 1) - {p}) & r2 for p in people(CFG2).values()): continue
        got.append(t)
        if len(got) == n: break
    assert len(got) == n, (xy(anchor), got)
    used.update(got)
    return got
def _unused_tdist(a, b):
    for r in range(0, 12):
        if a in ring(b, r): return r
    return 99
DAY2, NIGHT2 = {}, {}
for s, u in ((1, 2), (2, 3)):            # огороды: место 1-2
    c = center(U[u]['lv'][2]); DAY2[s] = pick(T(round(c[0]), round(c[1])), 2, False)
for i in range(8):                       # дома 1-8: места построек 0-2 (основание) и 3-7
    objs = U[4 + i]['lv'][2]
    beds = [o[1] for o in objs if is_bed(o[0])]
    c = center(objs); mid = T(round(c[0]), round(c[1]))
    NIGHT2[i] = pick(beds[0] if beds else mid, 3, True)
    if i >= 3: DAY2[i] = pick(mid, 2, False)
    print('дом', i + 1, 'кроватей', len(beds), 'ночь', [xy(t) for t in NIGHT2[i]], 'день', [xy(t) for t in DAY2[i]] if i >= 3 else '')

# ---- водоносы (по одному у колодца: ходят от колодца к костру) и вечер в баре (3 места на уровень бара)
WELL_SPOT = {0: pick(9952, 1, False)[0], 1: pick(9944, 1, False)[0]}
BAR_SPOT = {}
for lv in LEVELS:
    # у столиков бара: клетка свободна при этом уровне бара (остальное — 2-й уровень), до нее можно дойти
    cfg = dict(CFG2); cfg[17] = lv
    wb = blocked(world(cfg)) | {GRAVE}
    rr = flood(ENTRANCE, wb | used)
    c = center(U[17]['lv'][lv]); a = T(round(c[0]), round(c[1]))
    got = []
    for t in sorted(ring(a, 9), key=lambda t: (tdist(t, a), xy(t))):
        if t in rr and t not in used and t not in got and not (ring(t, 1) & set(people(CFG2).values())):
            got.append(t)
            if len(got) == 3: break
    assert len(got) == 3, ('бар', lv, got)
    used.update(got); BAR_SPOT[lv] = got
print('водоносы', {k: xy(v) for k, v in WELL_SPOT.items()}, 'бар', {k: [xy(t) for t in v] for k, v in BAR_SPOT.items()})

# ---- брамины в загоне (2-й уровень фермы): клетки браминов из песочницы
BRAH2 = [o[1] for o in B('Ферма браминов', 2) if o[0] >> 24 == 1][:2]
assert len(BRAH2) == 2 and all(t not in blk_all for t in BRAH2), BRAH2

# ---- главный сундук уровня: куда переносить вещи из сундуков прежнего уровня
def is_cont(pid): return pid >> 24 == 0 and mapparse.subtype(pid) == 1
def iname(pid):
    import render
    try: return render.fidpath(struct.unpack_from('>i', mapparse.proto(pid), 8)[0]).split('\\')[-1].lower()
    except Exception: return ''
def main_cont(objs):
    cs = [o for o in objs if is_cont(o[0])]
    if not cs: return None
    pref = ('lkr', 'chest', 'locker', 'shlf', 'drssr', 'desk', 'frig')
    cs.sort(key=lambda o: min([i for i, p in enumerate(pref) if p in iname(o[0])] or [99]))
    return cs[0]

def calls(objs, ind='   '):
    out = []
    for pid, tile, rf, extra in objs:
        out.append(f'{ind}call lay_o({pid}, {tile}, {rf});')
        for fn, args in extra: out.append(f'{ind}call lay_{fn}({args});')
    return out

STEPS = []
o = ['// Уровни зданий поселения: переход здания на следующий уровень, места людей и старосты по уровням.',
     '// Файл создан tools/layout/levels_emit.py из scripts_src/test/f2mtblay.h, руками не править.',
     '// Подключать после f2mtlay.h, f2mspots.h и f2mbld.h.', '#ifndef F2MLVL_H', '#define F2MLVL_H', '',
     f'#define LVL_FIRE2      ({FIRE2})   // костер перед шатром старосты (центр 2)',
     f'#define LVL_TED2       ({TED2})   // место старосты у шатра',
     f'#define LVL_SAFE2      ({SAFE2})   // куда Хэнк убегает в бою, когда стоит шатер',
     f'#define LVL_BRAHMIN0   ({BRAH2[0]})   // брамины в загоне (ферма 2)',
     f'#define LVL_BRAHMIN1   ({BRAH2[1]})',
     '',
     'procedure lvl_step(variable u, variable lv);', 'procedure lvl_spot(variable slot, variable lv, variable k);',
     'procedure lvl_night(variable tent, variable lv, variable k);\nprocedure lvl_well(variable w);\nprocedure lvl_bar(variable lv, variable k);']
body = []
for u, d in U.items():
    for lv in LEVELS:
        if lv == 1 and (d.get('old1') or d.get('empty1')): continue
        old = d['lv'][lv - 1] if lv > 1 else []
        new = d['lv'][lv]
        nk = {(q[0], q[1]) for q in new}
        gone = [q for q in old if (q[0], q[1]) not in nk]
        nc = main_cont(new)
        oc = [q for q in gone if is_cont(q[0])]
        name = f'lvl_s{u}_{lv}'
        STEPS.append((u, lv, name)); o.append(f'procedure {name};')
        body += ['', f'// {d["name"]}: уровень {lv}. Ставим {len(new)}, убираем {len(gone)}' + (f', вещи из {len(oc)} сундуков в {iname(nc[0])}' if oc and nc else ''),
                 f'procedure {name} begin', '   variable nc := 0, oc;']
        first = lv == (2 if d.get('empty1') else 1)
        if d.get('ruin') is not None and first and not d.get('old1'): body.append(f'   call lay_ruin_clear({d["ruin"]});')
        body += calls(new)
        if oc and nc:
            body.append(f'   nc := tile_contains_pid_obj({nc[1]}, 0, {nc[0]});')
            for q in oc:
                body += [f'   oc := tile_contains_pid_obj({q[1]}, 0, {q[0]});', '   if (oc and nc) then move_obj_inven_to_obj(oc, nc);']
        for q in gone:
            if is_cont(q[0]) and not nc: continue          # некуда переложить: старый сундук остается
            body.append(f'   call lay_x({q[0]}, {q[1]});')
        body.append('end')
o += body
o += ['', '// Здание u переходит с уровня lv - 1 на уровень lv (только объекты на карте)', 'procedure lvl_step(variable u, variable lv) begin']
for i, (u, lv, name) in enumerate(STEPS):
    o.append(f'   {"if" if i == 0 else "else if"} (u == {u} and lv == {lv}) then call {name};')
o += ['end', '', '// Днем: место 1-2 огороды, 3-7 палатки прораба (k = 0, 1). На 1-м уровне — f2mspots.h',
      'procedure lvl_spot(variable slot, variable lv, variable k) begin', '   if (lv < 2) then return lay_spot(slot, k);']
for s, ts in sorted(DAY2.items()):
    o.append(f'   if (slot == {s}) then begin if (k == 0) then return {ts[0]}; return {ts[1]}; end')
o += ['   return 0;', 'end', '', '// Ночью: дом 0-7 (0-2 основание, 3-7 прораб), место у кровати k = 0-2',
      'procedure lvl_night(variable tent, variable lv, variable k) begin', '   if (lv < 2) then return lay_night(tent, k);']
for i, ts in sorted(NIGHT2.items()):
    o.append(f'   if (tent == {i}) then begin if (k == 0) then return {ts[0]}; if (k == 1) then return {ts[1]}; return {ts[2]}; end')
o += ['   return 0;', 'end', '', '// Водонос у колодца w (0 старый, 1 новый)', 'procedure lvl_well(variable w) begin',
      f'   if (w == 0) then return {WELL_SPOT[0]};', f'   return {WELL_SPOT[1]};', 'end', '',
      '// Вечером в баре: место k = 0-2 у бара уровня lv', 'procedure lvl_bar(variable lv, variable k) begin']
for lv in LEVELS:
    ts = BAR_SPOT[lv]
    o.append(f'   if (lv == {lv}) then begin if (k == 0) then return {ts[0]}; if (k == 1) then return {ts[1]}; return {ts[2]}; end')
o += ['   return 0;', 'end', '', '#endif', '']
open(os.path.join(ROOT, 'scripts_src/f2mlvl.h'), 'w', encoding='utf-8').write('\n'.join(o))
print('f2mlvl.h', len(o), 'строк, переходов', len(STEPS))

# места 1-го уровня (f2mspots.h) не должны оказаться под чужим зданием 2-го уровня или под новым зданием 1-го
own = {1: 2, 2: 3}
for s, ts in DAY1.items():
    me = own.get(s, 4 + s)
    for u, d in U.items():
        if u == me: continue
        for lv in LEVELS:
            if lv == 1 and d.get('old1'): continue
            assert not set(ts) & blocked(d['lv'][lv]), ('днем', s, d['name'], lv)
for i, ts in NIGHT1.items():
    for u, d in U.items():
        if u == 4 + i: continue
        for lv in LEVELS:
            if lv == 1 and d.get('old1'): continue
            assert not set(ts) & blocked(d['lv'][lv]), ('ночью', i, d['name'], lv)
print('места 1-го уровня свободны')

# ---- временный стол радиста (Егор 2026-10-09): маленький стол table1 с пультом comp5 снаружи, рядом с любым
# построенным зданием лагеря, не на людях. Для каждого здания — клетка стола (1-3 клетки от его стен на любом уровне)
# и место радиста рядом; клетки свободны при всех уровнях всех зданий и не отрезают людей от въезда.
# Пишет scripts_src/f2mradl.h: radio_spot(u) и radio_sam(u), 0 — места нет
RADIO_ORDER = [13, 12, 14, 15, 17, 18, 16, 19] + list(range(4, 12)) + [0, 1, 2, 3]
spots_all = set(used) | {t for v in DAY1.values() for t in v} | {t for v in NIGHT1.values() for t in v}
pp_all = set(people(CFG1).values()) | set(people(CFG2).values()) | spots_all
pp_all |= {T(149, 34)}   # лопата у северного частокола (CAMP_SHOVEL)
b1 = blocked(world(CFG1)) | {GRAVE}; b2 = blocked(world(CFG2)) | {GRAVE}
RSPOT = {}
for u in RADIO_ORDER:
    walls = set()
    for lv in LEVELS: walls |= blocked(U[u]['lv'][lv])
    if not walls: continue
    cand, seen_l, layer = [], set(walls), set(walls)
    for _k in range(3):   # слои 1, 2, 3 клетки от стен здания
        layer = {tdir(t, r, 1) for t in layer for r in range(6)} - seen_l
        seen_l |= layer; cand += sorted(layer, key=xy)
    for t in cand:
        if t in blk_all or ring(t, 1) & pp_all or t not in reach1 or t not in reach2: continue
        sam = [n for n in sorted(ring(t, 1) - {t}) if n not in blk_all and n in reach1 and n in reach2 and not ring(n, 1) & (pp_all - {n})]
        if not sam: continue
        r1 = flood(ENTRANCE, b1 | {t}); r2 = flood(ENTRANCE, b2 | {t})
        if all((ring(q, 1) - {q}) & r1 for q in people(CFG1).values()) and all((ring(q, 1) - {q}) & r2 for q in people(CFG2).values()) \
           and all(s in r1 and s in r2 for s in spots_all if s in reach1 and s in reach2) and sam[0] in r1 and sam[0] in r2:
            RSPOT[u] = (t, sam[0]); break
print('стол радиста:', {U[u]['name']: xy(v[0]) for u, v in RSPOT.items()})
assert 13 in RSPOT
o = ['// Сгенерировано tools/layout/levels_emit.py: временный стол радиста (table1 + comp5) у построенных зданий лагеря.',
     '// Не править руками. Порядок выбора здания — RADIO_ORDER в levels_emit.py (центр, склад, мастерская...).',
     '#ifndef F2MRADL_H', '#define F2MRADL_H',
     f'#define RADIO_ORDER_N  ({len(RADIO_ORDER)})',
     'procedure radio_unit(variable i) begin']
for i, u in enumerate(RADIO_ORDER): o.append(f'   {"if" if i == 0 else "else if"} (i == {i}) then return {u};')
o += ['   return -1;', 'end', 'procedure radio_spot(variable u) begin']
for u, (t, s) in RSPOT.items(): o.append(f'   if (u == {u}) then return {t};   // {xy(t)[0]}, {xy(t)[1]}: {U[u]["name"]}')
o += ['   return 0;', 'end', 'procedure radio_sam(variable u) begin']
for u, (t, s) in RSPOT.items(): o.append(f'   if (u == {u}) then return {s};')
o += ['   return 0;', 'end', '#endif', '']
open(os.path.join(ROOT, 'scripts_src/f2mradl.h'), 'w', encoding='utf-8').write('\n'.join(o))
