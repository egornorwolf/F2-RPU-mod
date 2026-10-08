// Ночной вор Томми Ларк (квест 2.6, карточка в docs/npc-cards.md): когда жилье доросло до 2-го уровня,
// из хижин начинают пропадать вещи. Ночью вор ходит между домами. Поймать его можно по-разному:
// подойти в режиме скрытности (Скрытность 50), заметить издали (Восприятие 7) или просто столкнуться вплотную.
// Пойманному герой решает судьбу: убить, прогнать или оставить работать (Красноречие 50).
// Пока вор не пойман, каждую неделю из кассы поселения пропадает немного крышек.
// Подключать после define.h, command.h, sfall.h, f2mod.h, f2mcv.h, f2mcamp.h, f2mbld.h, f2mhome.h и f2mset.h.
#ifndef F2MTHIEF_H
#define F2MTHIEF_H

#define GV_THIEF        "f2mthfst"  // 0 тихо, 1 кражи идут, 2 вор на карте этой ночью, 3 прогнан, 4 убит, 5 остался работать
#define GV_THIEF_WEEK   "f2mthfwk"  // неделя, за которую воровство уже посчитали (+1)
#define GV_THIEF_SEEN   "f2mthfsn"  // 1 = герой заметил его этой ночью (Восприятие или скрытность)
#define GV_THIEF_HOUR   "f2mthfhr"  // раньше этого часа вор снова не выйдет (спугнули — ждет следующей ночи)

#define THIEF_NONE      (0)
#define THIEF_STEALS    (1)
#define THIEF_HERE      (2)
#define THIEF_GONE      (3)
#define THIEF_DEAD      (4)
#define THIEF_WORKS     (5)

#define PID_THIEF       (16777454)  // Raider: модель меняем на NMMAXZ (кожаная куртка), анимации ножа есть
#define THIEF_SNEAK     (50)        // Скрытность: подойти незамеченным
#define THIEF_PE        (7)         // Восприятие: заметить его в темноте за несколько клеток
#define THIEF_SPEECH    (50)        // Красноречие: оставить работать
#define THIEF_XP        (150)
#define THIEF_CAPS      (20)        // украденные крышки возвращаются герою
#define THIEF_WEEK_LOSS (50)        // крышек из кассы за неделю, пока вор на свободе

#define thief_msg(n)    message_str(SCRIPT_F2MTHIEF, n)
#define thief_done      (get_sfall_global_int(GV_THIEF) >= THIEF_GONE)

procedure thief_obj;
procedure thief_spot;
procedure thief_put;
procedure thief_clear;
procedure thief_tick;

procedure thief_obj begin
   variable c;
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      // модель та же, что у налетчиков, поэтому отличаем по команде: вор не из банды
      if (obj_pid(c) == PID_THIEF and not is_critter_dead(c)
          and has_trait(TRAIT_OBJECT, c, OBJECT_TEAM_NUM) == TEAM_CARAVAN) then return c;
   end
   return 0;
end

// Ходит у жилья: берем место у одной из палаток
procedure thief_spot begin
   variable s := 0, u;
   while (s < 8) do begin
      u := bld_house_unit(s);
      if (bld_shown(u) >= 2) then return lvl_spot(s + 3, bld_shown(u), 1);
      s += 1;
   end
   return tile_num_in_direction(camp_fire, 3, 4);
end

// Вор на карте этой ночью: нож, украденное при нем
procedure thief_put begin
   variable obj;
   if (thief_obj) then return;
   obj := create_object_sid(PID_THIEF, cv_free_tile(thief_spot), 0, SCRIPT_F2MTHIEF);
   critter_add_trait(obj, TRAIT_OBJECT, OBJECT_TEAM_NUM, TEAM_CARAVAN);
   art_change_fid_num(obj, GANG_ART_JACKET);
   add_obj_to_inven(obj, create_object(PID_GOLD_LOCKET, 0, 0));
   item_caps_adjust(obj, THIEF_CAPS);
   add_obj_to_inven(obj, create_object(PID_KNIFE, 0, 0));
   anim(obj, ANIMATE_ROTATION, random(0, 5));
   set_sfall_global(GV_THIEF, THIEF_HERE);
   set_sfall_global(GV_THIEF_SEEN, 0);
end

// Утро или герой ушел: вор растворился до следующей ночи
procedure thief_clear begin
   variable c;
   c := thief_obj;
   if (c) then destroy_object(c);
   if (get_sfall_global_int(GV_THIEF) == THIEF_HERE) then begin
      set_sfall_global(GV_THIEF, THIEF_STEALS);
      set_sfall_global(GV_THIEF_HOUR, bld_hour + 10);   // спугнули: придет не раньше следующей ночи
   end
end

// Из глобального скрипта: жалобы, ночные выходы вора и недельная убыль кассы
procedure thief_tick begin
   variable cash;
   if (not set_founded or thief_done or get_sfall_global_int(GV_SET_ABANDON) != ABANDON_NO) then return;
   // Кражи начинаются, когда жилье доросло до 2-го уровня
   if (get_sfall_global_int(GV_THIEF) == THIEF_NONE) then begin
      if (bld_shown(bld_house_unit(0)) < 2 and bld_shown(bld_house_unit(1)) < 2) then return;
      set_sfall_global(GV_THIEF, THIEF_STEALS);
      set_sfall_global(GV_THIEF_WEEK, set_weeks_now + 1);
      if (cur_map_index == MAP_F2MOD_CAMP) then display_msg(thief_msg(200));
      return;
   end
   // Пока вор на свободе, за неделю из кассы пропадает немного крышек
   if (get_sfall_global_int(GV_THIEF_WEEK) != set_weeks_now + 1) then begin
      set_sfall_global(GV_THIEF_WEEK, set_weeks_now + 1);
      cash := get_sfall_global_int(GV_SET_CASH) - THIEF_WEEK_LOSS;
      if (cash < 0) then cash := 0;
      set_sfall_global(GV_SET_CASH, cash);
   end
   if (cur_map_index != MAP_F2MOD_CAMP or combat_is_initialized) then begin
      if (thief_obj) then call thief_clear;
      return;
   end
   if (camp_night) then begin
      if (get_sfall_global_int(GV_THIEF) == THIEF_STEALS and (get_game_mode bwand 0x3FFFFD) == 0
          and bld_hour >= get_sfall_global_int(GV_THIEF_HOUR) and random(1, 100) <= 35) then
         call thief_put;
   end else if (get_sfall_global_int(GV_THIEF) == THIEF_HERE) then
      call thief_clear;
end

#endif
