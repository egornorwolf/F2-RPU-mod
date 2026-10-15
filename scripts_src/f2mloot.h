// Добыча в сундуках лагеря (Егор 2026-10-15, тест 0.9.10): в баре пиво, газировка и еда, в палатках мелочь,
// в мастерской инструменты, на складе припасы, в медпункте лекарства. Кладем один раз в каждый сундук (сундук нового
// уровня здания тоже получает свое). Какой сундук чей — f2mloott.h (tools/layout/levels_emit.py). Сундуки в доме героя
// не трогаем. Вещи можно просто взять: хозяева их не стерегут.
// Подключать после sfall.h и f2mod.h.
#ifndef F2MLOOT_H
#define F2MLOOT_H
#include "f2mloott.h"

#define ARR_LOOT            "f2mloot"   // pid * 40000 + клетка сундука -> 1 (уже наполнен)

procedure loot_sync;
procedure loot_fill(variable box, variable kind);
procedure loot_put(variable box, variable pid, variable n);

procedure loot_put(variable box, variable pid, variable n) begin
   if (n > 0) then add_mult_objs_to_inven(box, create_object(pid, 0, 0), n);
end

procedure loot_fill(variable box, variable kind) begin
   variable r;
   if (kind == 1) then begin            // бар
      call loot_put(box, PID_BEER, random(2, 4));
      call loot_put(box, PID_NUKA_COLA, random(1, 3));
      call loot_put(box, PID_GAMMA_GULP_BEER, random(0, 1));
      call loot_put(box, PID_IGUANA_ON_A_STICK, random(1, 2));
      call loot_put(box, PID_MEAT_ON_A_STICK, random(0, 1));
   end else if (kind == 2) then begin   // палатка: одна-две мелочи
      r := random(0, 5);
      if (r == 0) then call loot_put(box, PID_FLARE, 1);
      else if (r == 1) then call loot_put(box, PID_LIGHTER, 1);
      else if (r == 2) then call loot_put(box, PID_DECK_OF_CARDS, 1);
      else if (r == 3) then call loot_put(box, PID_CHEEZY_POOFS, 1);
      else if (r == 4) then call loot_put(box, PID_BOX_OF_NOODLES, 1);
      else call loot_put(box, PID_HEALING_POWDER, 1);
      if (random(0, 1)) then item_caps_adjust(box, random(5, 25));
   end else if (kind == 3) then begin   // мастерская
      call loot_put(box, PID_WRENCH, 1);
      call loot_put(box, PID_OIL_CAN, 1);
      call loot_put(box, PID_FLARE, random(1, 2));
      call loot_put(box, PID_ROPE, random(0, 1));
   end else if (kind == 4) then begin   // склад
      call loot_put(box, PID_IGUANA_ON_A_STICK, random(1, 2));
      call loot_put(box, PID_MEAT_JERKY, random(1, 2));
      call loot_put(box, PID_WATER_FLASK, 1);
      call loot_put(box, PID_ROPE, 1);
   end else if (kind == 5) then begin   // медпункт
      call loot_put(box, PID_HEALING_POWDER, random(1, 2));
      call loot_put(box, PID_ANTIDOTE, 1);
   end
end

// Вход в лагерь: новые сундуки (после стройки) получают добычу
procedure loot_sync begin
   variable o, arr, k, key;
   arr := load_array(ARR_LOOT);
   if (not arr) then begin
      arr := create_array_map;
      save_array(ARR_LOOT, arr);
   end
   foreach (o in list_as_array(LIST_GROUNDITEMS)) begin
      if (elevation(o) == 0 and obj_item_subtype(o) == item_type_container) then begin
         k := loot_kind(tile_num(o));
         key := obj_pid(o) * 40000 + tile_num(o);
         if (k and not arr[key]) then begin
            arr[key] := 1;
            call loot_fill(o, k);
         end
      end
   end
end

#endif
