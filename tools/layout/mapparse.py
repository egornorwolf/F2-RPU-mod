import struct, sys, zlib
sys.path.insert(0, '/home/claude/f2-rpu-mod/tools')
import dat2
DAT = '/mnt/project-files/f2mod/game-data/master.dat'
tree = {n.lower(): (c, s, o) for n, c, _, s, o in dat2.read_tree(DAT)}
import os
_idx = {}
for root, ds, fs in os.walk('/home/claude/rpu/data'):
    for f in fs:
        full = os.path.join(root, f)
        _idx[os.path.relpath(full, '/home/claude/rpu/data').replace('/', '\\').lower()] = full
def dat(name):
    if name.lower() in _idx: return open(_idx[name.lower()], 'rb').read()
    return dat0(name)
def dat0(name):
    c, s, o = tree[name.lower()]
    with open(DAT, 'rb') as f:
        f.seek(o); d = f.read(s)
    return zlib.decompress(d) if c else d
lists = {}
import os
RPU = '/home/claude/rpu/data/proto'
def rd(rel):
    p = os.path.join(RPU, *rel.split('\\')[1:])
    if os.path.exists(p): return open(p, 'rb').read()
    for f in os.listdir(os.path.dirname(p)) if os.path.isdir(os.path.dirname(p)) else []:
        if f.lower() == os.path.basename(p).lower(): return open(os.path.join(os.path.dirname(p), f), 'rb').read()
    return dat(rel)
def lst(kind):
    if kind not in lists:
        lists[kind] = rd(f'proto\\{kind}\\{kind}.lst').decode('cp1251').split('\n')
    return lists[kind]
KIND = {0: 'items', 1: 'critters', 2: 'scenery', 3: 'walls', 4: 'tiles', 5: 'misc'}
pcache = {}
def proto(pid):
    if pid not in pcache:
        k = KIND[pid >> 24]; name = lst(k)[(pid & 0xffffff) - 1].strip()
        pcache[pid] = rd(f'proto\\{k}\\{name}')
    return pcache[pid]
def subtype(pid):
    return struct.unpack_from('>i', proto(pid), 32)[0]
class R:
    def __init__(s, b, o=0): s.b, s.o = b, o
    def i(s, n=1):
        if n == 0: return ()
        v = struct.unpack_from(f'>{n}i', s.b, s.o); s.o += 4 * n
        return v if n > 1 else v[0]
def read_obj(r, out, depth=0):
    f = r.i(18)
    o = dict(tile=f[1], fid=f[8], flags=f[9], elev=f[10], pid=f[11], sid=f[16], frame=f[6], rot=f[7], ld=f[13], li=f[14])
    inv_len = r.i(); r.i(2)
    t = o['pid'] >> 24
    if t == 1:
        r.i(11)
    else:
        r.i()
        if t == 0:
            st = subtype(o['pid'])
            r.i({3: 2, 4: 1, 5: 1, 6: 1}.get(st, 0))
        elif t == 2:
            st = subtype(o['pid'])
            r.i({0: 1, 1: 2, 2: 2, 3: 2, 4: 2}.get(st, 0))
        elif t == 5 and 0x5000010 <= o['pid'] <= 0x5000017:
            r.i(4)
    if depth == 0: out.append(o)
    for _ in range(inv_len):
        r.i(); read_obj(r, out, depth + 1)
def parse(path):
    b = open(path, 'rb').read(); r = R(b)
    h = r.i(); r.o = 4 + 16
    ent, el, rot, nlv, scr, flags, dark, ngv = r.i(8)
    r.o = 0xEC
    r.i(ngv) if ngv else None; r.i(nlv) if nlv else None
    tiles = {}
    for e in range(3):
        if not flags & (2 << e):
            tiles[e] = r.i(10000)
    for t in range(5):
        n = r.i()
        if n:
            ext = (n + 15) // 16
            for _ in range(ext):
                for _ in range(16):
                    sid = r.i(); r.i()
                    st = (sid >> 24) & 0xff
                    if st == 1: r.i(2)
                    elif st == 2: r.i(1)
                    r.i(14)
                r.i(2)
    total = r.i(); objs = []
    for e in range(3):
        n = r.i()
        for _ in range(n): read_obj(r, objs)
    assert len(objs) == total, (len(objs), total)
    return dict(enter=ent, flags=flags, objs=objs, tiles=tiles, rest=len(b) - r.o)
if __name__ == '__main__':
    m = parse(sys.argv[1])
    print('enter', m['enter'], 'objs', len(m['objs']), 'rest', m['rest'])
    from collections import Counter
    c = Counter((o['pid'], o['elev']) for o in m['objs'])
    for (pid, e), n in sorted(c.items()): print(hex(pid), e, n)
