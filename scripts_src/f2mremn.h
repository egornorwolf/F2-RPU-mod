// Остатки банды (квест 1.4б, Егор 2026-10-09; карточка «Остатки банды» в docs/npc-cards.md).
// Банда ушла из карьера живой (взрыв погреба, откуп или мир) — хотя бы вожак и один боец: через 60 дней
// первая случайная встреча в пустыне — вожак и до 4 бойцов, уже как дикари.
// Вожак (Кейн, если был жив при взрыве) не идет к герою ни за что; бойцов можно уговорить (Красноречие 60),
// тогда с вожаком бой один на один, а бойцы приходят в лагерь ополченцами.
// Подключать после define.h, command.h, sfall.h, f2mod.h, f2mcv.h, f2mset.h (в нем f2mbld.h), f2mraid.h и f2mlair.h.
#ifndef F2MREMN_H
#define F2MREMN_H

#define GV_REMN         "f2mremst"  // 0 встречи не было, 1 была (один раз)
#define GV_REMN_FIGHT   "f2mremfg"  // 1 = бой на карте встречи начался: враждебные остатки идут на героя сами
#define GV_REMN_JOIN    "f2mremjn"  // сколько бойцов из остатков идут в лагерь: встанут у ворот при входе

#define REMN_DAYS       (60)
#define REMN_MEN        (4)
#define REMN_SPEECH     (60)
#define REMN_XP         (300)

// Модели дикарей (анимации проверены по critter.dat): NMKROM — копье, пистолет, пистолет-пулемет, винтовка;
// NMWARR — нож, молот, копье, пистолет-пулемет; NMPRMB — только копье
#define REMN_ART_LEAD   (FID_NMKROM bwand 0xFFF)
#define REMN_ART_WARR   (FID_NMWARR bwand 0xFFF)
#define REMN_ART_PRMB   (FID_NMPRMB bwand 0xFFF)

#define remn_msg(n)     message_str(SCRIPT_F2MREMC, n)
#define remn_art(c)     (obj_art_fid(c) bwand 0xFFF)
#define remn_is(c)      (obj_pid(c) == PID_RAIDER_MALE and (remn_art(c) == REMN_ART_LEAD or remn_art(c) == REMN_ART_WARR \
                         or remn_art(c) == REMN_ART_PRMB))
#define remn_lead(c)    (remn_art(c) == REMN_ART_LEAD)

procedure remn_due;
procedure remn_arrive;

// Пора ли встрече: банда ушла живой и прошло 60 дней (из обработчика случайных встреч)
procedure remn_due begin
   variable how;
   how := get_sfall_global_int(GV_LAIR_HOW);
   if (get_sfall_global_int(GV_REMN) or (how != LAIR_HOW_BLAST and how != LAIR_HOW_PEACE)) then return 0;
   // сохранения до 0.9.3: ни час ухода, ни число ушедших не записаны — отсчет с этой минуты, вожак и 4 бойца
   if (not get_sfall_global_int(GV_LAIR_FIN)) then begin
      set_sfall_global(GV_LAIR_FIN, bld_hour);
      if (not get_sfall_global_int(GV_REMN_MEN)) then set_sfall_global(GV_REMN_MEN, REMN_MEN + 1);
      return 0;
   end
   if (get_sfall_global_int(GV_REMN_MEN) < 2) then return 0;
   return bld_hour >= get_sfall_global_int(GV_LAIR_FIN) + REMN_DAYS * 24;
end

// Карта лагеря: уговоренные бойцы пришли и встали у южных ворот ополченцами (едят как жители).
// Места у поста их не держат (Егор 2026-10-09: спят посменно, штрафов за места у охраны нет).
// Ополченцы как все: снаряжение охраны у Рика их переоденет в броню моделью героя
procedure remn_arrive begin
   variable n, i := 0, obj;
   n := get_sfall_global_int(GV_REMN_JOIN);
   if (n <= 0) then return;
   set_sfall_global(GV_REMN_JOIN, 0);
   while (i < n) do begin
      obj := cv_put(PID_MILITIA_MALE, SCRIPT_F2MCMIL, tile_num_in_direction(RAID_GATE_IN, (i + 3) % 6, 3));
      if (i % 2) then art_change_fid_num(obj, REMN_ART_PRMB);
      else art_change_fid_num(obj, REMN_ART_WARR);
      call cv_arm(obj, PID_SPEAR, 0);
      call cv_stims(obj, 1);
      anim(obj, ANIMATE_ROTATION, 2);
      i += 1;
   end
   set_sfall_global(GV_SET_MILIT, get_sfall_global_int(GV_SET_MILIT) + n);
   display_msg(remn_msg(300) + n + remn_msg(301));
end

#endif
