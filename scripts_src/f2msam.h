// Радист Сэм Мортон (0.7.1, карточка в docs/npc-cards.md, квест 1.3: «на следующий день после набега приходит радист»).
// Приходит через сутки после первого набега, если в домах есть свободное место (палатка 2, шатер 4); нет места — ждет.
// Ставит радио (маленький стол с пультом снаружи у построенного здания, 1 день, бесплатно; места нет — просит место), продает герою рацию за 50. С рацией в рюкзаке
// вдали от лагеря герой слышит, что еды или воды до конца недели не хватит (сразу после недельной проверки, за неделю).
// Подключать после define.h, command.h, sfall.h, f2mod.h, f2mcv.h, f2mcamp.h и f2mset.h (в нем f2mbld.h).
#ifndef F2MSAM_H
#define F2MSAM_H

#define GV_SAM          "f2msamst"  // SAM_* ниже
#define GV_SAM_HOUR     "f2msamhr"  // когда радио будет готово: game_time / ONE_GAME_HOUR
#define GV_SAM_NEWS     "f2msamnw"  // сказать герою при входе: 1 радист пришел, 2 приходил, но жить негде
#define GV_SAM_WEEK     "f2msamwk"  // неделя, за которую рация уже предупредила (+1)
#define GV_SAM_TABLE    "f2msamtb"  // здание (U_*) + 1, у которого стоит временный стол с радио (0 — стола нет)
#define GV_RADIO_ROOM   "f2mradrm"  // 1 = построена радиостанция (buildings-levels.md): временный стол сносим

#define SAM_NONE        (0)
#define SAM_HERE        (1)     // пришел, ждет разговора
#define SAM_BUILDING    (2)     // ставит радио у старосты
#define SAM_RADIO       (3)     // малое радио работает
#define SAM_DEAD        (9)

#define PID_SAM         (16777511)  // Technicion: модель NMLABB (белый халат), анимации пистолета есть
#define SAM_RADIO_PRICE (50)        // рация герою
#define SAM_BUILD_HOURS (24)
#define SAM_HANDS_SKILL (50)        // Ремонт или Наука: собрать рацию самому, бесплатно
#define SAM_HANDS_XP    (50)
// Временный стол (Егор 2026-10-09): маленький стол table1 с пультом comp5 снаружи у любого построенного здания.
// Места у каждого здания считает tools/layout/levels_emit.py (f2mradl.h). Большой стол ltable2 у старосты — до 0.9.6
#define PID_RTABLE_S    (33554732)  // table1: маленький стол
#define PID_RTABLE_OLD  (33554926)  // ltable2: прежний большой стол (убираем из сохранений)
#include "f2mradl.h"

procedure sam_places;
procedure sam_free;
procedure sam_obj;
procedure sam_put;
procedure sam_radio_decor;
procedure sam_tick;
procedure sam_has_radio;
procedure sam_table_unit;
procedure sam_home;

// Мест в домах: палатка 2, шатер 4 (buildings-levels.md)
procedure sam_places begin
   variable u := U_HOUSE, n := 0, lv;
   while (u < U_HOUSE + 8) do begin
      lv := bld_level(u);
      if (lv == 1) then n += 2;
      else if (lv >= 2) then n += 4;
      u += 1;
   end
   return n;
end

procedure sam_free begin
   return sam_places > set_civs_here;
end

procedure sam_obj begin
   variable c;
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (obj_pid(c) == PID_SAM and not is_critter_dead(c)) then return c;
   end
   return 0;
end

// Радист на карте лагеря у радио (или у костра, пока радио нет): 10-мм пистолет, кусачки, своя рация
procedure sam_put begin
   variable obj;
   if (sam_obj) then return;
   obj := cv_put(PID_SAM, SCRIPT_F2MRADIO, sam_home);
   critter_add_trait(obj, TRAIT_OBJECT, OBJECT_AI_PACKET, AI_ADDICT_WIMPY);
   call cv_arm(obj, PID_10MM_PISTOL, PID_10MM_JHP);
   add_obj_to_inven(obj, create_object(PID_MULTI_TOOL, 0, 0));
   add_obj_to_inven(obj, create_object(PID_RADIO, 0, 0));
   anim(obj, ANIMATE_ROTATION, 2);
end

// Здание, у которого встанет стол: стол уже стоит — там же; иначе первое построенное по порядку из f2mradl.h. -1 — места нет
procedure sam_table_unit begin
   variable i := 0, u;
   if (get_sfall_global_int(GV_SAM_TABLE)) then return get_sfall_global_int(GV_SAM_TABLE) - 1;
   while (i < RADIO_ORDER_N) do begin
      u := radio_unit(i);
      if (bld_shown(u) >= 1 and radio_spot(u)) then return u;
      i += 1;
   end
   return -1;
end

// Где стоит радист: у своего стола, пока стола нет — на прежнем месте у костра
procedure sam_home begin
   variable u;
   u := get_sfall_global_int(GV_SAM_TABLE) - 1;
   if (u >= 0 and radio_sam(u)) then return radio_sam(u);
   return BLD_SAM;
end

// Стол с пультом (стоит, как только радист взялся за работу): снаружи, у построенного здания, не на людях.
// Построена радиостанция — временный стол сносим
procedure sam_radio_decor begin
   variable u, t, obj;
   // сохранения до 0.9.6: большой стол у старосты
   obj := tile_contains_pid_obj(BLD_RADIO, 0, PID_RTABLE_OLD);
   if (obj) then begin
      destroy_object(obj);
      obj := tile_contains_pid_obj(BLD_RADIO, 0, PID_RCOMP);
      if (obj) then destroy_object(obj);
   end
   if (get_sfall_global_int(GV_SAM) < SAM_BUILDING or get_sfall_global_int(GV_SAM) == SAM_DEAD) then return;
   u := sam_table_unit;
   if (u < 0) then return;
   t := radio_spot(u);
   if (get_sfall_global_int(GV_RADIO_ROOM)) then begin
      obj := tile_contains_pid_obj(t, 0, PID_RTABLE_S);
      if (obj) then destroy_object(obj);
      obj := tile_contains_pid_obj(t, 0, PID_RCOMP);
      if (obj) then destroy_object(obj);
      return;
   end
   set_sfall_global(GV_SAM_TABLE, u + 1);
   if (not tile_contains_pid_obj(t, 0, PID_RTABLE_S)) then create_object(PID_RTABLE_S, t, 0);
   if (not tile_contains_pid_obj(t, 0, PID_RCOMP)) then create_object(PID_RCOMP, t, 0);
end

procedure sam_has_radio begin
   return obj_is_carrying_obj_pid(dude_obj, PID_RADIO) > 0;
end

// Из глобального скрипта раз в несколько секунд: приход радиста, готовое радио, вызовы по рации
procedure sam_tick begin
   variable st, n, need, have, msg := "";
   st := get_sfall_global_int(GV_SAM);
   if (st == SAM_NONE and get_sfall_global_int(GV_RAID)
       and bld_hour >= get_sfall_global_int(GV_RAID_HOUR) + 24 and get_sfall_global_int(GV_SET_ABANDON) == ABANDON_NO) then begin
      if (sam_free) then begin
         set_sfall_global(GV_SAM, SAM_HERE);
         set_sfall_global(GV_SAM_NEWS, 1);
      end else if (not get_sfall_global_int(GV_SAM_NEWS)) then
         set_sfall_global(GV_SAM_NEWS, 2);
   end
   if (st == SAM_BUILDING and bld_hour >= get_sfall_global_int(GV_SAM_HOUR)) then begin
      set_sfall_global(GV_SAM, SAM_RADIO);
      display_msg(message_str(SCRIPT_F2MRADIO, 300));
   end
   // Рация: сразу после недельной проверки (или как только рация у героя), за неделю до следующей:
   // с любого конца карты успеть вернуться (Егор 2026-10-08: 3 дня — мало)
   if (st != SAM_RADIO or cur_map_index == MAP_F2MOD_CAMP or not sam_has_radio or not set_founded) then return;
   if (get_sfall_global_int(GV_SAM_WEEK) == set_weeks_now + 1) then return;
   set_sfall_global(GV_SAM_WEEK, set_weeks_now + 1);
   n := set_people;
   have := get_sfall_global_int(GV_SET_FOOD) + set_food_prod;
   need := 0;
   if (have < n) then need := (n - have) * SET_FOOD_PRICE;
   if (need > get_sfall_global_int(GV_SET_CASH)) then msg := message_str(SCRIPT_F2MRADIO, 301);
   have := get_sfall_global_int(GV_SET_WATER) + bld_water;
   if (have < n and (n - have) * SET_WATER_PRICE + need > get_sfall_global_int(GV_SET_CASH)) then begin
      if (msg == "") then msg := message_str(SCRIPT_F2MRADIO, 307);
      else msg += message_str(SCRIPT_F2MRADIO, 302);
   end
   if (msg != "") then display_msg(message_str(SCRIPT_F2MRADIO, 303) + msg + message_str(SCRIPT_F2MRADIO, 306));
end

#endif
