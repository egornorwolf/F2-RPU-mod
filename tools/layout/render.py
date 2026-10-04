import struct, sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from mapparse import parse, dat, rd, tree
from PIL import Image, ImageDraw
pal = dat('color.pal')[:768]
P = [(min(255, pal[i*3]*4), min(255, pal[i*3+1]*4), min(255, pal[i*3+2]*4)) for i in range(256)]
artl = {}
def artlist(k):
    if k not in artl:
        artl[k] = dat(f'art\\{k}\\{k}.lst').decode('cp1251').split('\n')
    return artl[k]
fc = {}
def frm(path, rot=0):
    key = (path, rot)
    if key in fc: return fc[key]
    try: d = dat(path)
    except KeyError: fc[key] = None; return None
    xo = struct.unpack('>6h', d[0x0a:0x16]); yo = struct.unpack('>6h', d[0x16:0x22])
    offs = struct.unpack('>6I', d[0x22:0x3a]); r = rot if offs[rot] or rot == 0 else 0
    p = 0x3e + offs[r]
    w, h, size, fx, fy = struct.unpack('>HHIhh', d[p:p+12]); px = d[p+12:p+12+w*h]
    im = Image.new('RGBA', (w, h)); im.putdata([(0,0,0,0) if c == 0 else P[c]+(255,) for c in px])
    fc[key] = (im, xo[r] + fx, yo[r] + fy); return fc[key]
TK = {0:'items',1:'critters',2:'scenery',3:'walls',4:'tiles',5:'misc',6:'intrface',7:'inven',8:'heads',9:'backgrnd',10:'skilldex'}
def fidpath(fid):
    t = (fid >> 24) & 0xf; n = artlist(TK[t])[fid & 0xfff].strip().split()[0] if t != 1 else None
    return f'art\\{TK[t]}\\{n}' if n else None
def hexxy(tile):
    v3 = 199 - tile % 200; y = tile // 200
    x = 48 * (v3 // 2); sy = 12 * (-(v3 // 2))
    if v3 & 1: x += 32
    return x + 16 * y, sy + 12 * y
def sqxy(s):
    v5 = 99 - s % 100; v6 = s // 100
    return -16 + 48 * v5 + 32 * v6, -2 - 12 * v5 + 24 * v6
def render(mapfile, out, center, rad_px=(900, 650), extra=(), marks=()):
    m = parse(mapfile)
    cx, cy = hexxy(center); x0, y0 = cx - rad_px[0], cy - rad_px[1]
    im = Image.new('RGB', (2*rad_px[0], 2*rad_px[1]), (0,0,0))
    tl = rd('art\\tiles\\tiles.lst') if False else None
    tiles_lst = dat('art\\tiles\\tiles.lst').decode('cp1251').split('\n')
    fl = m['tiles'][0]
    for s in range(10000):
        f = fl[s] & 0xffff
        if f in (0, 1): continue
        x, y = sqxy(s); x -= x0; y -= y0
        if -100 < x < im.width + 20 and -50 < y < im.height + 20:
            r = frm('art\\tiles\\' + tiles_lst[f].strip())
            if r: im.paste(r[0], (x, y), r[0])
    objs = [o for o in m['objs'] if o['elev'] == 0] + list(extra)
    def key(o): 
        x, y = hexxy(o['tile']); return (o.get('flat', 0) == 0, y, -x)
    dr = ImageDraw.Draw(im)
    for o in sorted(objs, key=key):
        t = o['pid'] >> 24
        if t == 5: continue
        p = o.get('path') or fidpath(o['fid'])
        if not p: continue
        r = frm(p, o.get('rot', 0))
        if not r: continue
        a, ox, oy = r
        x, y = hexxy(o['tile']); x += 16 + ox - x0; y += 8 + oy - y0
        im.paste(a, (x - a.width // 2, y - a.height + 1), a)
    for t, lbl, col in marks:
        x, y = hexxy(t); x += 16 - x0; y += 8 - y0
        dr.ellipse((x-4, y-3, x+4, y+3), outline=col); dr.text((x+5, y-6), lbl, fill=col)
    im.save(out)
    return m
if __name__ == '__main__':
    m = render('/home/claude/f2-rpu-mod/base/rpu-2.4.34/maps/desert1.map', 'd1.png', 20100,
               marks=[(20100, 'START', (255,255,0)), (19096, 'CAR', (0,255,255))])
