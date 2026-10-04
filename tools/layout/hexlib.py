from render import hexxy
DT = [[-1, 199, 200, 201, 1, -200], [-201, -1, 200, 1, -199, -200]]
def tdir(t, r, n):
    if n < 0: r, n = (r + 3) % 6, -n
    for _ in range(n): t += DT[(t % 200) & 1][r]
    return t
def nearest(px, py, parity=None):
    best = None
    for t in range(40000):
        if parity is not None and (t % 200) % 2 != parity: continue
        x, y = hexxy(t); d = (x - px) ** 2 + (y - py) ** 2
        if best is None or d < best[0]: best = (d, t)
    return best[1]
