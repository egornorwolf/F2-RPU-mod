// Кто из каравана погиб в пути. Каждому месту в караване свой бит в GV_CARAVAN_DEAD:
// 0 охранник, 1 охранница Сара, 2–3 брамины, 4–13 мирные (порядок как в cv_civilians).
// Погибший на одном участке дороги на следующих уже не появляется.
// Подключать после define.h, sfall.h и f2mod.h.
#ifndef F2MCDEAD_H
#define F2MCDEAD_H

#define CV_SLOT_GUARD       (0)
#define CV_SLOT_SARA        (1)
#define CV_SLOT_BRAHMIN     (2)     // 2 и 3
#define CV_SLOT_CIV         (4)     // 4..13
#define CV_SLOTS            (14)

procedure cv_bit(variable i);
procedure cv_slot_pid(variable i);
procedure cv_is_dead(variable i);
procedure cv_set_dead(variable i);
procedure cv_mark_dead(variable pid);
procedure cv_civs_alive;

// 2 в степени i (в SSL нет сдвига)
procedure cv_bit(variable i) begin
   variable b := 1;
   while (i > 0) do begin
      b := b * 2;
      i -= 1;
   end
   return b;
end

procedure cv_slot_pid(variable i) begin
   if (i == 0) then return PID_GUN_GUARD_MALE;
   if (i == 1) then return PID_GUN_GUARD_FEMALE;
   if (i == 2 or i == 3) then return PID_BRAHMIN;
   // Мирные: 3 мужчины, 4 женщины, 3 ребенка
   if (i == 4 or i == 11) then return PID_WEAK_PEASANT_MALE;
   if (i == 5 or i == 10) then return PID_AVERAGE_PEASANT_FEMALE;
   if (i == 6 or i == 13) then return PID_CHILD_MALE;
   if (i == 7) then return PID_AVERAGE_PEASANT_MALE;
   if (i == 8 or i == 12) then return PID_WEAK_PEASANT_FEMALE;
   if (i == 9) then return PID_CHILD_FEMALE;
   return 0;
end

procedure cv_is_dead(variable i) begin
   return (get_sfall_global_int(GV_CARAVAN_DEAD) bwand cv_bit(i)) != 0;
end

procedure cv_set_dead(variable i) begin
   set_sfall_global(GV_CARAVAN_DEAD, get_sfall_global_int(GV_CARAVAN_DEAD) bwor cv_bit(i));
end

// Погиб кто-то из каравана на дороге: отмечаем первое живое место с таким же видом
// (одинаковые переселенцы взаимозаменяемы, важно только сколько их осталось)
procedure cv_mark_dead(variable pid) begin
   variable i := 0;
   if (not is_escort_map(cur_map_index)) then return;
   while (i < CV_SLOTS) do begin
      if (cv_slot_pid(i) == pid and not cv_is_dead(i)) then begin
         call cv_set_dead(i);
         return;
      end
      i += 1;
   end
end

// Сколько мирных еще живы
procedure cv_civs_alive begin
   variable i := 0, n := 0;
   while (i < 10) do begin
      if (not cv_is_dead(CV_SLOT_CIV + i)) then n += 1;
      i += 1;
   end
   return n;
end

#endif
