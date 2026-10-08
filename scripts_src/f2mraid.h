// Первый набег (1.3) и главарь у ворот (1.3а), docs/quests-detailed.md.
// Набег за кадром: через сутки после основания, когда герой ушел с карты лагеря (пока он там — ждет).
// Потери по тому, что герой успел: ничего — все запасы, половина палаток прораба и угнанный фургон;
// частокол — пятая часть запасов и один погибший житель, люди злы неделю (дух -10%);
// ополчение у Рика или оставленный в лагере спутник (с частоколом или без) — десятая часть запасов,
// без жертв, но следующий набег сильнее на 3 налетчиков.
// Главарь Кейн приходит к воротам через сутки после набега, если герой в лагере, иначе при следующем приходе.
// Подключать после define.h, command.h, scenepid.h, sfall.h, f2mod.h, f2mcv.h, f2mcamp.h, f2mset.h и f2mpay.h (константы набега).
#ifndef F2MRAID_H
#define F2MRAID_H

#define RAID_WAGON          (tile_num_in_direction(LAY_WAGONS, 2, 6))   // третий фургон каравана (cv_wagons)

// Модели банды «Ржавые шакалы» (npc-cards.md): главарь NMMETB, бойцы NMLTBB и NMMAXZ (rpu.dat и npc_armor.dat).
// Готовых прототипов с этими моделями в игре нет: ставим налетчика и меняем ему модель (номер в critters.lst).
#define GANG_ART_BOSS       (FID_NMMETB bwand 0xFFF)
#define GANG_ART_ARMOR      (FID_NMLTBB bwand 0xFFF)   // кожаная броня
#define GANG_ART_JACKET     (FID_NMMAXZ bwand 0xFFF)   // кожаная куртка

procedure raid_hours_since_found;
procedure raid_due;
procedure raid_victim;
procedure raid_do;
procedure raid_companion_pid(variable pid);
procedure raid_companion_left;
procedure boss_due;
procedure gang_setup(variable obj, variable art);
procedure gang_raider(variable tile, variable i);
procedure boss_put;
procedure gang_alive(variable except);
procedure gang_remove;
procedure gang_remove_but(variable keep);

procedure raid_hours_since_found begin
   return game_time / ONE_GAME_HOUR - get_sfall_global_int(GV_CAMP_DAY);
end

// Пора: набега еще не было, лагерь основан сутки назад, герой ушел с карты лагеря
procedure raid_due begin
   if (get_sfall_global_int(GV_RAID) or not get_sfall_global_int(GV_RAID_AWAY)) then return 0;
   if (get_sfall_global_int(GV_CARAVAN) != CARAVAN_DONE or not set_founded) then return 0;
   return raid_hours_since_found >= RAID_HOURS;
end

// Кто погибнет при частоколе: «мальчик с огородов», если он есть, иначе последний из переселенцев
procedure raid_victim begin
   variable i := CV_SLOTS - 1;
   while (i >= CV_SLOT_CIV) do begin
      if (cv_slot_pid(i) == PID_CHILD_MALE and set_here(i)) then return i;
      i -= 1;
   end
   i := CV_SLOTS - 1;
   while (i >= CV_SLOT_CIV) do begin
      if (set_here(i)) then return i;
      i -= 1;
   end
   return -1;
end

// Сам набег: считаем потери. Что видно на карте (кровь, тела, ящики, фургон, палатки), ставит карта лагеря при входе.
procedure raid_do begin
   variable out, pct, f, w, i, n := 0, lost := 0, slot;
   set_sfall_global(GV_RAID, 1);
   set_sfall_global(GV_RAID_HOUR, game_time / ONE_GAME_HOUR);
   set_sfall_global(GV_RAID_DECOR, 1);
   if (get_sfall_global_int(GV_SET_MILIT) > 0 or get_sfall_global_int(GV_COMP_STAY)) then out := RAID_OUT_GUARD;
   else if (get_sfall_global_int(GV_FENCE)) then out := RAID_OUT_FENCE;
   else out := RAID_OUT_NONE;
   set_sfall_global(GV_RAID_OUT, out);

   pct := 100;
   if (out == RAID_OUT_FENCE) then pct := 20;
   else if (out == RAID_OUT_GUARD) then pct := 10;
   f := get_sfall_global_int(GV_SET_FOOD) * pct / 100;
   w := get_sfall_global_int(GV_SET_WATER) * pct / 100;
   set_sfall_global(GV_SET_FOOD, get_sfall_global_int(GV_SET_FOOD) - f);
   set_sfall_global(GV_SET_WATER, get_sfall_global_int(GV_SET_WATER) - w);
   set_sfall_global(GV_RAID_FOOD, f);
   set_sfall_global(GV_RAID_WATER, w);

   if (out == RAID_OUT_NONE) then begin
      // Половина палаток прораба (с конца), фургон угнан
      i := BUILD_TENT;
      while (i < BUILD_HERO) do begin
         if (camp_built(i)) then n += 1;
         i += 1;
      end
      n := (n + 1) / 2;
      i := BUILD_HERO - 1;
      while (i >= BUILD_TENT and n > 0) do begin
         if (camp_built(i)) then begin
            set_sfall_global(GV_CAMP_BUILT, get_sfall_global_int(GV_CAMP_BUILT) bwand bwnot(cv_bit(i)));
            lost := lost bwor cv_bit(i);
            n -= 1;
         end
         i -= 1;
      end
      set_sfall_global(GV_RAID_TENTS, lost);
      set_sfall_global(GV_WAGON, 1);
   end else if (out == RAID_OUT_FENCE) then begin
      slot := raid_victim;
      if (slot >= 0) then begin
         call cv_set_dead(slot);
         set_sfall_global(GV_RAID_DEAD, cv_slot_pid(slot));
         set_sfall_global(GV_SET_SYNC, 1);
      end
      set_sfall_global(GV_SET_ANGRY, game_time / ONE_GAME_HOUR + 168);
   end else
      set_sfall_global(GV_RAID_NEXT, RAID_NEXT_EXTRA);
   call set_short_morale(get_sfall_global_int(GV_SET_FSHORT), get_sfall_global_int(GV_SET_WSHORT));
end

// Спутники героя (party.h RPU): кого можно оставить в лагере. Багажник машины не в счет.
procedure raid_companion_pid(variable pid) begin
   return pid == PID_VIC or pid == PID_MYRON or pid == PID_MARCUS or pid == PID_JOHN_MACRAE or pid == PID_SULIK
       or pid == PID_LENNY or pid == PID_CYBERDOG or pid == PID_DOC or pid == PID_GORIS or pid == PID_DAVIN
       or pid == PID_MIRIA or pid == PID_BRAINBOT or pid == PID_DOGMEAT or pid == PID_PARIAH_DOG or pid == PID_K9
       or pid == PID_ROBOBRAIN_HUMAN or pid == PID_ROBOBRAIN_ABNORMAL or pid == PID_ROBOBRAIN_CHIMP or pid == PID_LADDIE
       or pid == PID_KARL or pid == PID_JONNY or pid == PID_LLOYD or pid == PID_KITSUNE or pid == PID_DEX or pid == PID_CAT_JULES;
end

// Герой уходит с карты лагеря: остался ли там живой спутник («подожди здесь» выводит его из отряда)
procedure raid_companion_left begin
   variable c;
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (not is_critter_dead(c) and raid_companion_pid(obj_pid(c)) and not obj_in_party(c)) then return 1;
   end
   return 0;
end

// Главарь: через сутки после набега (герой в лагере — сразу, нет — при следующем приходе)
procedure boss_due begin
   if (not get_sfall_global_int(GV_RAID) or get_sfall_global_int(GV_BOSS) != BOSS_NONE) then return 0;
   return game_time / ONE_GAME_HOUR >= get_sfall_global_int(GV_RAID_HOUR) + BOSS_HOURS;
end

// Банда: своя команда и модель по карточке. Модель меняем до того, как дать оружие:
// движок проверяет анимации оружия по номеру модели.
procedure gang_setup(variable obj, variable art) begin
   critter_add_trait(obj, TRAIT_OBJECT, OBJECT_TEAM_NUM, TEAM_F2M_GANG);
   art_change_fid_num(obj, art);
end

// Рядовой налетчик (npc-cards.md): одно из шести оружий, у NMLTBB и NMMAXZ есть анимации всех (D, E, H, I, J);
// броня по виду модели: кожаная броня или кожаная куртка
procedure gang_raider(variable tile, variable i) begin
   variable obj, k, armor, it;
   obj := create_object_sid(PID_RAIDER_MALE, cv_free_tile(tile), 0, SCRIPT_F2MRDR);
   if (i % 2) then begin
      call gang_setup(obj, GANG_ART_JACKET);
      armor := PID_LEATHER_JACKET;
   end else begin
      call gang_setup(obj, GANG_ART_ARMOR);
      armor := PID_LEATHER_ARMOR;
   end
   it := create_object(armor, 0, 0);
   add_obj_to_inven(obj, it);
   wield_obj_critter(obj, it);
   k := i % 6;
   if (k == 0) then call cv_arm(obj, PID_KNIFE, 0);
   else if (k == 1) then call cv_arm(obj, PID_CLUB, 0);
   else if (k == 2) then call cv_arm(obj, PID_10MM_PISTOL, PID_10MM_JHP);
   else if (k == 3) then call cv_arm(obj, PID_10MM_SMG, PID_10MM_JHP);
   else if (k == 4) then call cv_arm(obj, PID_HUNTING_RIFLE, PID_223_FMJ);
   else call cv_arm(obj, PID_SAWED_OFF_SHOTGUN, PID_SHOTGUN_SHELLS);
   anim(obj, ANIMATE_ROTATION, 5);
   return obj;
end

// Кейн у ворот, 20 бойцов на краю карты по обе стороны дороги (у въезда на карту, их видно)
procedure boss_put begin
   variable obj, i := 0, x, y;
   set_sfall_global(GV_BOSS, BOSS_WAIT);
   obj := create_object_sid(PID_RAIDER_MALE, cv_free_tile(RAID_GATE_OUT), 0, SCRIPT_F2MBOSS);
   call gang_setup(obj, GANG_ART_BOSS);
   call cv_arm(obj, PID_COMBAT_SHOTGUN, PID_SHOTGUN_SHELLS);
   add_obj_to_inven(obj, create_object(PID_10MM_SMG, 0, 0));
   add_mult_objs_to_inven(obj, create_object(PID_10MM_JHP, 0, 0), 2);
   add_obj_to_inven(obj, create_object(PID_KNIFE, 0, 0));
   set_critter_base_stat(obj, STAT_max_hp, 90);
   critter_heal(obj, 200);
   anim(obj, ANIMATE_ROTATION, 5);
   while (i < GANG_SIZE) do begin
      x := 78 + 28 * (i / 10) + (i % 5) * 4;
      y := 180 + ((i % 10) / 5) * 3;
      call gang_raider(y * 200 + x, i);
      i += 1;
   end
end

// Живые бойцы банды, кроме except (в destroy_p_proc вне боя умирающий еще считается живым: fallout2-ce combat.cc)
procedure gang_alive(variable except) begin
   variable c, n := 0;
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (c != except and is_gang(c) and not is_critter_dead(c)) then n += 1;
   end
   return n;
end

// Банда ушла: убираем живых (трупы остаются)
procedure gang_remove begin
   call gang_remove_but(0);
end

// Все живые бойцы банды, кроме keep: скрипт, который убирает банду, не должен уничтожить сам себя
// посреди затемнения (иначе он обрывается и экран остается черным)
procedure gang_remove_but(variable keep) begin
   variable c;
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (c != keep and is_gang(c) and not is_critter_dead(c)) then destroy_object(c);
   end
end

#endif
