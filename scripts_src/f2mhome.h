// Жители по домам и на работу (Егор 2026-10-08): как только построены палатки или огороды, мирные не стоят
// у костра, а расходятся: днем по двое у каждой новой палатки (места 3-7) и на каждом огороде (1-2),
// ночью (с 21:00 до 6:00) спят в палатках, у кроватей: палатки лагеря 0-2 и палатки прораба 3-7, по трое.
// Кому места не хватило, стоят у костра. Клетки мест — f2mspots.h (tools/layout/spots_emit.py).
// Подключать после f2mcamp.h, f2mspots.h, f2mbld.h и f2mlvl.h (места по уровням зданий, 0.7.0). camp_spread(0) — вход на карту или затемнение (людей просто ставим),
// camp_spread(1) — из map_update: кого видно на экране, тот идет сам, кого не видно — переставляем.
#ifndef F2MHOME_H
#define F2MHOME_H

#define camp_night          (game_time_hour >= 2100 or game_time_hour < 600)

procedure camp_spread(variable walk);
procedure camp_is_civ(variable c);

procedure camp_is_civ(variable c) begin
   variable p;
   if (is_critter_dead(c) or obj_in_party(c)) then return 0;
   p := obj_pid(c);
   return p == PID_WEAK_PEASANT_MALE or p == PID_AVERAGE_PEASANT_MALE or p == PID_AVERAGE_PEASANT_FEMALE
       or p == PID_WEAK_PEASANT_FEMALE or p == PID_CHILD_MALE or p == PID_CHILD_FEMALE;
end

procedure camp_spread(variable walk) begin
   variable spots, n := 0, s, c, i := 0, k, t, u;
   if (combat_is_initialized or get_sfall_global_int(GV_BURY_ON) or get_sfall_global_int(GV_CARAVAN_HOSTILE)) then return;
   spots := temp_array(0, 0);
   if (camp_night) then begin
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
      s := 3;
      while (s <= 9) do begin
         // сначала палатки 3-7, потом огороды 1-2 (s 8, 9)
         i := s;
         if (s == 8) then i := 1;
         else if (s == 9) then i := 2;
         if (i < BUILD_TENT) then u := U_GARDEN + i - BUILD_GARDEN;
         else u := bld_house_unit(i);
         if (bld_shown(u) >= 1) then begin
            resize_array(spots, n + 2);
            spots[n] := lvl_spot(i, bld_shown(u), 0);
            spots[n + 1] := lvl_spot(i, bld_shown(u), 1);
            n += 2;
         end
         s += 1;
      end
   end
   i := 0;
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (camp_is_civ(c)) then begin
         // кому места нет — у костра, как при приходе каравана (cv_civilians)
         if (i < n) then t := spots[i];
         else t := tile_num_in_direction(camp_fire, (i - n) % 6, 2 + ((i - n) / 6) * 2);
         if (tile_distance(tile_num(c), t) > 1) then begin
            if (walk and tile_is_visible(tile_num(c))) then begin
               if (not anim_busy(c)) then animate_move_obj_to_tile(c, t, 0);
            end else begin
               critter_attempt_placement(c, t, 0);
               anim(c, ANIMATE_ROTATION, random(0, 5));
            end
         end
         i += 1;
      end
   end
end

#endif
