// Логово налетчиков в карьере (квест 1.4, quests-detailed.md) и военная база на его месте (1.5, military-base.md).
// Карта f2mlair (копия горной карты mountn5), точки на ней — f2mlairl.h (tools/layout/lair_emit.py).
// Тексты — f2mlair.msg (скрипт карты логова). Подключать после define.h, command.h, sfall.h, f2mod.h, f2mcv.h,
// f2mcamp.h, f2mset.h (в нем f2mbld.h), f2mpay.h и f2mraid.h.
#ifndef F2MLAIR_H
#define F2MLAIR_H

#define GV_LAIR         "f2mlairs"  // 0 неизвестно, 1 герой знает, где логово (кружок на карте), 2 логово взято
#define GV_LAIR_HOW     "f2mlairh"  // как взято: LAIR_HOW_* ниже
#define GV_LAIR_PASS    "f2mlairp"  // 1 = часовой пропустил к главарю
#define GV_LAIR_ALARM   "f2mlaira"  // 1 = банда воюет с героем
#define GV_LAIR_POISON  "f2mlairx"  // 1 = вода отравлена
#define GV_LAIR_CELLAR  "f2mlairc"  // 1 погреб найден, 2 взорван
#define GV_LAIR_PUT     "f2mlairg"  // 1 = банда и предметы уже на карте
#define GV_LAIR_TRACK   "f2mlairt"  // час, когда Рик расскажет, где логово (банда ушла от ворот)
#define GV_BASE_GARR    "f2mbgarr"  // сколько бойцов гарнизона живет на базе (едят из запасов поселения)

#define LAIR_KNOWN      (1)
#define LAIR_DONE       (2)
#define LAIR_HOW_FIGHT  (1)
#define LAIR_HOW_ALLY   (2)     // Кейн сдался, его люди — гарнизон карьера, сам он командир
#define LAIR_HOW_PEACE  (3)     // ушли без боя (Красноречие 100 или 75 и 1000 крышек)
#define LAIR_HOW_BLAST  (4)     // погреб взорван, банда ушла без еды

#define LAIR_WM_X       (830)
#define LAIR_WM_Y       (700)
#define LAIR_GANG       (12)    // бойцов в логове при живом Кейне
#define LAIR_GANG_HEADLESS (10) // Кейн убит у ворот (1.3а): 10 бойцов без главаря
#define LAIR_SEE        (7)     // банда замечает чужого на столько клеток
#define LAIR_SNEAK      (60)    // Скрытность: замечают только вплотную
#define LAIR_SNEAK_SEE  (2)
#define LAIR_POISON_SKILL (50)  // Наука или Первая помощь: доза яда на бочку
#define LAIR_DYN_SKILL  (40)    // Ремонт или Наука: заряд в погреб
#define LAIR_DYN_COUNT  (2)
#define LAIR_PE         (7)     // Восприятие: заметить погреб под камнями
#define LAIR_SPEECH_ALLY (75)
#define LAIR_SPEECH_FREE (100)
#define LAIR_BRIBE      (1000)
#define LAIR_XP         (5000)
#define LAIR_TRACK_HOURS (72)   // банда ушла от ворот: через трое суток Рик знает, где логово

#define PID_LAIR_WATER  (33554983)  // Barrel (бочка, одна клетка)
#define PID_LAIR_CELLAR (33555705)  // Pile of Rocks (камни над лазом в погреб)
#define LAIR_OLD_CRATE  (18702)     // 102, 93: ящик со скриптом случайной встречи из mountn5, убираем
#define U_BASE          (U_BASE_UNIT)   // военная база в f2mbld.h (вне U_COUNT: на карту лагеря не ставится)
#define BASE_TOP_LEVEL  (3)         // 4-й уровень (штаб) — по квесту, позже

#define lair_msg(n)     message_str(SCRIPT_F2MLAIR, n)
#define lair_done       (get_sfall_global_int(GV_LAIR) >= LAIR_DONE)
#define lair_kane_dead  (get_sfall_global_int(GV_BOSS_NOTE) != 0)   // убит у ворот и обыскан (героем или Риком)
#define base_level      (bld_level(U_BASE))
#define base_cap(lv)    ((lv >= 1) * (4 + 2 * (lv)))                // гарнизон 6 / 8 / 10

procedure lair_reveal(variable msg);
procedure lair_tick;
procedure lair_gang_alive(variable except);
procedure lair_seen(variable who);
procedure lair_alarm;
procedure lair_finish(variable how);
procedure lair_gang_leave(variable keep);

procedure lair_reveal(variable msg) begin
   set_sfall_global(GV_LAIR, LAIR_KNOWN);
   mark_area_known(MARK_TYPE_TOWN, AREA_F2MOD_LAIR, MARK_STATE_KNOWN);
   if (msg) then display_msg(lair_msg(msg));
end

// Из глобального скрипта: когда герой узнает, где логово
procedure lair_tick begin
   variable b;
   if (get_sfall_global_int(GV_LAIR)) then return;
   // Обыскал Кейна (сам или Рик): строка в журнал уже была
   if (get_sfall_global_int(GV_BOSS_NOTE)) then begin
      call lair_reveal(200);
      return;
   end
   // Отказал Кейну у ворот: банда ушла, через трое суток охрана выследила, откуда они ходят
   b := get_sfall_global_int(GV_BOSS);
   if (b != BOSS_LEFT and b != BOSS_BEATEN) then return;
   if (not get_sfall_global_int(GV_LAIR_TRACK)) then begin
      set_sfall_global(GV_LAIR_TRACK, bld_hour + LAIR_TRACK_HOURS);
      return;
   end
   if (bld_hour >= get_sfall_global_int(GV_LAIR_TRACK)) then call lair_reveal(201);
end

// Живые бойцы банды на карте, кроме except (Кейн тоже в банде)
procedure lair_gang_alive(variable except) begin
   variable c, n := 0;
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (c != except and is_gang(c) and not is_critter_dead(c)) then n += 1;
   end
   return n;
end

// Заметил ли бандит героя: со Скрытностью 60 и в режиме скрытности — только вплотную
procedure lair_seen(variable who) begin
   variable d;
   d := tile_distance_objs(who, dude_obj);
   if (dude_is_sneaking and has_skill(dude_obj, SKILL_SNEAK) >= LAIR_SNEAK) then return d <= LAIR_SNEAK_SEE;
   return d <= LAIR_SEE and obj_can_see_obj(who, dude_obj);
end

// Тревога: вся банда идет на героя
procedure lair_alarm begin
   variable c;
   if (get_sfall_global_int(GV_LAIR_ALARM) or lair_done) then return;
   set_sfall_global(GV_LAIR_ALARM, 1);
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (is_gang(c) and not is_critter_dead(c)) then set_object_data(c, OBJ_DATA_WHO_HIT_ME, dude_obj);
   end
   display_msg(lair_msg(202));
end

// Логово взято любым путем: опыт, реплика героя, запасы назад в поселение (кроме взрыва погреба)
procedure lair_finish(variable how) begin
   if (lair_done) then return;
   set_sfall_global(GV_LAIR, LAIR_DONE);
   set_sfall_global(GV_LAIR_HOW, how);
   set_sfall_global(GV_LAIR_ALARM, 0);
   give_exp_points(LAIR_XP);
   display_msg(lair_msg(210) + LAIR_XP + lair_msg(211));
   float_msg(dude_obj, lair_msg(212), FLOAT_MSG_YELLOW);
   if (how != LAIR_HOW_BLAST and (get_sfall_global_int(GV_RAID_FOOD) or get_sfall_global_int(GV_RAID_WATER))) then begin
      set_sfall_global(GV_SET_FOOD, get_sfall_global_int(GV_SET_FOOD) + get_sfall_global_int(GV_RAID_FOOD));
      set_sfall_global(GV_SET_WATER, get_sfall_global_int(GV_SET_WATER) + get_sfall_global_int(GV_RAID_WATER));
      display_msg(lair_msg(213) + get_sfall_global_int(GV_RAID_FOOD) + lair_msg(214) + get_sfall_global_int(GV_RAID_WATER) + lair_msg(215));
      set_sfall_global(GV_RAID_FOOD, 0);
      set_sfall_global(GV_RAID_WATER, 0);
   end
end

// Банда уходит из карьера (мир или взрыв): живые исчезают, трупы остаются. keep — тот, чей скрипт сейчас работает
procedure lair_gang_leave(variable keep) begin
   variable c;
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (c != keep and is_gang(c) and not is_critter_dead(c)) then destroy_object(c);
   end
end

#endif
