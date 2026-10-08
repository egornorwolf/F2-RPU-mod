// Кто платит за поселение (принцип 7, Егор 2026-10-08): герой из кармана, касса старосты или вскладчину
// (касса отдает все, что есть, остальное доплачивает герой, economy.md 1). Пункт показываем, только если денег хватает.
// И цены первого набега (1.3): частокол у Хэнка, ополчение у Рика.
// Подключать после define.h, command.h, sfall.h, f2mod.h и f2mset.h.
#ifndef F2MPAY_H
#define F2MPAY_H

#define PAY_HERO            (0)
#define PAY_CASH            (1)
#define PAY_SPLIT           (2)

#define FENCE_PRICE         (1000)  // деревянный частокол: 250 за сторону, весь периметр (buildings-levels.md)
#define FENCE_DAYS          (4)     // по дню на сторону
#define MILITIA_PRICE       (500)   // ополчение: четверо наемников (quests-detailed.md 1.3)
#define MILITIA_COUNT       (4)

// Набег 1.3 и главарь 1.3а (f2mraid.h)
#define RAID_OUT_NONE       (1)     // ничего не сделано: Рик с одним охранником
#define RAID_OUT_FENCE      (2)     // только частокол
#define RAID_OUT_GUARD      (3)     // ополчение или спутник (частокол уже не важен)
#define RAID_HOURS          (24)    // набег через сутки после основания (Егор, 2026-10-08)
#define BOSS_HOURS          (24)    // главарь через сутки после набега
#define RAID_NEXT_EXTRA     (3)     // «они запомнили»: следующий набег сильнее на 3
#define RAID_TRACK_SKILL    (50)    // Скиталец: прочитать следы
#define WAGON_HOURS         (168)   // угнанный фургон Тед покупает с ближайшим караваном (раз в неделю)
#define BOSS_SPEECH         (60)    // Красноречие: имя Кейна и слабость банды
#define BOSS_XP_SPEECH      (200)
#define BURY_MORALE         (5)     // похоронили погибшего: дух +5%
#define GANG_SIZE           (20)    // бойцы Кейна на краю карты


#define pay_cash_now        (get_sfall_global_int(GV_SET_CASH))
#define can_pay_hero(p)     (dude_caps >= (p))
#define can_pay_cash(p)     (pay_cash_now >= (p))
#define can_pay_split(p)    (pay_cash_now > 0 and pay_cash_now < (p) and dude_caps >= (p) - pay_cash_now)

procedure pay_do(variable price, variable who);

procedure pay_do(variable price, variable who) begin
   variable c;
   if (who == PAY_HERO) then
      item_caps_adjust(dude_obj, -price);
   else if (who == PAY_CASH) then
      set_sfall_global(GV_SET_CASH, pay_cash_now - price);
   else begin
      c := pay_cash_now;
      set_sfall_global(GV_SET_CASH, 0);
      item_caps_adjust(dude_obj, c - price);
   end
end

#endif
