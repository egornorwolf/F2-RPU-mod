# Частокол вокруг лагеря у скал (набег 1.3, Егор 2026-10-08: забор у Хэнка до первого набега).
# Берет деревянный частокол песочницы (scripts_src/test/f2mtblay.h, tb_sys 4: колья fen*, концы и углы из карт F2,
# блоки block.frm) и пишет scripts_src/f2mfence.h (lay_fence, lay_fence_x). Проверяет по прототипам:
#   - колья не стоят на клетках, занятых непроходимыми объектами лагеря (основание, стройки прораба, развалины, бочки);
#   - проходимость: от въезда на карту через ворота частокола до мест людей, а снаружи внутрь только через ворота.
# f2mtlay.h не трогает. Использование: fence_emit.py
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapparse
from hexlib import tdir
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
HIDDEN, NOBLOCK, MULTIHEX = 0x1, 0x10, 0x800

def read_calls(path, start_re, stop_re, fn):
    out, on = [], False
    for line in open(path, encoding='utf-8'):
        if re.search(start_re, line): on = True; continue
        if on and re.search(stop_re, line): break
        if not on: continue
        m = re.match(rf'\s+call {fn}_o\((\d+), (\d+), (\d+)\);', line)
        if m: out.append([int(m.group(1)), int(m.group(2)), int(m.group(3)), []]); continue
        m = re.match(rf'\s+call {fn}_(flg|lit)\((.+)\);', line)
        if m and out: out[-1][3].append((m.group(1), m.group(2)))
    return out

PAL = read_calls(os.path.join(ROOT, 'scripts_src/test/f2mtblay.h'), r'if \(s == 4\) then begin', r'if \(s == 5\) then begin', 'tb')
LAY = os.path.join(ROOT, 'scripts_src/f2mtlay.h')
CAMP = read_calls(LAY, r'^procedure lay_camp begin', r'^end', 'lay')
SLOTS = read_calls(LAY, r'^procedure lay_slot\(.*begin', r'^end', 'lay')
LIGHTS = read_calls(LAY, r'^procedure lay_lights begin', r'^end', 'lay')
RUINS = read_calls(LAY, r'^procedure lay_ruins begin', r'^end', 'lay')
defs = {m.group(1): int(m.group(2)) for m in re.finditer(r'#define LAY_(\w+)\s+\((\d+)\)', open(LAY, encoding='utf-8').read())}
print('частокол', len(PAL), 'основание', len(CAMP), 'стройки', len(SLOTS), 'развалины', len(RUINS))

def xy(t): return t % 200, t // 200
def T(x, y): return y * 200 + x
PI = {}
def flags(o):
    if o[0] not in PI:
        import struct
        PI[o[0]] = struct.unpack_from('>I', mapparse.proto(o[0]), 20)[0]
    f = PI[o[0]]
    for fn, a in o[3]:
        if fn == 'flg': fs, fc = map(int, a.split(',')); f = (f | fs) & ~fc
    return f
def ring(t, n):
    s = {t}
    for _ in range(n): s |= {tdir(u, r, 1) for u in s for r in range(6)}
    return s
def blocked(objs):
    out = set()
    for o in objs:
        if o[0] >> 24 not in (1, 2, 3): continue
        f = flags(o)
        if f & (HIDDEN | NOBLOCK): continue
        out |= ring(o[1], 1) if f & MULTIHEX else {o[1]}
    return out
def flood(start, blk, lo=5, hi=194):
    seen = {start}; q = [start]
    while q:
        t = q.pop()
        for r in range(6):
            n = tdir(t, r, 1); x, y = xy(n)
            if n not in seen and n not in blk and lo <= x <= hi and lo <= y <= hi: seen.add(n); q.append(n)
    return seen

# 1. колья не на занятых клетках
others = CAMP + SLOTS + LIGHTS + RUINS
ob = blocked(others); pb = blocked(PAL)
clash = sorted(pb & ob)
print('частокол на занятых клетках:', [xy(t) for t in clash] or 'нет')
assert not clash

# 2. проходимость. Рамка частокола и ворота (проемы в рамке)
xs = [xy(o[1])[0] for o in PAL]; ys = [xy(o[1])[1] for o in PAL]
x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
print('рамка частокола x', x0, x1, 'y', y0, y1)
ENTRANCE = 35301                       # въезд на карту (как в settle_emit.py), снаружи у южного края
PTS = {k: defs[k] for k in ('TED', 'FOREMAN', 'CHIEF', 'WAGONS', 'CAR', 'FIRE')}
for tag, objs in (('основание + развалины + частокол', CAMP + LIGHTS + RUINS + PAL),
                  ('+ все стройки прораба', CAMP + LIGHTS + RUINS + SLOTS + PAL)):
    blk = blocked(objs); reach = flood(ENTRANCE, blk)
    bad = [k for k, t in PTS.items() if not ring(t, 1) & reach]
    print('проходимость', tag + ':', bad or 'ок')
    assert not bad, bad
# снаружи внутрь только через ворота: ищем проемы в северной и южной стенах (просвет между кольями шире клетки),
# закрываем их и проверяем, что снаружи до мест людей не дойти
blk = blocked(CAMP + LIGHTS + RUINS + PAL)
GATES = []
for ya, yb in ((y0, y0 + 4), (y1 - 4, y1)):
    row = sorted({xy(o[1])[0] for o in PAL if ya <= xy(o[1])[1] <= yb})
    GATES += [(a + 1, b - 1, ya, yb) for a, b in zip(row, row[1:]) if b - a > 1]
print('ворота (x от, x до, ряды):', GATES)
assert len(GATES) == 2, GATES
wall = {T(x, y) for a, b, ya, yb in GATES for x in range(a, b + 1) for y in range(ya, yb + 1)}
sealed = flood(T(10, 10), blk | wall, 5, 194)
leak = [k for k, t in PTS.items() if ring(t, 1) & sealed]
print('без ворот снаружи до людей не дойти:', 'ок' if not leak else leak)
assert not leak, leak
assert ring(ENTRANCE, 0) & flood(T(10, 10), blk)

# палатки прораба по местам 3-7 (для сноса после набега)
TENTS, cur = {}, None
on = False
for line in open(LAY, encoding='utf-8'):
    if re.match(r'^procedure lay_slot\(.*begin', line): on = True; continue
    if on and line.startswith('end'): break
    m = re.search(r'if \(slot == (\d+)\) then begin', line)
    if on and m: cur = int(m.group(1)); continue
    m = re.match(r'\s+call lay_o\((\d+), (\d+), (\d+)\);', line)
    if on and m and cur is not None and 3 <= cur <= 7: TENTS.setdefault(cur, []).append([int(m.group(1)), int(m.group(2)), int(m.group(3)), []])
print('палатки прораба:', {k: len(v) for k, v in TENTS.items()})
assert sorted(TENTS) == [3, 4, 5, 6, 7]

def calls(objs, fn='lay_o', ind='   '):
    out = []
    for pid, tile, rf, extra in objs:
        out.append(f'{ind}call {fn}({pid}, {tile}, {rf});')
        for f, a in extra: out.append(f'{ind}call lay_{f}({a});')
    return out
o = ['// Деревянный частокол вокруг лагеря у скал (набег 1.3): колья, концы и углы из карт F2 с блоками block.frm.',
     '// Файл создан tools/layout/fence_emit.py из частокола песочницы (scripts_src/test/f2mtblay.h), руками не править.',
     '// Подключать после f2mtlay.h (lay_o, lay_flg, lay_x).', '#ifndef F2MFENCE_H', '#define F2MFENCE_H', '',
     'procedure lay_fence;', 'procedure lay_slot_clear(variable slot);', '', f'// Частокол: {len(PAL)} объектов, ворота — проемы в южной и северной стенах',
     'procedure lay_fence begin']
o += calls(PAL)
o += ['end', '', '// Набег разрушил палатку прораба (места 3-7): убрать ее объекты', 'procedure lay_slot_clear(variable slot) begin']
for i, (slot, objs) in enumerate(sorted(TENTS.items())):
    o.append(f'   {"if" if i == 0 else "end else if"} (slot == {slot}) then begin   // палатка {slot + 1}: {len(objs)}')
    o += [f'      call lay_x({pid}, {tile});' for pid, tile, rf, extra in objs]
o += ['   end', 'end', '', '#endif', '']
open(os.path.join(ROOT, 'scripts_src/f2mfence.h'), 'w', encoding='utf-8').write('\n'.join(o))
print('f2mfence.h', len(o), 'строк')
