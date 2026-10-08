// Уровни зданий на карте лагеря (0.7.0): то, что достроено, а на карте еще прежнее, переставляем (f2mlvl.h).
// Зовут карта лагеря при входе и Хэнк (стройка закончилась при герое: через затемнение).
// Подключать после f2mbld.h, f2mlvl.h и f2mhome.h.
#ifndef F2MBLDAP_H
#define F2MBLDAP_H

procedure bld_apply;
procedure bld_after(variable u, variable lv);
procedure bld_fire_light;

// Свет костра: кострище в прототипе не светит (как в f2mtlay.h, lay_lights)
procedure bld_fire_light begin
   variable fp;
   fp := tile_contains_pid_obj(camp_fire, 0, LAY_FIREPIT);
   if (fp) then obj_set_light_level(fp, 100, 5);
end

// После перестройки: староста к шатру, брамины в загон
procedure bld_after(variable u, variable lv) begin
   variable c, n := 0;
   if (u == U_CENTRE and lv == 2) then begin
      call bld_fire_light;
      foreach (c in list_as_array(LIST_CRITTERS)) begin
         if (obj_pid(c) == PID_AVERAGE_MERCHANT_MALE and not is_critter_dead(c) and not obj_in_party(c)) then begin
            critter_attempt_placement(c, LVL_TED2, 0);
            anim(c, ANIMATE_ROTATION, 2);
         end
      end
   end
   if (u == U_FARM and lv == 2) then begin
      foreach (c in list_as_array(LIST_CRITTERS)) begin
         if (obj_pid(c) == PID_BRAHMIN and not is_critter_dead(c) and not obj_in_party(c) and n < 2) then begin
            if (n == 0) then critter_attempt_placement(c, LVL_BRAHMIN0, 0);
            else critter_attempt_placement(c, LVL_BRAHMIN1, 0);
            n += 1;
         end
      end
   end
end

// Возвращает, сколько уровней поставлено
procedure bld_apply begin
   variable u := 0, n := 0, lv;
   set_sfall_global(GV_BLD_SYNC, 0);
   while (u < U_COUNT) do begin
      while (bld_shown(u) < bld_level(u) and bld_shown(u) < U_TOP_LEVEL) do begin
         lv := bld_shown(u) + 1;
         call lvl_step(u, lv);
         call bld_set_shown(u, lv);
         call bld_after(u, lv);
         n += 1;
      end
      u += 1;
   end
   if (n) then call camp_spread(0);
   return n;
end

#endif
