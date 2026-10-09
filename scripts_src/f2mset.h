// Поселение (М4): недельный тик — еда, вода, касса, боевой дух, уход и возврат жителей.
// Правила: docs/design.md 5.2 (паек в неделю), economy.md (касса, докупка, излишки),
// growth.md 13 (боевой дух), quests-detailed.md 1.2 (без воды) и 1.7 (поселение брошено).
// Подключать после define.h, sfall.h, f2mod.h, f2mcdead.h и f2mcamp.h.
#ifndef F2MSET_H
#define F2MSET_H

#include "f2mbld.h"   // уровни зданий: вода, еда и дух от построек (0.7.0)

#define GV_SET_WEEK     "f2msweek"  // сколько недель с основания уже посчитано
#define GV_SET_FOOD     "f2msfood"  // запас еды, пайков
#define GV_SET_WATER    "f2mswatr"  // запас воды, пайков (паек = 21 л: 3 л в день)
#define GV_SET_CASH     "f2mscash"  // касса поселения у старосты
#define GV_SET_MORALE   "f2msmorl"  // боевой дух, % (от -50 до +50)
#define GV_SET_FSHORT   "f2msfsht"  // недель подряд без еды (не хватило и в кассе)
#define GV_SET_WSHORT   "f2mswsht"  // недель подряд без воды
#define GV_SET_ABANDON  "f2msaban"  // поселение брошено (1.7): ABANDON_* ниже
#define GV_SET_RETURN   "f2msretw"  // неделя, к которой люди вернутся (после уговора Теда)
#define GV_SET_NOLEAVE  "f2msnolv"  // 1 = люди привезены без колодца: без воды не уходят, только дух падает
#define GV_SET_NEWS     "f2msnews"  // Тед скажет при встрече: 1 люди ушли, 2 люди вернулись
#define GV_SET_HALF     "f2mshalf"  // 1 = Тед уговорен (Красноречие 60%): вернуть людей за полцены
#define GV_SET_SYNC     "f2mssync"  // 1 = люди ушли или вернулись, карта лагеря еще не обновлена
#define GV_SET_INIT     "f2msinit"  // 1 = запасы заведены (лагерь из сохранения до 0.4.0 заводится с текущей недели)
#define GV_SET_MILIT    "f2msmilt"  // сколько ополченцев (наняты у Рика и бывшие налетчики) живы: живут у поста охраны и едят
// Сколько охраны нанимает Рик (guards.md 1, Егор: «мы не Город-Убежище»): 4, караулка (3 ур.) 6, казарма (4 ур.) 8.
// Хижины ополчение не занимает, за места штрафов нет: бывшие налетчики (1.4б) приходят сверх лимита и спят посменно
#define milit_cap       (4 + 2 * (bld_shown(U_GUARD) >= 3) + 2 * (bld_shown(U_GUARD) >= 4))
#define milit_free      (milit_cap - get_sfall_global_int(GV_SET_MILIT))
#define GV_SET_ANGRY    "f2msangr"  // до какого часа игры люди злы после набега: дух -10% (1.3, забор; неделя)
#define GV_SET_MBONUS   "f2msmbon"  // постоянная прибавка к духу, % (1.3: похоронили погибшего +5)

#define ABANDON_NO       (0)
#define ABANDON_YES      (1)
#define ABANDON_RETURN   (2)    // уговорились, люди в пути

#define SET_START_WEEKS  (2)    // еды и воды каравана на 2 недели (1.2: «воды в бочках недели на две»)
#define SET_WELL_WATER   (10)   // колодец: +10 пайков воды в неделю (design.md 5.2)
#define SET_GARDEN_FOOD  (5)    // огород: +5 пайков еды в неделю
#define SET_FOOD_PRICE   (10)   // докупка еды: 10 за паек
#define SET_WATER_PRICE  (21)   // вода у каравана: 1 крышка за литр, 21 л на паек (1.2)
#define SET_SURPLUS      (5)    // излишки староста продает караванам: 5 за паек
#define SET_KEEP_WEEKS   (2)    // запас сверх двух недель продается
#define MORALE_TENTS     (-20)  // до 0.7.0: живут в палатках (growth.md 13); теперь дух жилья по уровням, f2mbld.h
#define RETURN_PRICE     (1000) // 1.7: колодец и тысяча на дорогу
#define RETURN_PRICE_CH  (500)  // 1.7: Красноречие 60% — полцены
#define RETURN_SPEECH    (60)
#define RETURN_CARAVAN   (1500) // 1.7: караван привозит людей без колодца
#define RETURN_WEEKS     (2)    // люди приходят через 2 недели

procedure set_founded;
procedure set_weeks_now;
procedure set_gone(variable slot);
procedure set_here(variable slot);
procedure set_civs_here;
procedure set_people;
procedure set_wells;
procedure set_gardens;
procedure set_food_prod;
procedure set_short_morale(variable fs, variable ws);
procedure set_init;
procedure set_leave_half;
procedure set_abandon;
procedure set_people_return;
procedure set_resource(variable stock_gv, variable short_gv, variable prod, variable need, variable price);
procedure set_tick(variable week);
procedure set_tick_all;

procedure set_founded begin
   return get_sfall_global_int(GV_CAMP_LAYOUT) != 0;
end

// Полных недель с основания лагеря
procedure set_weeks_now begin
   if (not set_founded) then return 0;
   return camp_days / 7;
end

procedure set_gone(variable slot) begin
   return (get_sfall_global_int(GV_SET_GONE) bwand cv_bit(slot)) != 0;
end

// Живет в лагере: не погиб и не ушел
procedure set_here(variable slot) begin
   return not cv_is_dead(slot) and not set_gone(slot);
end

procedure set_civs_here begin
   variable i := 0, n := 0;
   while (i < 10) do begin
      if (set_here(CV_SLOT_CIV + i)) then n += 1;
      i += 1;
   end
   return n;
end

// Едят все: Тед, Хэнк, охрана, ополченцы, переселенцы, радист и гарнизон базы (f2msam.h: "f2msamst" 1-3 — живет в лагере)
procedure set_people begin
   variable sam;
   sam := get_sfall_global_int("f2msamst");
   return 2 + set_here(CV_SLOT_GUARD) + set_here(CV_SLOT_SARA) + set_civs_here + get_sfall_global_int(GV_SET_MILIT)
      + (sam >= 1 and sam <= 3) + (get_sfall_global_int("f2mfarst") == 1)   // радист и старший фермер
      + get_sfall_global_int("f2mbgarr");   // гарнизон базы (f2mlair.h)
end

procedure set_wells begin
   return (get_sfall_global_int(GV_WELL_OLD) == WELL_OLD_FIXED) + camp_built(BUILD_WELL);
end

procedure set_gardens begin
   return camp_built(BUILD_GARDEN) + camp_built(BUILD_GARDEN + 1);
end

// Огороды и брамины — работа жителей: умножается на дух (growth.md 13). Колодцы дают воду без людей.
// Сколько дает каждый уровень здания — f2mbld.h (0.7.0)
procedure set_food_prod begin
   return bld_food * (100 + get_sfall_global_int(GV_SET_MORALE)) / 100;
end

// Дух: жилье и бар (f2mbld.h: палатка -10%, шатер 0%, бар +5%) и нехватка (еда: -10%, со второй недели -25%; вода: -25%);
// после набега (1.3): злы на неделю -10%, похоронили погибшего +5% навсегда
procedure set_short_morale(variable fs, variable ws) begin
   variable m := bld_morale;   // жилье по уровням и бар (0.7.0; до него палатки -20)
   m += get_sfall_global_int(GV_SET_MBONUS);
   if (game_time / ONE_GAME_HOUR < get_sfall_global_int(GV_SET_ANGRY)) then m -= 10;
   if (fs == 1) then m -= 10;
   else if (fs >= 2) then m -= 25;
   if (ws >= 1) then m -= 25;
   if (m < -50) then m := -50;
   if (m > 50) then m := 50;
   set_sfall_global(GV_SET_MORALE, m);
end

// Первый раз: запасы каравана на 2 недели, касса пустая
procedure set_init begin
   variable n;
   n := set_people;
   set_sfall_global(GV_SET_WEEK, 0);
   set_sfall_global(GV_SET_FOOD, n * SET_START_WEEKS);
   set_sfall_global(GV_SET_WATER, n * SET_START_WEEKS);
   set_sfall_global(GV_SET_CASH, 0);
   call set_short_morale(0, 0);
end

// Уходит половина переселенцев (с конца списка)
procedure set_leave_half begin
   variable i := 9, n;
   n := set_civs_here / 2;
   while (i >= 0 and n > 0) do begin
      if (set_here(CV_SLOT_CIV + i)) then begin
         set_sfall_global(GV_SET_GONE, get_sfall_global_int(GV_SET_GONE) bwor cv_bit(CV_SLOT_CIV + i));
         n -= 1;
      end
      i -= 1;
   end
end

// 1.7: уходят все, кроме Теда, Хэнка и одного охранника. Запасы и касса пропадают.
procedure set_abandon begin
   variable i := 0;
   while (i < 10) do begin
      if (not cv_is_dead(CV_SLOT_CIV + i)) then
         set_sfall_global(GV_SET_GONE, get_sfall_global_int(GV_SET_GONE) bwor cv_bit(CV_SLOT_CIV + i));
      i += 1;
   end
   if (set_here(CV_SLOT_GUARD) and set_here(CV_SLOT_SARA)) then
      set_sfall_global(GV_SET_GONE, get_sfall_global_int(GV_SET_GONE) bwor cv_bit(CV_SLOT_SARA));
   set_sfall_global(GV_SET_ABANDON, ABANDON_YES);
   set_sfall_global(GV_SET_FOOD, 0);
   set_sfall_global(GV_SET_WATER, 0);
   set_sfall_global(GV_SET_CASH, 0);
end

// Люди вернулись (1.7): все, кто жив, снова в лагере. Еды и воды приносят с собой на 2 недели,
// как первый караван (иначе без запаса снова ушли бы в ту же неделю).
procedure set_people_return begin
   set_sfall_global(GV_SET_GONE, 0);
   set_sfall_global(GV_SET_FOOD, set_people * SET_START_WEEKS);
   set_sfall_global(GV_SET_WATER, set_people * SET_START_WEEKS);
   set_sfall_global(GV_SET_ABANDON, ABANDON_NO);
   set_sfall_global(GV_SET_WSHORT, 0);
   set_sfall_global(GV_SET_FSHORT, 0);
end

// Одна статья (еда или вода) за неделю: запас + производство - едоки; нехватку докупает
// староста из кассы, излишек сверх двух недель продает. Возвращает, сколько потрачено из кассы.
procedure set_resource(variable stock_gv, variable short_gv, variable prod, variable need, variable price) begin
   variable have, buy, cash, spent := 0, keep;
   have := get_sfall_global_int(stock_gv) + prod;
   cash := get_sfall_global_int(GV_SET_CASH);
   if (have >= need) then begin
      have -= need;
      set_sfall_global(short_gv, 0);
      keep := need * SET_KEEP_WEEKS;
      if (have > keep) then begin
         cash += (have - keep) * SET_SURPLUS;
         spent -= (have - keep) * SET_SURPLUS;
         have := keep;
      end
   end else begin
      buy := need - have;
      if (buy * price > cash) then buy := cash / price;
      cash -= buy * price;
      spent := buy * price;
      if (have + buy < need) then
         set_sfall_global(short_gv, get_sfall_global_int(short_gv) + 1);
      else
         set_sfall_global(short_gv, 0);
      have := 0;
   end
   set_sfall_global(stock_gv, have);
   set_sfall_global(GV_SET_CASH, cash);
   return spent;
end

// Одна неделя. Итог в окно сообщений (видно и вдали от лагеря).
procedure set_tick(variable week) begin
   variable n, food, water, fspent, wspent, fs, ws, cash0, msg;
   n := set_people;
   food := set_food_prod;
   water := bld_water;
   cash0 := get_sfall_global_int(GV_SET_CASH);
   fspent := set_resource(GV_SET_FOOD, GV_SET_FSHORT, food, n, SET_FOOD_PRICE);
   wspent := set_resource(GV_SET_WATER, GV_SET_WSHORT, water, n, SET_WATER_PRICE);
   fs := get_sfall_global_int(GV_SET_FSHORT);
   ws := get_sfall_global_int(GV_SET_WSHORT);
   msg := "Скалистый приют, неделя " + week + ": людей " + n + ", еда +" + food + " (запас " + get_sfall_global_int(GV_SET_FOOD)
      + "), вода +" + water + " (запас " + get_sfall_global_int(GV_SET_WATER) + "), касса " + cash0 + " -> " + get_sfall_global_int(GV_SET_CASH) + ".";
   display_msg(msg);

   // Брошенный лагерь: оставшимся некуда идти, считаем только еду и воду
   if (ws == 0) then set_sfall_global(GV_SET_NOLEAVE, 0);
   if (get_sfall_global_int(GV_SET_ABANDON) != ABANDON_NO) then begin
      call set_short_morale(fs, ws);
      return;
   end
   if (ws >= 1 and not get_sfall_global_int(GV_SET_NOLEAVE)) then begin
      if (ws == 1) then begin
         call set_leave_half;
         set_sfall_global(GV_SET_NEWS, 1);
         set_sfall_global(GV_SET_SYNC, 1);
         display_msg("Нечем пить: половина переселенцев собрала вещи и ушла. Дух -25%.");
      end else begin
         call set_abandon;
         set_sfall_global(GV_SET_NEWS, 1);
         set_sfall_global(GV_SET_SYNC, 1);
         display_msg("Лагерь брошен: люди ушли. Остались Тед, Хэнк и один охранник.");
      end
   end else if (fs == 3) then begin
      call set_leave_half;
      set_sfall_global(GV_SET_NEWS, 1);
         set_sfall_global(GV_SET_SYNC, 1);
      display_msg("Третью неделю нечего есть: половина переселенцев ушла.");
   end
   if (ws >= 1) then display_msg("Воды не хватает, денег в кассе на нее нет.");
   else if (fs >= 1) then display_msg("Еды не хватает, денег в кассе на нее нет.");
   call set_short_morale(fs, ws);
end

// Догоняем все прошедшие недели (герой мог быть далеко). Возврат людей после уговора Теда.
procedure set_tick_all begin
   variable now, w;
   if (not set_founded) then return;
   now := set_weeks_now;
   if (not get_sfall_global_int(GV_SET_INIT)) then begin
      set_sfall_global(GV_SET_INIT, 1);
      call set_init;
      set_sfall_global(GV_SET_WEEK, now);
      return;
   end
   w := get_sfall_global_int(GV_SET_WEEK);
   while (w < now) do begin
      w += 1;
      set_sfall_global(GV_SET_WEEK, w);
      if (get_sfall_global_int(GV_SET_ABANDON) == ABANDON_RETURN and w >= get_sfall_global_int(GV_SET_RETURN)) then begin
         call set_people_return;
         set_sfall_global(GV_SET_NEWS, 2);
         set_sfall_global(GV_SET_SYNC, 1);
         display_msg("Люди вернулись в Скалистый приют.");
      end
      call set_tick(w);
   end
end

#endif
