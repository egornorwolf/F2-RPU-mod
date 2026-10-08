# Рисует лагерь с выбранными объектами (картинка для проверки без игры)
import struct, render, mapparse
from levels_lib import *
from PIL import Image
MAP = os.path.join(ROOT, 'mod/data/maps/f2mset.map')
def draw(objs, out, center_t=T(100, 100), rad=(2600, 1500), marks=(), thumb=2600):
    ex = []
    for o in objs:
        fid = struct.unpack_from('>i', mapparse.proto(o[0]), 8)[0]
        ex.append(dict(tile=o[1], pid=o[0], fid=fid, elev=0, rot=o[2] & 7))
    real = render.parse
    def p(f):
        m = real(f); m['objs'] = [e for e in m['objs'] if e['pid'] >> 24 != 5]; return m
    render.parse = p
    render.render(MAP, out, center_t, rad_px=rad, extra=ex, marks=marks)
    render.parse = real
    im = Image.open(out); im.thumbnail((thumb, thumb)); im.convert('RGB').save(out.rsplit('.', 1)[0] + '.jpg', quality=85)
