import sys, struct; sys.path.insert(0, __import__('os').path.dirname(__file__) or '.')
from gen import *
from mapparse import proto
from hexlib import tdir
b = tdir(S,1,10); w = tdir(b,1,12)
wag = [(tdir(w,0,6), 33554959), (tdir(w,1,7), 33554960), (tdir(w,2,6), 33554959)]
def go(objs, out):
    extra = [dict(tile=t, pid=p, fid=struct.unpack_from('>i', proto(p), 8)[0]) for t,p in objs]
    im_m = render('/home/claude/f2-rpu-mod/base/rpu-2.4.34/maps/desert1.map', out, at(-80, -40), rad_px=(1150, 640), extra=extra, marks=[])
base = [(t,p) for v in L.values() for t,p in v] + wag
go(base, 'camp_start.png')
go(base + [(t,p) for v in DONE.values() for t,p in v], 'camp_full.png')
from PIL import Image
for n in ('camp_start', 'camp_full'):
    Image.open(n + '.png').convert('RGB').save(f'/mnt/project-files/f2mod/m3/{n}.jpg', quality=85)
