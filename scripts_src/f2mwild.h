// Дикие твари у забора (квест 2.17 «Мутанты у забора»): стая кентавров и флоатеров приходит к южным воротам.
// Герой может выйти и перебить их сам (касса +300, дух +3) или оставить охране и турелям:
// тогда забор чинят за 100 крышек из кассы. Звери — существа из игры, своих моделей не рисуем.
// Подключать после define.h, command.h, sfall.h, f2mod.h, f2mcv.h, f2mcamp.h, f2mbld.h и f2mset.h.
#ifndef F2MWILD_H
#define F2MWILD_H

#define GV_WILD         "f2mwilds"  // 0 тихо, 1 стая у забора, 2 отбита героем, 3 отбита охраной (забор чинили)
#define GV_WILD_WEEK    "f2mwildw"  // неделя, в которую стая уже приходила (+1)
#define GV_WILD_HOUR    "f2mwildh"  // до этого часа герой еще может выйти сам

#define WILD_COUNT      (4)
#define WILD_HOURS      (4)
#define WILD_PAY        (300)       // в кассу поселения за чистую работу
#define WILD_FIX        (100)       // ремонт забора из кассы, если дрались без героя
#define WILD_MORALE     (3)
#define wild_msg(n)     message_str(SCRIPT_F2MRAT, n)

procedure wild_is(variable c);
procedure wild_alive;
procedure wild_spawn;
procedure wild_win;
procedure wild_tick;

procedure wild_is(variable c) begin
   return obj_pid(c) == PID_CENTAUR or obj_pid(c) == PID_FLOATER;
end

procedure wild_alive begin
   variable c, n := 0;
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (wild_is(c) and not is_critter_dead(c)) then n += 1;
   end
   return n;
end

// Стая за южными воротами, на виду у охраны
procedure wild_spawn begin
   variable i := 0, t;
   set_sfall_global(GV_WILD, 1);
   set_sfall_global(GV_WILD_HOUR, bld_hour + WILD_HOURS);
   while (i < WILD_COUNT) do begin
      t := cv_free_tile(RAID_GATE_OUT + (i % 2) * 200 + (i / 2) * 3 - 3);
      if (i % 2) then create_object_sid(PID_CENTAUR, t, 0, SCRIPT_F2MRAT);
      else create_object_sid(PID_FLOATER, t, 0, SCRIPT_F2MRAT);
      i += 1;
   end
   display_msg(wild_msg(110));
end

// Стая перебита при герое: деньги в кассу и дух
procedure wild_win begin
   if (get_sfall_global_int(GV_WILD) != 1) then return;
   set_sfall_global(GV_WILD, 2);
   set_sfall_global(GV_SET_CASH, get_sfall_global_int(GV_SET_CASH) + WILD_PAY);
   set_sfall_global(GV_SET_MORALE, get_sfall_global_int(GV_SET_MORALE) + WILD_MORALE);
   display_msg(wild_msg(111) + WILD_PAY + wild_msg(112));
end

// Из глобального скрипта: приход стаи и итог, если герой не вышел
procedure wild_tick begin
   variable c, cash;
   if (not set_founded or get_sfall_global_int(GV_SET_ABANDON) != ABANDON_NO) then return;
   if (get_sfall_global_int(GV_WILD) == 1) then begin
      if (wild_alive == 0) then call wild_win;
      else if (bld_hour >= get_sfall_global_int(GV_WILD_HOUR) or cur_map_index != MAP_F2MOD_CAMP) then begin
         set_sfall_global(GV_WILD, 3);
         foreach (c in list_as_array(LIST_CRITTERS)) begin
            if (wild_is(c) and not is_critter_dead(c)) then destroy_object(c);
         end
         cash := get_sfall_global_int(GV_SET_CASH) - WILD_FIX;
         if (cash < 0) then cash := 0;
         set_sfall_global(GV_SET_CASH, cash);
         display_msg(wild_msg(113));
      end
      return;
   end
   // Стая приходит днем, не чаще раза в неделю, когда вокруг лагеря есть забор
   if (get_sfall_global_int(GV_FENCE) and cur_map_index == MAP_F2MOD_CAMP and not camp_night
       and not combat_is_initialized and (get_game_mode bwand 0x3FFFFD) == 0
       and get_sfall_global_int(GV_WILD_WEEK) != set_weeks_now + 1 and random(1, 100) <= 10) then begin
      set_sfall_global(GV_WILD_WEEK, set_weeks_now + 1);
      call wild_spawn;
   end
end

#endif
