// Жители по домам и на работу (Егор 2026-10-08): как только построены палатки или огороды, мирные не стоят
// у костра, а расходятся: по двое в каждую новую палатку (места 3-7) и на каждый огород (1-2). Кому места
// не хватило, остаются у костра. Клетки мест — f2mspots.h (проходимость проверена tools/layout/spots_emit.py).
// Подключать после f2mcamp.h и f2mspots.h. Звать вне боя (вход на карту, после стройки в затемнении).
#ifndef F2MHOME_H
#define F2MHOME_H

procedure camp_spread;
procedure camp_is_civ(variable c);

procedure camp_is_civ(variable c) begin
   variable p;
   if (is_critter_dead(c) or obj_in_party(c)) then return 0;
   p := obj_pid(c);
   return p == PID_WEAK_PEASANT_MALE or p == PID_AVERAGE_PEASANT_MALE or p == PID_AVERAGE_PEASANT_FEMALE
       or p == PID_WEAK_PEASANT_FEMALE or p == PID_CHILD_MALE or p == PID_CHILD_FEMALE;
end

procedure camp_spread begin
   variable spots, n := 0, s, c, i := 0;
   if (combat_is_initialized) then return;
   spots := temp_array(0, 0);
   s := 3;
   while (s <= 9) do begin
      // сначала палатки 3-7, потом огороды 1-2 (s 8, 9)
      i := s;
      if (s == 8) then i := 1;
      else if (s == 9) then i := 2;
      if (camp_built(i)) then begin
         resize_array(spots, n + 2);
         spots[n] := lay_spot(i, 0);
         spots[n + 1] := lay_spot(i, 1);
         n += 2;
      end
      s += 1;
   end
   if (n == 0) then return;
   i := 0;
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (i < n and camp_is_civ(c)) then begin
         if (tile_num(c) != spots[i]) then critter_attempt_placement(c, spots[i], 0);
         anim(c, ANIMATE_ROTATION, random(0, 5));
         i += 1;
      end
   end
end

#endif
