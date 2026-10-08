# Общее для уровней зданий поселения: разбор песочницы (f2mtblay.h) по зданиям лагеря.
# UNITS: имя, список объектов по уровням {1: [...], 2: [...], ...}; объект = [pid, tile, rf, [(fn, args)]]
import os, re, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapparse
from hexlib import tdir
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
HIDDEN, NOBLOCK, MULTIHEX = 0x1, 0x10, 0x800

SRC = open(os.path.join(ROOT, 'scripts_src/test/f2mtblay.h'), encoding='utf-8').read().split('\n')
names, LV, SYS = {}, {}, {}
cur = level = sysk = None; pending = None
for line in SRC:
    m = re.match(r'// (.+): объектов по уровням', line)
    if m: pending = m.group(1)
    m = re.match(r'procedure tb_b(\d+)\(variable lv\) begin', line)
    if m: cur = int(m.group(1)); names[cur] = pending; LV[cur] = {1: [], 2: [], 3: [], 4: []}; level = None; continue
    m = re.match(r'\s+(?:end else )?if \(lv == (\d)\) then begin', line)
    if m and cur is not None: level = int(m.group(1)); continue
    m = re.match(r'\s+(?:end else )?if \(s == (\d+)\) then begin', line)
    if m: sysk = int(m.group(1)); SYS[sysk] = []; cur = None; continue
    if line.startswith('end') or line.startswith('procedure tb_bld') or line.startswith('procedure tb_turrets'):
        cur = None; sysk = None
    m = re.match(r'\s+call tb_o\((\d+), (\d+), (\d+)\);', line)
    tgt = LV[cur][level] if cur is not None and level else SYS[sysk] if sysk is not None else None
    if m and tgt is not None: tgt.append([int(m.group(1)), int(m.group(2)), int(m.group(3)), []]); continue
    m = re.match(r'\s+call (tb_flg|tb_lit)\((.+)\);', line)
    if m and tgt is not None and tgt: tgt[-1][3].append((m.group(1)[3:], m.group(2)))
byname = {v: k for k, v in names.items()}
def B(prefix, lv=1): return LV[[k for n, k in byname.items() if n.startswith(prefix)][0]][lv]

def xy(t): return t % 200, t // 200
def T(x, y): return y * 200 + x
def center(objs):
    xs = [xy(o[1])[0] for o in objs]; ys = [xy(o[1])[1] for o in objs]
    return sum(xs) / len(xs), sum(ys) / len(ys)
def ring(t, n):
    s = {t}
    for _ in range(n): s |= {tdir(u, r, 1) for u in s for r in range(6)}
    return s
PI = {}
def pflags(pid):
    if pid not in PI: PI[pid] = struct.unpack_from('>I', mapparse.proto(pid), 20)[0]
    return PI[pid]
def oflags(o):
    f = pflags(o[0])
    for fn, a in o[3]:
        if fn == 'flg': fs, fc = map(int, a.split(',')); f = (f | fs) & ~fc
    return f
def blocked(objs):
    out = set()
    for o in objs:
        if o[0] >> 24 not in (1, 2, 3): continue
        f = oflags(o)
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
def clusters(objs, n):
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
