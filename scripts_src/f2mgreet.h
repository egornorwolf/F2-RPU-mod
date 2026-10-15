// Реплики людей лагеря при встрече (Егор 2026-10-08: у ополчения и жителей фразы разные, и подряд не повторяются).
// Один общий счетчик на всех: каждый следующий, кто заговорил, берет следующую строку своего набора.
// Подключать после sfall.h и f2mod.h.
#ifndef F2MGREET_H
#define F2MGREET_H

#define GV_GREET            "f2mgreet"

#define GV_GREET_UP         "f2mgrtup"  // время (get_uptime), когда кто-то в лагере последним сказал приветствие
#define GREET_GAP_MS        (3500)

procedure greet_pick(variable base, variable n);
procedure greet_turn;

// Охрана и ополчение говорят по очереди, не все разом (Егор 2026-10-15): пока не прошло 3,5 с после чужой реплики,
// очередь занята (вернет 0, попробует позже). Половина из тех, кто ждал, так и промолчит: у ворот не хор.
procedure greet_turn begin
   variable last;
   last := get_sfall_global_int(GV_GREET_UP);
   if (last and get_uptime >= last and get_uptime < last + GREET_GAP_MS) then return 0;
   set_sfall_global(GV_GREET_UP, get_uptime);
   return 1;
end

procedure greet_pick(variable base, variable n) begin
   variable k;
   k := get_sfall_global_int(GV_GREET) + 1;
   if (k > 9999) then k := 1;
   set_sfall_global(GV_GREET, k);
   return base + k % n;
end

#endif
