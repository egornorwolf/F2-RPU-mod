// Лечение жителей и охраны (Егор 2026-10-11). Без медпункта лечит только движок (14 здоровья за 3 часа отлучки героя).
// Медпункт любого уровня: раз в сутки всем жителям и охране здоровье до полного, и при герое в лагере.
// Клиника (3-й уровень, с доктором): то же сразу после боя.
// Подключать в скрипт карты лагеря после f2mod.h, f2mbld.h и f2mlvl.h.
#ifndef F2MHEAL_H
#define F2MHEAL_H

#define GV_HEAL_DAY     "f2mheald"  // день игры (+1), когда медпункт лечил в последний раз
#define GV_HEAL_FIGHT   "f2mhealf"  // 1 = в бою на карте лагеря ранили жителя (ставит gl_f2mod)
#define HEAL_CLINIC     (3)

procedure heal_all;
procedure heal_tick;

procedure heal_all begin
   variable c;
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (c != dude_obj and not obj_in_party(c) and not is_critter_dead(c)
          and has_trait(TRAIT_OBJECT, c, OBJECT_TEAM_NUM) == TEAM_CARAVAN
          and get_critter_stat(c, STAT_current_hp) < get_critter_stat(c, STAT_max_hp)) then
         critter_heal(c, get_critter_stat(c, STAT_max_hp));
   end
end

// Из map_enter и map_update карты лагеря (движок зовет map_update и сразу после конца боя)
procedure heal_tick begin
   variable today;
   if (combat_is_initialized) then return;
   if (get_sfall_global_int(GV_HEAL_FIGHT)) then begin
      set_sfall_global(GV_HEAL_FIGHT, 0);
      if (bld_shown(U_MED) >= HEAL_CLINIC) then call heal_all;
   end
   if (bld_shown(U_MED) < 1) then return;
   today := game_time / ONE_GAME_DAY + 1;
   if (get_sfall_global_int(GV_HEAL_DAY) == today) then return;
   set_sfall_global(GV_HEAL_DAY, today);
   call heal_all;
end

#endif
