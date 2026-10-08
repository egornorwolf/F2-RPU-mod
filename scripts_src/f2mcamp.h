// Лагерь у скал: общее для карты лагеря, прораба, колодцев и старосты.
// Подключать после define.h, sfall.h, f2mod.h и f2mcdead.h (нужен cv_bit).
#ifndef F2MCAMP_H
#define F2MCAMP_H

#define BUILD_WELL      (0)     // новый колодец
#define BUILD_GARDEN    (1)     // 1 и 2 — огороды
#define BUILD_TENT      (3)     // 3..6 — палатки
#define BUILD_COUNT     (7)

#define PID_WELL_OLD    (33555425)  // MODWELL1: заколоченный колодец
#define PID_WELL_FIXED  (33556410)  // WELL001 (RPU): тот же колодец, открытый
#define PID_WELL_NEW    (33554815)  // well1: колодец с воротом

procedure camp_built(variable slot);
procedure camp_set_built(variable slot);
procedure camp_has_water;
procedure camp_water_done(variable text);
procedure camp_days;

procedure camp_built(variable slot) begin
   return (get_sfall_global_int(GV_CAMP_BUILT) bwand cv_bit(slot)) != 0;
end

procedure camp_set_built(variable slot) begin
   set_sfall_global(GV_CAMP_BUILT, get_sfall_global_int(GV_CAMP_BUILT) bwor cv_bit(slot));
end

// Есть рабочий колодец: старый починен или прораб выкопал новый
procedure camp_has_water begin
   return (get_sfall_global_int(GV_WELL_OLD) == WELL_OLD_FIXED) or camp_built(BUILD_WELL);
end

// Первый рабочий колодец закрывает квест «Вода»: опыт один раз
procedure camp_water_done(variable text) begin
   if (get_sfall_global_int(GV_QUEST_WATER) == 2) then return;
   set_sfall_global(GV_QUEST_WATER, 2);
   give_exp_points(WATER_XP);
   display_msg(text);
end

// Сколько полных суток прошло с основания лагеря
procedure camp_days begin
   return (game_time / ONE_GAME_HOUR - get_sfall_global_int(GV_CAMP_DAY)) / 24;
end

#endif
