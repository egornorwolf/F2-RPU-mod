// Реплики людей лагеря при встрече (Егор 2026-10-08: у ополчения и жителей фразы разные, и подряд не повторяются).
// Один общий счетчик на всех: каждый следующий, кто заговорил, берет следующую строку своего набора.
// Подключать после sfall.h и f2mod.h.
#ifndef F2MGREET_H
#define F2MGREET_H

#define GV_GREET            "f2mgreet"

procedure greet_pick(variable base, variable n);

procedure greet_pick(variable base, variable n) begin
   variable k;
   k := get_sfall_global_int(GV_GREET) + 1;
   if (k > 9999) then k := 1;
   set_sfall_global(GV_GREET, k);
   return base + k % n;
end

#endif
