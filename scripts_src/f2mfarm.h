// Старший фермер Дэйв Хольц (карточка в docs/npc-cards.md) и два его квеста:
// 2.2 «Крысы в огороде» (ночью на огородах) и 2.3 «Пропавший брамин».
// Фермер приходит как новосел, когда построен хотя бы один огород и в домах есть место.
// Подключать после define.h, command.h, sfall.h, f2mod.h, f2mcv.h, f2mcamp.h, f2mbld.h, f2mlvl.h, f2mset.h и f2msam.h.
#ifndef F2MFARM_H
#define F2MFARM_H
#include "f2mhome.h"   // camp_night: ночь в лагере

#define GV_FARM         "f2mfarst"  // 0 нет, 1 живет в лагере, 9 погиб
#define GV_FARM_NEWS    "f2mfarnw"  // 1 = сказать герою при входе, что пришел старший фермер
#define GV_RATS         "f2mratst"  // 0 тихо, 1 крысы на огородах, 2 отбиты, 3 упущены
#define GV_RATS_WEEK    "f2mratwk"  // неделя, в которую крысы уже приходили (+1)
#define GV_RATS_HOUR    "f2mrathr"  // до этого часа надо разобраться (утро)
#define GV_RATS_AGAIN   "f2mratag"  // проспали крыс: с этого часа (+1) они вернутся в первую же ночь, когда герой в лагере
#define GV_RATS_BOOM    "f2mratbm"  // 1 = у норы рванула граната или динамит (HOOK_ONEXPLOSION в gl_f2mod), разберет farm_tick
#define GV_BRAH         "f2mbrast"  // брамин: 0 тихо, 1 пропал, 2 нашли, 3 не нашли
#define GV_BRAH_WEEK    "f2mbrawk"  // неделя, в которую брамин уже пропадал (+1)

#define PID_FARMER      (16777430)  // Farmer: модель NMBRLP, анимации ножа (D) и винтовки (J) есть
#define PID_RAT_PEST    (16777328)  // Pig Rat: обычная крыса пустоши
#define PID_RAT_HOLE    (33555730)  // modhole1: нора под забором

#define FARM_RATS       (4)         // крыс за ночь
#define RATS_HOURS      (6)         // столько часов до утра, пока можно отбиться
#define RATS_XP         (100)
#define RATS_BLAST_XP   (100)
#define RATS_LOSS_NONE  (20)        // % урожая: никто не вышел
#define RATS_LOSS_GUARD (10)        // % урожая: отбилась охрана (двое и больше)
#define RATS_LOSS_BLAST (5)         // % урожая: нору взорвали
#define RATS_MORALE     (3)
#define RATS_SEAL_REPAIR (60)       // Ремонт: заделать подкоп (иначе кувалда, монтировка, взрывчатка)         // дух: минус, если урожай потрепали
#define BRAH_OUTDOOR    (50)        // Скиталец: найти по следам наверняка
#define BRAH_CHANCE     (50)        // без навыка и с охраной — половина на половину
#define BRAH_PAY        (50)        // пастуху
#define BRAH_PAY_CHANCE (60)
#define BRAH_BUY        (100)       // новый брамин у каравана
#define BRAH_SPEECH     (40)
#define BRAH_XP         (150)
#define BRAH_LOSS       (10)        // % еды за неделю, если брамина так и не нашли
#define BRAH_MORALE     (4)         // дух: минус, если брамина решили не искать (Егор 2026-10-09)

#define farm_here       (get_sfall_global_int(GV_FARM) == 1)
#define farm_msg(n)     message_str(SCRIPT_F2MFARM, n)

procedure farm_obj;
procedure farm_spot;
procedure farm_put;
procedure farm_loss(variable pct);
procedure rats_alive_but(variable except);
procedure rats_alive;
procedure rats_hole;
procedure rats_spawn;
procedure rats_win(variable xp);
procedure rats_hole_obj;
procedure rats_hole_clear;
procedure rats_seal(variable how);
procedure farm_tick;

procedure farm_obj begin
   variable c;
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (obj_pid(c) == PID_FARMER and not is_critter_dead(c)) then return c;
   end
   return 0;
end

// Место фермера: на первом огороде, а пока огородов нет — у костра
procedure farm_spot begin
   if (bld_shown(U_GARDEN) >= 1) then return lvl_spot(1, bld_shown(U_GARDEN), 0);
   return tile_num_in_direction(camp_fire, 1, 2);
end

// Фермер на карте лагеря: нож и охотничье ружье (карточка), анимации у модели есть
procedure farm_put begin
   variable obj;
   if (farm_obj or not farm_here) then return;
   obj := cv_put(PID_FARMER, SCRIPT_F2MFARM, farm_spot);
   critter_add_trait(obj, TRAIT_OBJECT, OBJECT_AI_PACKET, AI_PEASANT);
   call cv_arm(obj, PID_HUNTING_RIFLE, PID_223_FMJ);
   add_obj_to_inven(obj, create_object(PID_KNIFE, 0, 0));
   anim(obj, ANIMATE_ROTATION, 2);
end

// Потеря урожая: процент от недельного сбора огородов уходит из запаса еды
procedure farm_loss(variable pct) begin
   variable n;
   n := set_food_prod * pct / 100;
   if (n < 1) then n := 1;
   if (n > get_sfall_global_int(GV_SET_FOOD)) then n := get_sfall_global_int(GV_SET_FOOD);
   set_sfall_global(GV_SET_FOOD, get_sfall_global_int(GV_SET_FOOD) - n);
   return n;
end

procedure rats_alive_but(variable except) begin
   variable c, n := 0;
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (c != except and obj_pid(c) == PID_RAT_PEST and not is_critter_dead(c)) then n += 1;
   end
   return n;
end

procedure rats_alive begin
   variable c, n := 0;
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (obj_pid(c) == PID_RAT_PEST and not is_critter_dead(c)) then n += 1;
   end
   return n;
end

// Нора под забором у первого огорода: через нее крысы и лезут
procedure rats_hole begin
   return tile_num_in_direction(farm_spot, 0, 4);
end

// Нора на карте (место у огорода могло смениться с уровнем огорода, ищем по всей карте)
procedure rats_hole_obj begin
   variable c;
   foreach (c in list_as_array(LIST_SCENERY)) begin
      if (obj_pid(c) == PID_RAT_HOLE) then return c;
   end
   return 0;
end

// Крысы отбиты, ушли или нору заделали: норы больше нет (0.9.6, Егор: «дыра без крыс»)
procedure rats_hole_clear begin
   variable h;
   h := rats_hole_obj;
   if (h) then destroy_object(h);
end

// Нору закрыли (Егор 2026-10-09): how 0 — взрыв рядом (граната, динамит), 1 — взрывчатка в нору,
// 2 — Ремонт 60, 3 — кувалда или монтировка. Крысы еще лезут — они уходят, урожай почти цел
procedure rats_seal(variable how) begin
   // в бою крыс не убираем (движок падает, если существо исчезает посреди боя): разберет farm_tick после боя
   if (combat_is_initialized) then begin
      set_sfall_global(GV_RATS_BOOM, 1);
      return;
   end
   if (get_sfall_global_int(GV_RATS) == 1) then begin
      if (how) then begin
         gfade_out(1);
         game_time_advance(ONE_GAME_HOUR);
      end
      call rats_win(RATS_BLAST_XP);
      call farm_loss(RATS_LOSS_BLAST);
      call rats_hole_clear;
      if (how) then gfade_in(1);
      if (how >= 2) then display_msg(farm_msg(205 + how));   // 207 Ремонт, 208 кувалда или монтировка
      else display_msg(farm_msg(206));
   end else begin
      call rats_hole_clear;
      display_msg(farm_msg(209));
   end
end

// Ночью на грядках: нора и крысы между ней и огородом (внутри забора)
procedure rats_spawn begin
   variable i := 0, t, g;
   set_sfall_global(GV_RATS, 1);
   set_sfall_global(GV_RATS_AGAIN, 0);
   set_sfall_global(GV_RATS_HOUR, bld_hour + RATS_HOURS);
   t := rats_hole;
   if (not tile_contains_pid_obj(t, 0, PID_RAT_HOLE)) then create_object_sid(PID_RAT_HOLE, t, 0, SCRIPT_F2MRAT);
   g := tile_num_in_direction(farm_spot, 0, 2);
   while (i < FARM_RATS) do begin
      create_object_sid(PID_RAT_PEST, cv_free_tile(tile_num_in_direction(g, i % 6, 1 + i / 3)), 0, SCRIPT_F2MRAT);
      i += 1;
   end
   display_msg(farm_msg(200));
end

// Крысы кончились (бой или взрыв норы): урожай цел, опыт и дух
procedure rats_win(variable xp) begin
   variable c;
   if (get_sfall_global_int(GV_RATS) != 1) then return;
   set_sfall_global(GV_RATS, 2);
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (obj_pid(c) == PID_RAT_PEST and not is_critter_dead(c)) then destroy_object(c);
   end
   give_exp_points(xp);
   set_sfall_global(GV_SET_MORALE, get_sfall_global_int(GV_SET_MORALE) + RATS_MORALE);
   display_msg(farm_msg(201) + xp + farm_msg(202));
   if (xp == RATS_XP) then call rats_hole_clear;   // отбились: крысы больше не лезут, нору засыпали
end

// Из глобального скрипта: приход фермера, ночные крысы и утренний итог, пропажа брамина
procedure farm_tick begin
   variable n;
   if (not set_founded or get_sfall_global_int(GV_SET_ABANDON) != ABANDON_NO) then return;
   // Старший фермер приходит, когда есть огород и место в домах
   if (get_sfall_global_int(GV_FARM) == 0 and bld_shown(U_GARDEN) >= 1 and sam_free) then begin
      set_sfall_global(GV_FARM, 1);
      set_sfall_global(GV_FARM_NEWS, 1);
   end
   // Граната или динамит рванули у норы (HOOK_ONEXPLOSION): нора завалена
   if (get_sfall_global_int(GV_RATS_BOOM) and not combat_is_initialized) then begin
      set_sfall_global(GV_RATS_BOOM, 0);
      if (cur_map_index == MAP_F2MOD_CAMP and rats_hole_obj) then call rats_seal(0);
   end
   // Нора осталась без крыс (сохранения до 0.9.6): убираем
   if (get_sfall_global_int(GV_RATS) != 1 and cur_map_index == MAP_F2MOD_CAMP and rats_hole_obj) then call rats_hole_clear;
   // 2.2 Крысы в огороде: ночью, не чаще раза в неделю, если герой в лагере
   if (get_sfall_global_int(GV_RATS) == 1) then begin
      if (rats_alive == 0) then call rats_win(RATS_XP);
      else if (combat_is_initialized) then begin end   // идет бой: итог после него
      else if (bld_hour >= get_sfall_global_int(GV_RATS_HOUR) or cur_map_index != MAP_F2MOD_CAMP) then begin
         set_sfall_global(GV_RATS, 3);
         // охрана лагеря: Рик, Сара и ополченцы — двое и больше отобьются сами
         if (set_here(CV_SLOT_GUARD) + set_here(CV_SLOT_SARA) + get_sfall_global_int(GV_SET_MILIT) >= 2) then
            n := farm_loss(RATS_LOSS_GUARD);
         else begin
            n := farm_loss(RATS_LOSS_NONE);
            set_sfall_global(GV_SET_MORALE, get_sfall_global_int(GV_SET_MORALE) - RATS_MORALE);
            // проспали (Егор 2026-10-09): крысы вернутся следующей ночью, когда герой будет в лагере
            set_sfall_global(GV_RATS_AGAIN, bld_hour + RATS_HOURS + 1);
         end
         foreach (n in list_as_array(LIST_CRITTERS)) begin
            if (obj_pid(n) == PID_RAT_PEST and not is_critter_dead(n)) then destroy_object(n);
         end
         if (cur_map_index == MAP_F2MOD_CAMP) then call rats_hole_clear;
         display_msg(farm_msg(203));
      end
   end else if (farm_here and bld_shown(U_GARDEN) >= 1 and cur_map_index == MAP_F2MOD_CAMP
                and camp_night and not combat_is_initialized and (get_game_mode bwand 0x3FFFFD) == 0
                and ((get_sfall_global_int(GV_RATS_AGAIN) and bld_hour + 1 >= get_sfall_global_int(GV_RATS_AGAIN))
                     or (get_sfall_global_int(GV_RATS_WEEK) != set_weeks_now + 1 and random(1, 100) <= 20))) then begin
      set_sfall_global(GV_RATS_WEEK, set_weeks_now + 1);
      call rats_spawn;
   end
   // 2.3 Пропавший брамин: утром, не чаще раза в неделю, если брамины в лагере есть
   if (get_sfall_global_int(GV_BRAH) == 0 and farm_here and cur_map_index == MAP_F2MOD_CAMP
       and not camp_night and not combat_is_initialized
       and set_here(CV_SLOT_BRAHMIN) and get_sfall_global_int(GV_BRAH_WEEK) != set_weeks_now + 1
       and random(1, 100) <= 15) then begin
      set_sfall_global(GV_BRAH_WEEK, set_weeks_now + 1);
      set_sfall_global(GV_BRAH, 1);
      display_msg(farm_msg(204));
   end
end

#endif
