import sys; sys.path.insert(0, __import__('os').path.dirname(__file__) or '.')
from mapparse import parse
m = parse('desert7.map')
def rel(anchor):
    ax, ay = anchor % 200, anchor // 200
    s = set()
    for o in m['objs']:
        if o['elev']: continue
        x, y = o['tile'] % 200, o['tile'] // 200
        if abs(x-ax) <= 7 and abs(y-ay) <= 6:
            p = o['pid']
            if (p >> 24) == 3 or 0x2000180 <= p <= 0x2000185:
                s.add((x-ax, y-ay, p))
    return s
a, b = rel(17505), rel(21121)
TENT = sorted(a & b)
if __name__ == '__main__':
    print(len(a), len(b), len(TENT)); print(sorted(a ^ b))
    for t in TENT: print(t)
