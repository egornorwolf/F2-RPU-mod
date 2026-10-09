// Охрана и караванщик сами воюют с врагами на дороге (и с бандой Кейна у ворот лагеря, 1.3а) и начинают бой сразу, как только враги есть на карте.
// Подключать в скрипт существа после define.h, command.h, sfall.h, define_extra.h и f2mod.h.
#ifndef F2MCFGT_H
#define F2MCFGT_H

// Звери в лагере (Егор 2026-10-09): стая у забора (2.17) и крысы на огородах (2.2) — охрана и ополчение бьют их сами,
// если те близко (CFGT_BEAST_SEE клеток)
#define CFGT_BEAST_SEE      (15)
#define cfgt_beast(c)       (cur_map_index == MAP_F2MOD_CAMP and \
                             ((get_sfall_global_int("f2mwilds") == 1 and (obj_pid(c) == PID_CENTAUR or obj_pid(c) == PID_FLOATER)) \
                              or (get_sfall_global_int("f2mratst") == 1 and obj_pid(c) == 16777328)))

procedure cv_nearest_enemy;
procedure cv_fight;

procedure cv_nearest_enemy begin
   variable c, best := 0, d, best_d := 9999;
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (not is_critter_dead(c) and ((is_escort_map(cur_map_index) and is_escort_enemy(obj_pid(c))) or (boss_fight_on and is_gang(c))
          or (cfgt_beast(c) and tile_distance_objs(self_obj, c) <= CFGT_BEAST_SEE))) then begin
         d := tile_distance_objs(self_obj, c);
         if (d < best_d) then begin
            best := c;
            best_d := d;
         end
      end
   end
   return best;
end

// Вне боя: нападаем первыми, и бой начинается для всех сразу.
// В бою (свой ход или «хочу ли вступить»): целимся в ближайшего живого врага.
// Движок ИИ берет цель из «кто меня ударил», поэтому ставим ее туда же.
procedure cv_fight begin
   variable e;
   if (not (is_escort_map(cur_map_index) or boss_fight_on or cur_map_index == MAP_F2MOD_CAMP) or get_sfall_global_int(GV_CARAVAN_HOSTILE)) then return 0;
   e := cv_nearest_enemy;
   if (not e) then return 0;
   set_object_data(self_obj, OBJ_DATA_WHO_HIT_ME, e);
   attack(e);
   return 1;
end

#endif
