# Пишет расстановку тестовой стройки для скриптов (scripts_src/test/f2mtblay.h) и пустую карту песочницы
# с полом города (mod/test/maps/f2mtown.map). Вход: town_build.pkl (town_build.py).
# Использование: town_emit.py [папка с town_build.pkl]
import sys, os, pickle, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mapparse
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
SRC = sys.argv[1] if len(sys.argv) > 1 else '/tmp/claude-0/tb/'
D = pickle.load(open(SRC + 'town_build.pkl', 'rb'))
def T(u, y): return y * 200 + (199 - u)

def calls(objs, ind='   '):
    out = []
    for e in objs:
        out.append(f'{ind}call tb_o({e["pid"]}, {e["tile"]}, {e["rot"] + 8 * e["frame"]});')
        if e['fset'] or e['fclr']: out.append(f'{ind}call tb_flg({e["fset"]}, {e["fclr"]});')
        if e['light']: out.append(f'{ind}call tb_lit({e["light"][0]}, {e["light"][1]});')
    return out

o = ['// Тестовая стройка города (песочница): расстановка всех уровней зданий, деревьев, мусора, света, забора, турелей.',
     '// Файл создан tools/layout/town_emit.py из town_build.py, руками не править. Только для f2mod_test.dat.',
     '#ifndef F2MTBLAY_H', '#define F2MTBLAY_H', '',
     f'#define TB_COUNT       ({len(D["NAMES"])})    // зданий в списке (жилье — все 8 домов сразу, огороды — оба)',
     '#define TB_SYS_TREES   (0)', '#define TB_SYS_TRASH   (1)', '#define TB_SYS_BARRELS (2)', '#define TB_SYS_LAMPS   (3)',
     '#define TB_SYS_PALISADE (4)', '#define TB_SYS_MESH    (5)', '#define TB_SYS_WALL    (6)', '#define TB_SYS_OUTER   (7)',
     f'#define TB_CAR_HEX     ({T(*D["CAR"])})', '',
     'variable tb_mode;   // 1 ставим, 0 убираем', 'variable tb_last;   // последний поставленный объект', '',
     'procedure tb_o(variable pid, variable tile, variable rf);', 'procedure tb_flg(variable fset, variable fclr);',
     'procedure tb_lit(variable dist, variable pct);', 'procedure tb_bld(variable b, variable lv);', 'procedure tb_sys(variable s);',
     'procedure tb_turrets(variable kind);', 'procedure tb_t(variable tile, variable kind);']
for i in range(len(D['NAMES'])): o.append(f'procedure tb_b{i}(variable lv);')
o += ['',
      '// Ставит объект (tb_mode = 1) или убирает такой же с этой клетки (tb_mode = 0). rf: поворот + 8 * кадр',
      'procedure tb_o(variable pid, variable tile, variable rf) begin',
      '   variable obj;',
      '   if (tb_mode) then begin',
      '      obj := create_object(pid, tile, 0);',
      '      if (rf bwand 7) then anim(obj, 1000, rf bwand 7);',
      '      if (rf / 8) then anim(obj, 1010, rf / 8);',
      '      tb_last := obj;',
      '   end else begin',
      '      obj := tile_contains_pid_obj(tile, 0, pid);',
      '      if (obj) then destroy_object(obj);',
      '      tb_last := 0;',
      '   end',
      'end', '',
      '// Флаги объекта, как на карте-образце (без блока, прозрачность и т. п.)',
      'procedure tb_flg(variable fset, variable fclr) begin',
      '   if (tb_last) then set_flags(tb_last, (get_flags(tb_last) bwor fset) bwand bwnot(fclr));',
      'end', '',
      '// Свет объекта, как на карте-образце (у фонарей в прототипе света нет)',
      'procedure tb_lit(variable dist, variable pct) begin',
      '   if (tb_last) then obj_set_light_level(tb_last, pct, dist);',
      'end', '']
for i, (name, L) in enumerate(zip(D['NAMES'], D['LEVELS'])):
    o.append(f'// {name}: объектов по уровням ' + ', '.join(str(len(x)) for x in L))
    o.append(f'procedure tb_b{i}(variable lv) begin')
    for lv in range(4):
        o.append(f'   {"if" if lv == 0 else "end else if"} (lv == {lv + 1}) then begin')
        o += calls(L[lv], '      ')
    o += ['   end', 'end', '']
o += ['procedure tb_bld(variable b, variable lv) begin']
for i in range(len(D['NAMES'])): o.append(f'   {"if" if i == 0 else "else if"} (b == {i}) then call tb_b{i}(lv);')
o += ['end', '']
SYS = ['trees', 'trash', 'barrels', 'lamps', 'palisade', 'mesh', 'wall', 'outer']
o += ['procedure tb_sys(variable s) begin']
for i, k in enumerate(SYS):
    o.append(f'   {"if" if i == 0 else "end else if"} (s == {i}) then begin   // {k}: {len(D["SYS"][k])}')
    o += calls(D['SYS'][k], '      ')
o += ['   end', 'end', '']
o += ['// Турели на кольце между стеной и внешней сеткой', 'procedure tb_turrets(variable kind) begin']
for x, y in D['TUR']: o.append(f'   call tb_t({y * 200 + x}, kind);')
o += ['end', '', '#endif', '']
open(os.path.join(ROOT, 'scripts_src/test/f2mtblay.h'), 'w', encoding='utf-8').write('\n'.join(o))
print('f2mtblay.h', len(o), 'lines')

# ---- карта: заголовок desert1, пол города, без объектов и скриптов
src = open(os.path.join(ROOT, 'base/rpu-2.4.34/maps/desert1.map'), 'rb').read()
base = mapparse.parse(os.path.join(ROOT, 'base/rpu-2.4.34/maps/desert1.map'))
h = bytearray(src[:0xEC])
h[4:20] = b'F2MTOWN.MAP'.ljust(16, b'\0')
M1 = D['M'][1]; GX0 = D['GX0']
struct.pack_into('>iiiii', h, 20, (M1 + 3) * 200 + GX0 + 4, 0, 0, 0, 0)   # вход снаружи у ворот, переменных карты нет, скрипт ставит сборка
flags = struct.unpack_from('>i', h, 40)[0]
struct.pack_into('>i', h, 48, 0)
body = bytearray(h)
for e in range(3):
    if not flags & (2 << e):
        t = D['TILES'] if e == 0 else base['tiles'][e]
        body += struct.pack('>10000i', *t)
body += struct.pack('>5i', 0, 0, 0, 0, 0)        # скриптов на карте нет
body += struct.pack('>4i', 0, 0, 0, 0)           # объектов нет: все ставит скрипт
os.makedirs(os.path.join(ROOT, 'mod/test/maps'), exist_ok=True)
open(os.path.join(ROOT, 'mod/test/maps/f2mtown.map'), 'wb').write(body)
print('f2mtown.map', len(body), 'flags', flags)
