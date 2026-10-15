// Жители по домам и на работу (Егор 2026-10-08): как только построены палатки или огороды, мирные не стоят
// у костра, а расходятся: днем сначала по двое на каждом огороде, по водоносу у каждого колодца (носит воду на огород и назад),
// потом по двое у каждой новой палатки (места 3-7); вечером до трех взрослых в баре; бармен и медик (0.9.7),
// ночью (с 21:00 до 6:00) спят в палатках, у кроватей: палатки лагеря 0-2 и палатки прораба 3-7, по трое.
// Кому места не хватило, стоят у костра. Клетки мест — f2mspots.h (tools/layout/spots_emit.py).
// Подключать после f2mcamp.h, f2mspots.h, f2mbld.h и f2mlvl.h (места по уровням зданий, 0.7.0). camp_spread(0) — вход на карту или затемнение (людей просто ставим),
// camp_spread(1) — из map_update: кого видно на экране, тот идет сам, кого не видно — переставляем.
#ifndef F2MHOME_H
#define F2MHOME_H

#include "f2msort.h"

#define camp_night          (game_time_hour >= 2100 or game_time_hour < 600)

procedure camp_spread(variable walk);
procedure camp_is_civ(variable c);
procedure camp_is_child(variable c);
procedure camp_go(variable c, variable t, variable walk);

procedure camp_is_civ(variable c) begin
   variable p;
   if (is_critter_dead(c) or obj_in_party(c)) then return 0;
   p := obj_pid(c);
   return p == PID_WEAK_PEASANT_MALE or p == PID_AVERAGE_PEASANT_MALE or p == PID_AVERAGE_PEASANT_FEMALE
       or p == PID_WEAK_PEASANT_FEMALE or p == PID_CHILD_MALE or p == PID_CHILD_FEMALE;
end

procedure camp_is_child(variable c) begin
   return obj_pid(c) == PID_CHILD_MALE or obj_pid(c) == PID_CHILD_FEMALE;
end

procedure camp_spread(variable walk) begin
   variable spots, n := 0, s, c, i := 0, k, t, u, bar := 0, b := 0, dnum, carry, tend := 0, medic := 0, civs, roles;
   if (combat_is_initialized or get_sfall_global_int(GV_BURY_ON) or get_sfall_global_int(GV_CARAVAN_HOSTILE)) then return;
   spots := temp_array(0, 0);
   dnum := game_time / ONE_GAME_DAY;
   if (camp_night) then begin
      // Вечером (21:00-24:00) у бара сидят до трех взрослых, каждый вечер разные (Егор 2026-10-08)
      if (game_time_hour >= 2100 and bld_shown(U_BAR) >= 1) then bar := 3;
      // по одному месту в каждой палатке, потом по второму, потом по третьему
      k := 0;
      while (k < 3) do begin
         s := 0;
         while (s < 8) do begin
            if (bld_shown(bld_house_unit(s)) >= 1) then begin
               resize_array(spots, n + 1);
               spots[n] := lvl_night(s, bld_shown(bld_house_unit(s)), k);
               n += 1;
            end
            s += 1;
         end
         k += 1;
      end
   end else begin
      // Днем сначала работа: огороды (по двое), водоносы у колодцев (по одному: колодец — огород), потом палатки 3-7
      carry := (game_time / (ONE_GAME_MINUTE * 20)) % 2;
      s := 1;
      while (s <= 9) do begin
         i := s;
         if (s <= 2) then u := U_GARDEN + s - 1;
         else if (s <= 4) then u := U_OLDWELL + s - 3;
         else begin
            i := s - 2;
            u := bld_house_unit(i);
         end
         if (s == 3 or s == 4) then begin
            if (bld_shown(u) >= 1) then begin
               resize_array(spots, n + 1);
               // носит воду на огород: свой (колодец 0 — огород 1, колодец 1 — огород 2), нет его — на другой; огородов нет — стоит у колодца
               k := U_GARDEN + s - 3;
               if (bld_shown(k) < 1) then k := U_GARDEN + 4 - s;
               if (carry and bld_shown(k) >= 1) then spots[n] := tile_num_in_direction(lvl_spot(k - U_GARDEN + 1, bld_shown(k), 0), s, 2);
               else spots[n] := lvl_well(s - 3);
               n += 1;
            end
         end else if (bld_shown(u) >= 1) then begin
            resize_array(spots, n + 2);
            spots[n] := lvl_spot(i, bld_shown(u), 0);
            spots[n + 1] := lvl_spot(i, bld_shown(u), 1);
            n += 2;
         end
         s += 1;
      end
   end
   // Работники (Егор 2026-10-09): бармен у стойки с 6:00 до полуночи, медик у стола с 6:00 до 21:00.
   // Роли закреплены жестко (Егор 2026-10-15, тест 0.9.10): раньше их раздавали по порядку списка существ, а он меняется после
   // каждого разговора — люди менялись ролями и местами и «появлялись из воздуха». Теперь жители упорядочены по id объекта
   // (не меняется ни при разговоре, ни при загрузке): бармен — первый взрослый, медик — второй, хозяйка медальона — первая
   // женщина среди остальных; остальные по своим местам в том же порядке. Пришел ключевой НПС (Ной в бар) — работник
   // становится обычным жителем и идет на свою работу.
   set_sfall_global(GV_BAR_TEND, 0);
   set_sfall_global(GV_MED_TEND, 0);
   if (game_time_hour >= 600 and lvl_staff(U_BAR, bld_shown(U_BAR)) and not get_sfall_global_int(GV_NOAH_HERE)) then tend := 1;
   if (not camp_night and lvl_staff(U_MED, bld_shown(U_MED))) then medic := 1;
   civs := temp_array(0, 0);
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (camp_is_civ(c)) then begin
         resize_array(civs, len_array(civs) + 1);
         civs[len_array(civs) - 1] := c;
      end
   end
   call camp_sort_id(civs);
   // роли: 1 бармен, 2 медик, 3 хозяйка медальона, 0 — по местам
   roles := temp_array(len_array(civs), 0);
   k := 1;
   if (get_sfall_global_int(GV_NOAH_HERE)) then k := 2;   // с Ноем бармена из жителей нет
   while (k <= 2) do begin
      s := 0;
      while (s < len_array(civs)) do begin
         if (roles[s] == 0 and not camp_is_child(civs[s])) then begin
            roles[s] := k;
            s := len_array(civs);
         end
         s += 1;
      end
      k += 1;
   end
   if (thief_victim_on) then begin
      s := 0;
      while (s < len_array(civs)) do begin
         if (roles[s] == 0 and not camp_is_child(civs[s]) and get_critter_stat(civs[s], STAT_gender) == GENDER_FEMALE) then begin
            roles[s] := 3;
            s := len_array(civs);
         end
         s += 1;
      end
   end
   // сначала все, у кого нет роли или работник не на смене, — по местам в постоянном порядке
   i := 0;
   s := 0;
   while (s < len_array(civs)) do begin
      c := civs[s];
      t := 0;
      if (roles[s] == 3) then
         t := THIEF_VICTIM_SPOT;
      else if (roles[s] == 1 and tend) then begin
         t := lvl_staff(U_BAR, bld_shown(U_BAR));
         set_sfall_global(GV_BAR_TEND, t);
      end else if (roles[s] == 2 and medic) then begin
         t := lvl_staff(U_MED, bld_shown(U_MED));
         set_sfall_global(GV_MED_TEND, t);
      end else if (bar and b < bar and roles[s] == 0 and not camp_is_child(c) and (s + dnum) % 2 == 0) then begin
         t := lvl_bar(bld_shown(U_BAR), b);
         b += 1;
      end else begin
         // кому места нет — у костра, как при приходе каравана (cv_civilians)
         if (i < n) then t := spots[i];
         else t := tile_num_in_direction(camp_fire, (i - n) % 6, 2 + ((i - n) / 6) * 2);
         i += 1;
      end
      call camp_go(c, t, walk);
      s += 1;
   end
end

// Житель идет на свое место. Видно на экране старое или новое место — идет пешком; мгновенно переставляем,
// только если не видно ни того, ни другого (вход на карту, затемнение — walk 0)
procedure camp_go(variable c, variable t, variable walk) begin
   if (tile_distance(tile_num(c), t) <= 1) then return;
   if (walk and (tile_is_visible(tile_num(c)) or tile_is_visible(t))) then begin
      if (not anim_busy(c)) then animate_move_obj_to_tile(c, t, 0);
   end else begin
      critter_attempt_placement(c, t, 0);
      anim(c, ANIMATE_ROTATION, random(0, 5));
   end
end

#endif
