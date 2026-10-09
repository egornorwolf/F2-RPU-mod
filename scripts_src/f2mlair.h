// Логово налетчиков в карьере (квест 1.4, quests-detailed.md) и военная база на его месте (1.5, military-base.md).
// Карта f2mlair (копия горной карты mountn5), точки на ней — f2mlairl.h (tools/layout/lair_emit.py).
// Тексты — f2mlair.msg (скрипт карты логова). Подключать после define.h, command.h, sfall.h, f2mod.h, f2mcv.h,
// f2mcamp.h, f2mset.h (в нем f2mbld.h), f2mpay.h и f2mraid.h.
#ifndef F2MLAIR_H
#define F2MLAIR_H
#include "f2mlairl.h"   // точки на карте логова: LAIR_CELLAR и прочие

#define GV_LAIR         "f2mlairs"  // 0 неизвестно, 1 герой знает, где логово (кружок на карте), 2 логово взято
#define GV_LAIR_HOW     "f2mlairh"  // как взято: LAIR_HOW_* ниже
#define GV_LAIR_PASS    "f2mlairp"  // 1 = часовой пропустил к главарю
#define GV_LAIR_ALARM   "f2mlaira"  // 1 = банда воюет с героем
#define GV_LAIR_POISON  "f2mlairx"  // 1 = вода отравлена
#define GV_LAIR_CELLAR  "f2mlairc"  // 1 погреб найден, 2 взорван
#define GV_LAIR_PUT     "f2mlairg"  // 1 = банда и предметы уже на карте
#define GV_LAIR_TRACK   "f2mlairt"  // час, когда Рик расскажет, где логово (банда ушла от ворот)
#define GV_LAIR_DYN     "f2mlaird"  // 1 = ящик с динамитом уже поставлен (0.8.1 наверху, с 0.8.3 внизу, в погребе)
#define GV_BASE_GARR    "f2mbgarr"  // сколько бойцов гарнизона живет на базе (едят из запасов поселения)
#define GV_CELL_PUT     "f2mcellg"  // 1 = погреб обставлен (охрана, запасы, динамит)
#define GV_CELL_GANG    "f2mcelln"  // живых охранников банды в погребе
#define GV_LAIR_GANG    "f2mlairn"  // живых бандитов наверху, в карьере
#define GV_CELL_BACK    "f2mcellb"  // 1 = герой поднимается из погреба: поставить его у лаза
#define GV_CELL_CHARGE  "f2mcellc"  // 1 = заряд заложен в запасы, рванет, когда герой выберется наверх
#define GV_CELL_RUIN    "f2mcellx"  // 1 = последствия взрыва в погребе уже показаны (охрана мертва, запасы под завалом)
#define GV_REMN_KANE    "f2mremkn"  // 1 = Кейн ушел из карьера живым: он вожак остатков банды (1.4б)
#define GV_REMN_MEN     "f2mremnn"  // сколько бойцов банды ушло из карьера живыми (с вожаком)
#define GV_CELL_LOOT    "f2mcellt"  // час, когда герой впервые ушел из погреба, обобрав трупы (через неделю они пропадут)
#define GV_LAIR_BRIBE   "f2mlairb"  // 1 = Кейна откупили 1000 крышек (для реплики остатков банды, 1.4б)
#define GV_LAIR_FIN     "f2mlairf"  // час, когда логово взято (через два месяца после взрыва — остатки банды)

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
#define PID_LAIR_CELLAR (33555705)  // Pile of Rocks (камни над лазом в погреб, пока лаз не найден)
#define PID_CELL_HOLE   (33555015)  // hole1: дыра с лестницей вниз (как люк в доме героя, Егор 2026-10-08)
#define PID_CELL_LADDER (33554571)  // Ladder: лестница из погреба наверх
#define PID_CELL_STACK  (33554652)  // Boxes: штабель запасов банды в погребе (сюда закладывают заряд)
#define CELL_GUARDS     (2)         // охрана погреба (из тех же LAIR_GANG бойцов)
#define LAIR_OLD_CRATE  (18702)     // 102, 93: ящик со скриптом случайной встречи из mountn5, убираем
#define U_BASE          (U_BASE_UNIT)   // военная база в f2mbld.h (вне U_COUNT: на карту лагеря не ставится)
#define BASE_TOP_LEVEL  (3)         // 4-й уровень (штаб) — по квесту, позже

#define lair_msg(n)     message_str(SCRIPT_F2MLAIR, n)
#define lair_done       (get_sfall_global_int(GV_LAIR) >= LAIR_DONE)
#define lair_kane_dead  (get_sfall_global_int(GV_BOSS_NOTE) != 0)   // убит у ворот и обыскан (героем или Риком)
#define base_level      (bld_level(U_BASE))
// Взорванный погреб открыт снова (Егор 2026-10-09): Хэнк расчистил (срок вышел), герой раскопал лопатой или построена база
#define cell_open       ((get_sfall_global_int(GV_CELL_OPEN) and bld_hour + 1 >= get_sfall_global_int(GV_CELL_OPEN)) or base_level >= 1)
#define base_cap(lv)    ((lv >= 1) * (4 + 2 * (lv)))                // гарнизон 6 / 8 / 10

procedure lair_reveal(variable msg);
procedure lair_tick;
procedure lair_gang_alive(variable except);
procedure lair_seen(variable who);
procedure lair_alarm;
procedure lair_finish(variable how);
procedure lair_gang_leave(variable keep);
procedure lair_cellar_face;
procedure lair_gang_fall(variable except);

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
   set_sfall_global(GV_LAIR_FIN, bld_hour);
   set_sfall_global(GV_LAIR_ALARM, 0);
   set_sfall_global(GV_LAIR_GANG, 0);
   set_sfall_global(GV_CELL_GANG, 0);
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

// Что лежит на месте лаза в погреб: пока лаз не нашли (и после взрыва) — куча камней,
// найденный лаз — дыра с лестницей вниз (как люк в доме героя). После взрыва лаз завален, пока его не расчистят
// (cell_open: Хэнк, лопата героя или военная база, Егор 2026-10-09). Зовут карта логова и глобальный скрипт
procedure lair_cellar_face begin
   variable rocks, hole, c;
   rocks := tile_contains_pid_obj(LAIR_CELLAR, 0, PID_LAIR_CELLAR);
   hole := tile_contains_pid_obj(LAIR_CELLAR, 0, PID_CELL_HOLE);
   c := get_sfall_global_int(GV_LAIR_CELLAR);
   if (c == 1 or (c == 2 and cell_open)) then begin
      if (rocks) then destroy_object(rocks);
      if (not hole) then create_object_sid(PID_CELL_HOLE, LAIR_CELLAR, 0, SCRIPT_F2MLOBJ);
   end else begin
      if (hole) then destroy_object(hole);
      if (not rocks) then create_object_sid(PID_LAIR_CELLAR, LAIR_CELLAR, 0, SCRIPT_F2MLOBJ);
   end
end

// Пал боец банды: считаем живых на этой карте и помним, сколько осталось на другой (карьер и погреб).
// Логово взято боем, только когда не осталось никого ни наверху, ни внизу
procedure lair_gang_fall(variable except) begin
   variable n;
   if (lair_done or not get_sfall_global_int(GV_LAIR_ALARM)) then return;
   n := lair_gang_alive(except);
   if (cur_map_index == MAP_F2MOD_CELL) then set_sfall_global(GV_CELL_GANG, n);
   else set_sfall_global(GV_LAIR_GANG, n);
   if (get_sfall_global_int(GV_CELL_GANG) == 0 and get_sfall_global_int(GV_LAIR_GANG) == 0) then
      call lair_finish(LAIR_HOW_FIGHT);
end

// Банда уходит из карьера (мир или взрыв): живые исчезают, трупы остаются. keep — тот, чей скрипт сейчас работает
procedure lair_gang_leave(variable keep) begin
   variable c, n := 0, kane := 0;
   // Кто ушел живым (Егор 2026-10-09): через пару месяцев они встретятся в пустыне (1.4б, f2mremn.h)
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (is_gang(c) and not is_critter_dead(c)) then begin
         n += 1;
         if ((obj_art_fid(c) bwand 0xFFF) == GANG_ART_BOSS) then kane := 1;
      end
   end
   if (get_sfall_global_int(GV_LAIR_CELLAR) != 2) then n += get_sfall_global_int(GV_CELL_GANG);   // сторожа погреба уходят с бандой
   set_sfall_global(GV_REMN_MEN, n);
   set_sfall_global(GV_REMN_KANE, kane);
   foreach (c in list_as_array(LIST_CRITTERS)) begin
      if (c != keep and is_gang(c) and not is_critter_dead(c)) then destroy_object(c);
   end
end

#endif
