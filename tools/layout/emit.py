import sys; sys.path.insert(0, __import__('os').path.dirname(__file__) or '.')
from gen import *
SLOTS = ['newwell', 'garden0', 'garden1', 'slot0', 'slot1', 'slot2', 'slot3']
o = ['// Расстановка лагеря у скал. Файл создан tools/layout/emit.py, руками не править.',
     '// Палатки собраны из тех же стен и шестов, что палатки торговцев в пустынных встречах (desert7).',
     '#ifndef F2MLAY_H', '#define F2MLAY_H', '']
for k, t in P.items(): o.append(f'#define LAY_{k.upper():<10} ({t})')
o += ['', '#define LAY_SLOTS      (7)    // 0 колодец, 1-2 огороды, 3-6 палатки', '',
      'procedure lay_obj(variable pid, variable tile);', 'procedure lay_camp;', 'procedure lay_slot(variable slot);', '',
      'procedure lay_obj(variable pid, variable tile) begin',
      '   if (not tile_contains_pid_obj(tile, 0, pid)) then create_object(pid, tile, 0);', 'end', '',
      'procedure lay_camp begin']
for t, p in L['base']: o.append(f'   call lay_obj({p}, {t});')
o.append(f'   create_object_sid({0x02000000 | 993}, LAY_OLDWELL, 0, SCRIPT_F2MWELL);   // старый заколоченный колодец')
o.append(f'   call lay_obj(128, LAY_LOCKER);   // сундук героя (Footlocker)')
o += ['end', '', 'procedure lay_slot(variable slot) begin']
for i, s in enumerate(SLOTS):
    o.append(f'   {"if" if i == 0 else "else if"} (slot == {i}) then begin   // {s}')
    for t, p in DONE[s]:
        if s == 'newwell': o.append(f'      if (not tile_contains_pid_obj({t}, 0, {p})) then create_object_sid({p}, {t}, 0, SCRIPT_F2MWELL);')
        else: o.append(f'      call lay_obj({p}, {t});')
    o.append('   end')
o += ['end', '', '#endif', '']
open('/home/claude/f2-rpu-mod/scripts_src/f2mlay.h', 'w', encoding='utf-8').write('\n'.join(o))
print(len(o), 'lines'); print(P)
