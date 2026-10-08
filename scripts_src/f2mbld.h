// Уровни зданий поселения (0.7.0): какой уровень у здания, стройки Хэнка (две бригады), цены и сроки, что дает уровень.
// Цены и сроки — сводная таблица docs/buildings-levels.md (с наценкой прораба +25%, караван 1).
// Объекты на карте ставит f2mlvl.h (только карта лагеря и Хэнк); тут только числа, их читают все.
// Подключать после define.h, sfall.h, f2mod.h, f2mcdead.h и f2mcamp.h.
#ifndef F2MBLD_H
#define F2MBLD_H

// Здания (номера как в tools/layout/levels_emit.py)
#define U_OLDWELL       (0)
#define U_NEWWELL       (1)
#define U_GARDEN        (2)     // 2-3 огороды (места прораба 1-2)
#define U_HOUSE         (4)     // 4-11 дома: 4-6 палатки основания, 7-11 палатки прораба (места 3-7)
#define U_STORE         (12)
#define U_CENTRE        (13)
#define U_WORKSHOP      (14)
#define U_GUARD         (15)
#define U_FARM          (16)
#define U_BAR           (17)
#define U_MED           (18)
#define U_HERO          (19)
#define U_COUNT         (20)
#define U_TOP_LEVEL     (2)     // 0.7.0: строим до 2-го уровня (3-й — с караваном 2, 4-й — после квестов)
#define U_BASE_UNIT     (20)    // военная база в карьере (1.5): строит та же бригада, на карте лагеря ее нет
#define bld_top(u)      (((u) == U_BASE_UNIT) * 3 + ((u) != U_BASE_UNIT) * U_TOP_LEVEL)
// Названия и описания уровней — в f2mcfrm.msg: здания 600 + u * 5 + lv и 700 + u * 5 + lv, база 452 + lv и 456 + lv
#define bld_name(u, lv) (((u) == U_BASE_UNIT) * (452 + (lv)) + ((u) != U_BASE_UNIT) * (600 + (u) * 5 + (lv)))
#define bld_desc(u, lv) (((u) == U_BASE_UNIT) * (456 + (lv)) + ((u) != U_BASE_UNIT) * (700 + (u) * 5 + (lv)))

#define BLD_JOBS        (2)     // бригад у Хэнка: две стройки сразу (третья — мастерская 3 уровня)
#define BLD_BATCH       (1000)  // бригада строит шатры вместо всех палаток разом: здание = BLD_BATCH + биты мест 0-7
#define BLD_BATCH_HOURS (36)    // 4 дома одним заказом за полтора срока одного (map-plan.md, раздел 8)
#define BLD_HELP_STAT   (5)     // помочь на стройке 1-го уровня: Сила и Выносливость
#define BLD_HELP_XP     (25)
#define BLD_HELP_PCT    (70)    // 2-й уровень своими руками: цена 70%, ждать на месте до конца
#define BLD_HELP_XP2    (50)
#define GV_BLD_SYNC     "f2mbsync"  // 1 = достроено, а на карте еще прежний уровень (Хэнк или карта лагеря поставят)

#define GV_JOB_U(j)     ("f2mjobu" + (j))   // бригада j: здание + 1 (0 — свободна)
#define GV_JOB_L(j)     ("f2mjobl" + (j))   // какой уровень строит
#define GV_JOB_H(j)     ("f2mjobh" + (j))   // час игры, когда закончит
// Костер: на 2-м уровне центра шатер старосты встает на место стола, костер — перед шатром.
// Клетку проверяет tools/layout/levels_emit.py (там же LVL_FIRE2 в f2mlvl.h)
#define BLD_FIRE2       (18480)     // x 80, y 92
// Радио у старосты (радист, 0.7.1): стол ltable2 с пультом comp5 и место радиста; клетки проверяет levels_emit.py
#define BLD_RADIO       (17681)     // x 81, y 88
#define BLD_SAM         (17482)     // x 82, y 87
#define PID_RTABLE      (33554926)  // ltable2
#define PID_RCOMP       (33554487)  // comp5
#define camp_fire       ((bld_shown(U_CENTRE) >= 2) * BLD_FIRE2 + (bld_shown(U_CENTRE) < 2) * LAY_FIRE)
#define bld_gv(pre, u)          ((pre) + ((u) / 10) + ((u) % 10))
#define bld_house_unit(slot)    (U_HOUSE + (slot))   // дом по месту палатки 0-7 (0-2 основание, 3-7 прораб)
#define bld_unit_slot(u)        ((u) - U_HOUSE)
#define bld_is_house(u)         ((u) >= U_HOUSE and (u) < U_HOUSE + 8)
#define bld_hour                (game_time / ONE_GAME_HOUR)

procedure bld_base(variable u);
procedure bld_level(variable u);
procedure bld_set_level(variable u, variable lv);
procedure bld_shown(variable u);
procedure bld_set_shown(variable u, variable lv);
procedure bld_price(variable u, variable lv);
procedure bld_hours(variable u, variable lv);
procedure bld_job_of(variable u);
procedure bld_job_free;
procedure bld_job_start(variable u, variable lv, variable hours);
procedure bld_job_left(variable j);
procedure bld_commit;
procedure bld_water;
procedure bld_food;
procedure bld_morale;

// Уровень, который был до 0.7.0 (без записи): что уже поставлено старым кодом лагеря
procedure bld_base(variable u) begin
   if (u == U_OLDWELL) then return get_sfall_global_int(GV_WELL_OLD) == WELL_OLD_FIXED;
   if (u == U_NEWWELL) then return camp_built(BUILD_WELL);
   if (u == U_GARDEN or u == U_GARDEN + 1) then return camp_built(BUILD_GARDEN + u - U_GARDEN);
   if (bld_is_house(u)) then begin
      if (bld_unit_slot(u) < BUILD_TENT) then return 1;
      return camp_built(bld_unit_slot(u));
   end
   if (u == U_HERO) then return camp_built(BUILD_HERO);
   if (u == U_STORE or u == U_CENTRE or u == U_FARM) then return 1;   // повозки, костер со столом, брамины каравана
   return 0;   // мастерская, пост охраны, бар, медпункт: строит Хэнк
end

procedure bld_level(variable u) begin
   variable v;
   v := get_sfall_global_int(bld_gv("f2mlvl", u));
   if (v > 0) then return v;
   return bld_base(u);
end

procedure bld_set_level(variable u, variable lv) begin
   set_sfall_global(bld_gv("f2mlvl", u), lv);
end

// Какой уровень стоит на карте сейчас
procedure bld_shown(variable u) begin
   variable v;
   v := get_sfall_global_int(bld_gv("f2mshw", u));
   if (v > 0) then return v;
   return bld_base(u);
end

procedure bld_set_shown(variable u, variable lv) begin
   set_sfall_global(bld_gv("f2mshw", u), lv);
end

// Цена уровня, крышки (таблица в buildings-levels.md)
procedure bld_price(variable u, variable lv) begin
   if (u == U_BASE_UNIT) then return lv * 1000;   // база: 1000 / 2000 / 3000 (military-base.md)
   if (lv == 1) then begin
      if (u == U_WORKSHOP or u == U_GUARD) then return 20;
      if (u == U_BAR or u == U_MED) then return 30;
      return 0;
   end
   if (u == U_OLDWELL or u == U_NEWWELL or u == U_STORE or u == U_GUARD or u == U_BAR) then return 150;
   if (u == U_GARDEN or u == U_GARDEN + 1 or bld_is_house(u) or u == U_CENTRE) then return 100;
   if (u == U_WORKSHOP or u == U_FARM or u == U_MED) then return 200;
   if (u == U_HERO) then return 400;
   return 0;
end

// Срок, часы: 1-й уровень несколько часов, 2-й день (дом героя два)
procedure bld_hours(variable u, variable lv) begin
   if (u == U_BASE_UNIT) then return (lv + 1) * 24;   // база: 2 / 3 / 4 дня
   if (lv == 1) then return 3;
   if (u == U_HERO) then return 48;
   return 24;
end

// Какая бригада строит здание (1-2), 0 — никакая
procedure bld_job_of(variable u) begin
   variable j := 1, v;
   while (j <= BLD_JOBS) do begin
      v := get_sfall_global_int(GV_JOB_U(j));
      if (v == u + 1) then return j;
      if (v > BLD_BATCH and bld_is_house(u)) then begin
         if ((v - BLD_BATCH) bwand cv_bit(bld_unit_slot(u))) then return j;
      end
      j += 1;
   end
   return 0;
end

procedure bld_job_free begin
   variable j := 1;
   while (j <= BLD_JOBS) do begin
      if (not get_sfall_global_int(GV_JOB_U(j))) then return j;
      j += 1;
   end
   return 0;
end

procedure bld_job_start(variable u, variable lv, variable hours) begin
   variable j;
   j := bld_job_free;
   if (not j) then return 0;
   set_sfall_global(GV_JOB_U(j), u + 1);
   set_sfall_global(GV_JOB_L(j), lv);
   set_sfall_global(GV_JOB_H(j), bld_hour + hours);
   return j;
end

// Сколько часов осталось бригаде j
procedure bld_job_left(variable j) begin
   variable h;
   h := get_sfall_global_int(GV_JOB_H(j)) - bld_hour;
   if (h < 0) then return 0;
   return h;
end

// Стройки, у которых вышел срок: здание получает уровень, бригада свободна. Возвращает, сколько достроено
procedure bld_commit begin
   variable j := 1, u, n := 0, i;
   while (j <= BLD_JOBS) do begin
      u := get_sfall_global_int(GV_JOB_U(j));
      if (u and bld_hour >= get_sfall_global_int(GV_JOB_H(j))) then begin
         set_sfall_global(GV_JOB_U(j), 0);
         set_sfall_global(GV_BLD_SYNC, 1);
         if (u > BLD_BATCH) then begin
            i := 0;
            while (i < 8) do begin
               if ((u - BLD_BATCH) bwand cv_bit(i)) then call bld_set_level(bld_house_unit(i), 2);
               i += 1;
            end
            display_msg(message_str(SCRIPT_F2MCFRM, 590) + message_str(SCRIPT_F2MCFRM, 446) + ".");
         end else begin
            u -= 1;
            call bld_set_level(u, get_sfall_global_int(GV_JOB_L(j)));
            display_msg(message_str(SCRIPT_F2MCFRM, 590) + message_str(SCRIPT_F2MCFRM, bld_name(u, get_sfall_global_int(GV_JOB_L(j)))) + ".");
         end
         n += 1;
      end
      j += 1;
   end
   return n;
end

// Вода в неделю, пайков: старый колодец 10 / мотопомпа 20, новый 10 / бак 15
procedure bld_water begin
   variable w := 0, lv;
   lv := bld_level(U_OLDWELL);
   if (lv == 1) then w += 10;
   else if (lv >= 2) then w += 20;
   lv := bld_level(U_NEWWELL);
   if (lv == 1) then w += 10;
   else if (lv >= 2) then w += 15;
   return w;
end

// Еда в неделю без духа, пайков: грядка 5 / огород 8; брамины: стоянка 2 / загон 10 (если жив хоть один брамин)
procedure bld_food begin
   variable f := 0, u := U_GARDEN, lv;
   while (u <= U_GARDEN + 1) do begin
      lv := bld_level(u);
      if (lv == 1) then f += 5;
      else if (lv >= 2) then f += 8;
      u += 1;
   end
   if (not cv_is_dead(CV_SLOT_BRAHMIN) or not cv_is_dead(CV_SLOT_BRAHMIN + 1)) then begin
      lv := bld_level(U_FARM);
      if (lv == 1) then f += 2;
      else if (lv >= 2) then f += 10;
   end
   return f;
end

// Дух от построек, %: жилье в среднем по домам (палатка -10, шатер 0), бар +5 (1-2 уровень)
procedure bld_morale begin
   variable u := U_HOUSE, n := 0, s := 0, lv, m := 0;
   while (u < U_HOUSE + 8) do begin
      lv := bld_level(u);
      if (lv >= 1) then begin
         n += 1;
         if (lv == 1) then s -= 10;
      end
      u += 1;
   end
   if (n) then m := s / n;
   if (bld_level(U_BAR) >= 1) then m += 5;
   return m;
end

#endif
