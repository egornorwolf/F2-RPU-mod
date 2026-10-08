# Места жителей у построек (Егор 2026-10-08: есть палатки или работа — жители расходятся по домам и на огороды,
# а не стоят у костра). Для каждого места 1-7 (огороды 1-2, палатки 4-8) — две свободные клетки у постройки,
# достижимые от въезда при всех стройках, частоколе и могиле. Пишет scripts_src/f2mspots.h. Запуск: spots_emit.py
import os, re, sys
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fence_emit.py'), encoding='utf-8').read()
exec(src.split('# палатки прораба')[0])
GRAVE = 31760
by = {}
cur = None; on = False
for line in open(LAY, encoding='utf-8'):
    if re.match(r'^procedure lay_slot\(.*begin', line): on = True; continue
    if on and line.startswith('end'): break
    m = re.search(r'if \(slot == (\d+)\) then begin', line)
    if on and m: cur = int(m.group(1)); continue
    m = re.match(r'\s+call lay_o\((\d+), (\d+), (\d+)\);', line)
    if on and m and cur is not None: by.setdefault(cur, []).append(int(m.group(2)))
blk = blocked(CAMP + LIGHTS + RUINS + SLOTS + PAL) | {GRAVE}
reach = flood(ENTRANCE, blk)
people = {defs[k] for k in ('TED', 'FOREMAN', 'CHIEF', 'FIRE')}
used = set()
SP = {}
for s in range(1, 8):
    ts = by[s]; cx = sum(xy(t)[0] for t in ts) / len(ts); cy = sum(xy(t)[1] for t in ts) / len(ts)
    cand = sorted((t for t in reach if t not in used and not (ring(t, 1) & people)),
                  key=lambda t: (xy(t)[0] - cx) ** 2 + (xy(t)[1] - cy) ** 2)
    got = []
    for t in cand:
        if any(t in ring(u, 1) for u in got + list(used)): continue
        # клетку человека закрываем: проход ко всем местам людей остается
        r2 = flood(ENTRANCE, blk | {t} | used | set(got))
        if all(ring(p, 1) & r2 for p in PTS.values()):
            got.append(t)
        if len(got) == 2: break
    assert len(got) == 2, s
    used |= set(got); SP[s] = got
    print('место', s, [xy(t) for t in got], 'центр', round(cx), round(cy))
o = ['// Места жителей у построек: огороды 1-2 (работа), палатки 4-8 (дом). Создан tools/layout/spots_emit.py, руками не править.',
     '#ifndef F2MSPOTS_H', '#define F2MSPOTS_H', '', 'procedure lay_spot(variable slot, variable k);', '',
     'procedure lay_spot(variable slot, variable k) begin']
for s, (a, b) in SP.items():
    o.append(f'   if (slot == {s}) then begin if (k == 0) then return {a}; return {b}; end')
o += ['   return 0;', 'end', '', '#endif', '']
open(os.path.join(ROOT, 'scripts_src/f2mspots.h'), 'w', encoding='utf-8').write('\n'.join(o))
