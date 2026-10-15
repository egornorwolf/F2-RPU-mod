// Сгенерировано tools/layout/base_emit.py: военная база на месте логова (карта f2mlair, копия mountn5). Не править руками.
// Уровень 1: расчистка лагеря банды (сундук Кейна и лаз в погреб остаются) и две армейские палатки (командир, казарма),
// 2: мастерская (дощатый сарай) и гараж (грузовик), 3: арсенал (будка). Постройки из карты mbclose (военная база у Наварро).
// Проходимость проверена поиском пути: сундук, лаз, выход из погреба, командир, Хэнк и гарнизон достижимы от входа на всех уровнях.
// Подключать после f2mtlay.h (lay_o, lay_flg).
#ifndef F2MBASEL_H
#define F2MBASEL_H

#define BASE_CMD      (18692)   // (92, 93): командир в своей палатке
#define BASE_HANK     (20092)   // (92, 100): Хэнк на базе, пока идет стройка
#define BASE_SPAWNS   (12)

procedure base_spawn(variable i);
procedure base_rot(variable i);
procedure base_clear_x(variable pid, variable tile);
procedure base_clear_list;
procedure base_lv1;
procedure base_lv2;
procedure base_lv3;

// Места гарнизона (по лагерю, у построек)
procedure base_spawn(variable i) begin
   if (i == 0) then return 20088;   // (88, 100)
   else if (i == 1) then return 19478;   // (78, 97)
   else if (i == 2) then return 18712;   // (112, 93)
   else if (i == 3) then return 18068;   // (68, 90)
   else if (i == 4) then return 20103;   // (103, 100)
   else if (i == 5) then return 17881;   // (81, 89)
   else if (i == 6) then return 18901;   // (101, 94)
   else if (i == 7) then return 19910;   // (110, 99)
   else if (i == 8) then return 17874;   // (74, 89)
   else if (i == 9) then return 18109;   // (109, 90)
   else if (i == 10) then return 19897;   // (97, 99)
   else if (i == 11) then return 18868;   // (68, 94)
   return 20088;
end

// Куда смотрит боец на месте i: на въезд в лагерь (юг)
procedure base_rot(variable i) begin
   if (i == 0) then return 2;
   if (i == 1) then return 3;
   if (i == 2) then return 2;
   if (i == 3) then return 3;
   if (i == 4) then return 2;
   if (i == 5) then return 3;
   if (i == 6) then return 2;
   if (i == 7) then return 2;
   if (i == 8) then return 3;
   if (i == 9) then return 2;
   if (i == 10) then return 2;
   if (i == 11) then return 3;
   return 2;
end

// Расчистка (уровень 1): 298 объектов лагеря банды. base_clear_x убирает объект (вещи из ящиков — в сундук, f2mlair.ssl)
procedure base_clear_list begin
   call base_clear_x(50332270, 16494);   // block.frm
   call base_clear_x(33554499, 16668);   // block.frm
   call base_clear_x(33554499, 16670);   // block.frm
   call base_clear_x(50332270, 16679);   // block.frm
   call base_clear_x(33555376, 16680);   // maryj02.frm
   call base_clear_x(50332270, 16680);   // block.frm
   call base_clear_x(50332270, 16681);   // block.frm
   call base_clear_x(50332270, 16688);   // block.frm
   call base_clear_x(50332270, 16690);   // block.frm
   call base_clear_x(50332270, 16691);   // block.frm
   call base_clear_x(50332270, 16692);   // block.frm
   call base_clear_x(50332270, 16693);   // block.frm
   call base_clear_x(33555376, 16694);   // maryj02.frm
   call base_clear_x(50332270, 16695);   // block.frm
   call base_clear_x(50332270, 16696);   // block.frm
   call base_clear_x(33555396, 16869);   // corn5.frm
   call base_clear_x(33554964, 16870);   // ccart06.frm
   call base_clear_x(33554499, 16870);   // block.frm
   call base_clear_x(50332577, 16872);   // ybk1005.frm
   call base_clear_x(50332575, 16874);   // ybk1003.frm
   call base_clear_x(50332574, 16875);   // ybk1002.frm
   call base_clear_x(50332573, 16876);   // ybk1001.frm
   call base_clear_x(50332572, 16877);   // ybk1000.frm
   call base_clear_x(50332603, 16878);   // ybk1011.frm
   call base_clear_x(33554830, 16879);   // barrel4.frm
   call base_clear_x(33554499, 16879);   // block.frm
   call base_clear_x(50332270, 16883);   // block.frm
   call base_clear_x(50332577, 16888);   // ybk1005.frm
   call base_clear_x(50332575, 16890);   // ybk1003.frm
   call base_clear_x(50332574, 16891);   // ybk1002.frm
   call base_clear_x(50332573, 16892);   // ybk1001.frm
   call base_clear_x(50332572, 16893);   // ybk1000.frm
   call base_clear_x(50332603, 16894);   // ybk1011.frm
   call base_clear_x(33555376, 16896);   // maryj02.frm
   call base_clear_x(50332270, 16896);   // block.frm
   call base_clear_x(33554499, 17069);   // block.frm
   call base_clear_x(50332578, 17072);   // ybk1006.frm
   call base_clear_x(50332576, 17073);   // ybk1004.frm
   call base_clear_x(33554816, 17073);   // ypole1.frm
   call base_clear_x(33554819, 17073);   // ypole4.frm
   call base_clear_x(50332269, 17079);   // block.frm
   call base_clear_x(33554746, 17080);   // trash4.frm
   call base_clear_x(33554499, 17082);   // block.frm
   call base_clear_x(33554802, 17083);   // corn2.frm
   call base_clear_x(33554499, 17083);   // block.frm
   call base_clear_x(33554499, 17084);   // block.frm
   call base_clear_x(33554499, 17087);   // block.frm
   call base_clear_x(50332578, 17088);   // ybk1006.frm
   call base_clear_x(50332576, 17089);   // ybk1004.frm
   call base_clear_x(33554816, 17089);   // ypole1.frm
   call base_clear_x(33554819, 17089);   // ypole4.frm
   call base_clear_x(50332269, 17095);   // block.frm
   call base_clear_x(50332270, 17097);   // block.frm
   call base_clear_x(50332270, 17098);   // block.frm
   call base_clear_x(33554499, 17268);   // block.frm
   call base_clear_x(33554963, 17269);   // ccart05.frm
   call base_clear_x(33554499, 17269);   // block.frm
   call base_clear_x(33554499, 17270);   // block.frm
   call base_clear_x(33554499, 17271);   // block.frm
   call base_clear_x(50332579, 17272);   // ybk1007.frm
   call base_clear_x(33554499, 17273);   // block.frm
   call base_clear_x(33554795, 17275);   // bowl1.frm
   call base_clear_x(33554499, 17275);   // block.frm
   call base_clear_x(33554499, 17278);   // block.frm
   call base_clear_x(50332584, 17279);   // ylf1001.frm
   call base_clear_x(33554828, 17280);   // barrel2.frm
   call base_clear_x(33554499, 17280);   // block.frm
   call base_clear_x(33554801, 17281);   // corn1.frm
   call base_clear_x(33554820, 17282);   // yrope1.frm
   call base_clear_x(33554499, 17283);   // block.frm
   call base_clear_x(33554959, 17284);   // ccart01.frm
   call base_clear_x(33554499, 17285);   // block.frm
   call base_clear_x(33554499, 17287);   // block.frm
   call base_clear_x(50332579, 17288);   // ybk1007.frm
   call base_clear_x(33554745, 17291);   // trash3.frm
   call base_clear_x(33554810, 17291);   // rug3.frm
   call base_clear_x(33554797, 17292);   // bucket1.frm
   call base_clear_x(33554499, 17292);   // block.frm
   call base_clear_x(33554798, 17293);   // cab1.frm
   call base_clear_x(33554798, 17294);   // cab1.frm
   call base_clear_x(50332837, 17295);   // yar2001.frm
   call base_clear_x(33555376, 17297);   // maryj02.frm
   call base_clear_x(50332270, 17299);   // block.frm
   call base_clear_x(50332577, 17300);   // ybk1005.frm
   call base_clear_x(50332270, 17300);   // block.frm
   call base_clear_x(50332575, 17302);   // ybk1003.frm
   call base_clear_x(33554499, 17302);   // block.frm
   call base_clear_x(50332270, 17302);   // block.frm
   call base_clear_x(50332574, 17303);   // ybk1002.frm
   call base_clear_x(50332573, 17304);   // ybk1001.frm
   call base_clear_x(50332270, 17304);   // block.frm
   call base_clear_x(50332572, 17305);   // ybk1000.frm
   call base_clear_x(50332603, 17306);   // ybk1011.frm
   call base_clear_x(50332270, 17306);   // block.frm
   call base_clear_x(33554499, 17469);   // block.frm
   call base_clear_x(33554499, 17471);   // block.frm
   call base_clear_x(50332580, 17472);   // ybk1008.frm
   call base_clear_x(33554499, 17473);   // block.frm
   call base_clear_x(33554652, 17474);   // boxes1.frm
   call base_clear_x(33554499, 17474);   // block.frm
   call base_clear_x(33554809, 17476);   // rug2.frm
   call base_clear_x(33554499, 17477);   // block.frm
   call base_clear_x(33555381, 17478);   // aybed2.frm
   call base_clear_x(33554499, 17478);   // block.frm
   call base_clear_x(50332585, 17479);   // ylf1002.frm
   call base_clear_x(33555375, 17480);   // maryj01.frm
   call base_clear_x(33554499, 17482);   // block.frm
   call base_clear_x(33554499, 17483);   // block.frm
   call base_clear_x(33554499, 17484);   // block.frm
   call base_clear_x(33554499, 17485);   // block.frm
   call base_clear_x(33554499, 17487);   // block.frm
   call base_clear_x(50332580, 17488);   // ybk1008.frm
   call base_clear_x(33554640, 17490);   // bed3.frm
   call base_clear_x(33554798, 17494);   // cab1.frm
   call base_clear_x(50332269, 17495);   // block.frm
   call base_clear_x(33555397, 17497);   // corn6.frm
   call base_clear_x(50332578, 17500);   // ybk1006.frm
   call base_clear_x(50332576, 17501);   // ybk1004.frm
   call base_clear_x(33554816, 17501);   // ypole1.frm
   call base_clear_x(33554819, 17501);   // ypole4.frm
   call base_clear_x(50332270, 17501);   // block.frm
   call base_clear_x(33554499, 17502);   // block.frm
   call base_clear_x(33554499, 17503);   // block.frm
   call base_clear_x(50332270, 17503);   // block.frm
   call base_clear_x(33554499, 17504);   // block.frm
   call base_clear_x(33554499, 17505);   // block.frm
   call base_clear_x(50332270, 17505);   // block.frm
   call base_clear_x(50332270, 17507);   // block.frm
   call base_clear_x(50332270, 17508);   // block.frm
   call base_clear_x(50332270, 17509);   // block.frm
   call base_clear_x(33555396, 17510);   // corn5.frm
   call base_clear_x(50332270, 17510);   // block.frm
   call base_clear_x(50332270, 17511);   // block.frm
   call base_clear_x(33554499, 17513);   // block.frm
   call base_clear_x(50332270, 17513);   // block.frm
   call base_clear_x(33554708, 17514);   // njunk6.frm
   call base_clear_x(33554499, 17514);   // block.frm
   call base_clear_x(50332270, 17514);   // block.frm
   call base_clear_x(33554499, 17671);   // block.frm
   call base_clear_x(50332581, 17672);   // ybk1009.frm
   call base_clear_x(33554499, 17673);   // block.frm
   call base_clear_x(33554499, 17674);   // block.frm
   call base_clear_x(33554499, 17674);   // block.frm
   call base_clear_x(33554499, 17677);   // block.frm
   call base_clear_x(33554499, 17678);   // block.frm
   call base_clear_x(50332269, 17679);   // block.frm
   call base_clear_x(33554499, 17680);   // block.frm
   call base_clear_x(50332581, 17688);   // ybk1009.frm
   call base_clear_x(50332838, 17695);   // yar2002.frm
   call base_clear_x(33554499, 17696);   // block.frm
   call base_clear_x(50332579, 17700);   // ybk1007.frm
   call base_clear_x(33554499, 17702);   // block.frm
   call base_clear_x(33554499, 17703);   // block.frm
   call base_clear_x(33555380, 17704);   // aybed1.frm
   call base_clear_x(33554499, 17704);   // block.frm
   call base_clear_x(33554499, 17705);   // block.frm
   call base_clear_x(50332584, 17707);   // ylf1001.frm
   call base_clear_x(33554820, 17710);   // yrope1.frm
   call base_clear_x(33554499, 17711);   // block.frm
   call base_clear_x(33554499, 17713);   // block.frm
   call base_clear_x(50332582, 17872);   // ybk1010.frm
   call base_clear_x(33554499, 17873);   // block.frm
   call base_clear_x(33554573, 17874);   // block.frm
   call base_clear_x(33554499, 17874);   // block.frm
   call base_clear_x(50332597, 17879);   // yrt1003.frm
   call base_clear_x(33554499, 17880);   // block.frm
   call base_clear_x(33554835, 17883);   // crate3.frm
   call base_clear_x(50332582, 17888);   // ybk1010.frm
   call base_clear_x(50332839, 17895);   // yar2003.frm
   call base_clear_x(33554499, 17896);   // block.frm
   call base_clear_x(33554655, 17897);   // boxes4.frm
   call base_clear_x(33554499, 17897);   // block.frm
   call base_clear_x(50332580, 17900);   // ybk1008.frm
   call base_clear_x(33554744, 17902);   // trash2.frm
   call base_clear_x(33554499, 17902);   // block.frm
   call base_clear_x(33554809, 17904);   // rug2.frm
   call base_clear_x(50332585, 17907);   // ylf1002.frm
   call base_clear_x(33554707, 17909);   // njunk5.frm
   call base_clear_x(33554499, 17909);   // block.frm
   call base_clear_x(33554707, 17910);   // njunk5.frm
   call base_clear_x(33554499, 17910);   // block.frm
   call base_clear_x(33554499, 17911);   // block.frm
   call base_clear_x(33555376, 17912);   // maryj02.frm
   call base_clear_x(33554829, 17913);   // barrel3.frm
   call base_clear_x(33554499, 17913);   // block.frm
   call base_clear_x(50332604, 18072);   // ybk1012.frm
   call base_clear_x(33554499, 18073);   // block.frm
   call base_clear_x(33554833, 18074);   // crate1.frm
   call base_clear_x(33554499, 18074);   // block.frm
   call base_clear_x(50332598, 18079);   // yrt1004.frm
   call base_clear_x(33554499, 18080);   // block.frm
   call base_clear_x(50332604, 18088);   // ybk1012.frm
   call base_clear_x(50332840, 18095);   // yar2004.frm
   call base_clear_x(33554499, 18096);   // block.frm
   call base_clear_x(33554499, 18097);   // block.frm
   call base_clear_x(50332581, 18100);   // ybk1009.frm
   call base_clear_x(33554573, 18102);   // block.frm
   call base_clear_x(33554804, 18106);   // pot1.frm
   call base_clear_x(33554499, 18106);   // block.frm
   call base_clear_x(50332269, 18107);   // block.frm
   call base_clear_x(33555376, 18108);   // maryj02.frm
   call base_clear_x(33554499, 18109);   // block.frm
   call base_clear_x(33554684, 18112);   // junk1.frm
   call base_clear_x(33554499, 18112);   // block.frm
   call base_clear_x(50332269, 18272);   // block.frm
   call base_clear_x(50332599, 18279);   // yrt1005.frm
   call base_clear_x(33554833, 18286);   // crate1.frm
   call base_clear_x(33554499, 18286);   // block.frm
   call base_clear_x(33554797, 18287);   // bucket1.frm
   call base_clear_x(33554499, 18287);   // block.frm
   call base_clear_x(50332269, 18288);   // block.frm
   call base_clear_x(50332841, 18295);   // yar2005.frm
   call base_clear_x(33554499, 18296);   // block.frm
   call base_clear_x(33554834, 18297);   // crate2.frm
   call base_clear_x(33554499, 18297);   // block.frm
   call base_clear_x(50332582, 18300);   // ybk1010.frm
   call base_clear_x(50332597, 18307);   // yrt1003.frm
   call base_clear_x(33554499, 18308);   // block.frm
   call base_clear_x(33554654, 18309);   // boxes3.frm
   call base_clear_x(33554499, 18309);   // block.frm
   call base_clear_x(33554499, 18309);   // block.frm
   call base_clear_x(33554499, 18310);   // block.frm
   call base_clear_x(33554533, 18311);   // tirs002.frm
   call base_clear_x(33554499, 18311);   // block.frm
   call base_clear_x(50332269, 18472);   // block.frm
   call base_clear_x(50332602, 18474);   // yrt1012.frm
   call base_clear_x(33554817, 18475);   // ypole2.frm
   call base_clear_x(50332591, 18478);   // ylf1008.frm
   call base_clear_x(50332589, 18479);   // ylf1006.frm
   call base_clear_x(33554820, 18482);   // yrope1.frm
   call base_clear_x(33554798, 18487);   // cab1.frm
   call base_clear_x(50332269, 18488);   // block.frm
   call base_clear_x(50332847, 18490);   // yar2011.frm
   call base_clear_x(33554817, 18491);   // ypole2.frm
   call base_clear_x(50332844, 18494);   // yar2008.frm
   call base_clear_x(50332842, 18495);   // yar2006.frm
   call base_clear_x(33554499, 18496);   // block.frm
   call base_clear_x(33554499, 18497);   // block.frm
   call base_clear_x(50332604, 18500);   // ybk1012.frm
   call base_clear_x(33554835, 18502);   // crate3.frm
   call base_clear_x(50332598, 18507);   // yrt1004.frm
   call base_clear_x(33554499, 18508);   // block.frm
   call base_clear_x(33554499, 18509);   // block.frm
   call base_clear_x(33554821, 18670);   // yrope2.frm
   call base_clear_x(50332596, 18673);   // ylf1013.frm
   call base_clear_x(50332270, 18674);   // block.frm
   call base_clear_x(50332601, 18675);   // yrt1011.frm
   call base_clear_x(50332600, 18677);   // yrt1009.frm
   call base_clear_x(50332270, 18678);   // block.frm
   call base_clear_x(50332590, 18679);   // ylf1007.frm
   call base_clear_x(50332848, 18689);   // yar2012.frm
   call base_clear_x(50332270, 18690);   // block.frm
   call base_clear_x(50332846, 18691);   // yar2010.frm
   call base_clear_x(50332845, 18693);   // yar2009.frm
   call base_clear_x(50332270, 18694);   // block.frm
   call base_clear_x(50332843, 18695);   // yar2007.frm
   call base_clear_x(33554804, 18696);   // pot1.frm
   call base_clear_x(33554499, 18696);   // block.frm
   call base_clear_x(33554708, 18697);   // njunk6.frm
   call base_clear_x(33554499, 18697);   // block.frm
   call base_clear_x(33554499, 18697);   // block.frm
   call base_clear_x(50332269, 18700);   // block.frm
   call base_clear_x(180, 18702);   // crate4.frm
   call base_clear_x(33554499, 18702);   // block.frm
   call base_clear_x(50332599, 18707);   // yrt1005.frm
   call base_clear_x(33554499, 18707);   // block.frm
   call base_clear_x(33554743, 18708);   // trash1.frm
   call base_clear_x(33554499, 18709);   // block.frm
   call base_clear_x(33554499, 18873);   // block.frm
   call base_clear_x(33554499, 18897);   // block.frm
   call base_clear_x(50332269, 18900);   // block.frm
   call base_clear_x(50332602, 18902);   // yrt1012.frm
   call base_clear_x(33554817, 18903);   // ypole2.frm
   call base_clear_x(50332591, 18906);   // ylf1008.frm
   call base_clear_x(50332589, 18907);   // ylf1006.frm
   call base_clear_x(33554820, 18910);   // yrope1.frm
   call base_clear_x(33554809, 19090);   // rug2.frm
   call base_clear_x(33554821, 19098);   // yrope2.frm
   call base_clear_x(50332596, 19101);   // ylf1013.frm
   call base_clear_x(50332270, 19102);   // block.frm
   call base_clear_x(50332601, 19103);   // yrt1011.frm
   call base_clear_x(50332600, 19105);   // yrt1009.frm
   call base_clear_x(50332270, 19106);   // block.frm
   call base_clear_x(50332590, 19107);   // ylf1007.frm
   call base_clear_x(33554528, 19288);   // char02.frm
   call base_clear_x(33554499, 19288);   // block.frm
   call base_clear_x(33554499, 19290);   // block.frm
   call base_clear_x(33554499, 19291);   // block.frm
   call base_clear_x(33554532, 19491);   // char06.frm
   call base_clear_x(33554499, 19491);   // block.frm
   call base_clear_x(33554745, 19493);   // trash3.frm
   call base_clear_x(33554499, 19493);   // block.frm
   call base_clear_x(33555044, 19690);   // woodfire.frm
   call base_clear_x(33554499, 19690);   // block.frm
   call base_clear_x(33555044, 19692);   // woodfire.frm
   call base_clear_x(33554499, 19692);   // block.frm
   call base_clear_x(33554744, 19889);   // trash2.frm
   call base_clear_x(33554499, 19889);   // block.frm
end

// Уровень 1: армейские палатки командира и казармы, объектов 139
procedure base_lv1 begin
   call lay_o(50332577, 17688, 0);
   call lay_o(50332575, 17690, 0);
   call lay_o(50332574, 17691, 0);
   call lay_o(50332573, 17692, 0);
   call lay_o(50332572, 17693, 0);
   call lay_o(50332603, 17694, 0);
   call lay_o(50332578, 17888, 0);
   call lay_o(50332576, 17889, 0);
   call lay_o(33554816, 17889, 0);
   call lay_o(33554819, 17889, 0);
   call lay_o(33554499, 17890, 0);
   call lay_o(33554499, 17891, 0);
   call lay_o(33554499, 17892, 0);
   call lay_o(50332270, 17893, 0);
   call lay_o(50332269, 17895, 0);
   call lay_o(50332579, 18088, 0);
   call lay_o(33554499, 18089, 0);
   call lay_o(33554499, 18090, 0);
   call lay_o(33555380, 18091, 0);
   call lay_o(33554499, 18092, 0);
   call lay_o(33554499, 18093, 0);
   call lay_o(130, 18093, 0);
   call lay_o(50332584, 18095, 0);
   call lay_o(33554499, 18096, 0);
   call lay_o(33554499, 18097, 0);
   call lay_o(33554820, 18098, 0);
   call lay_o(50332580, 18288, 0);
   call lay_o(50332585, 18295, 0);
   call lay_o(33554499, 18297, 0);
   call lay_o(50332581, 18488, 0);
   call lay_o(33554499, 18489, 0);
   call lay_o(369, 18489, 0);
   call lay_o(50332269, 18495, 0);
   call lay_o(50332582, 18688, 0);
   call lay_o(33554499, 18689, 0);
   call lay_o(50332597, 18695, 0);
   call lay_o(33554499, 18696, 0);
   call lay_o(50332604, 18888, 0);
   call lay_o(50332598, 18895, 0);
   call lay_o(33554499, 18896, 0);
   call lay_o(33554499, 18897, 0);
   call lay_o(33554499, 18898, 0);
   call lay_o(50332269, 19088, 0);
   call lay_o(50332599, 19095, 0);
   call lay_o(33554499, 19096, 0);
   call lay_o(33554499, 19098, 0);
   call lay_o(33554499, 19288, 0);
   call lay_o(50332269, 19289, 0);
   call lay_o(50332595, 19290, 0);
   call lay_flg(268435456, 0);
   call lay_o(33554817, 19291, 0);
   call lay_o(50332591, 19294, 0);
   call lay_flg(268435456, 0);
   call lay_o(50332589, 19295, 0);
   call lay_flg(268435456, 0);
   call lay_o(33554499, 19296, 0);
   call lay_o(33554499, 19297, 0);
   call lay_o(33554820, 19298, 0);
   call lay_o(33554821, 19486, 0);
   call lay_o(33554499, 19487, 0);
   call lay_o(50332596, 19489, 0);
   call lay_flg(268435456, 0);
   call lay_o(50332270, 19490, 0);
   call lay_o(50332601, 19491, 0);
   call lay_flg(268435456, 0);
   call lay_o(50332600, 19493, 0);
   call lay_flg(268435456, 0);
   call lay_o(50332270, 19494, 0);
   call lay_o(50332590, 19495, 0);
   call lay_flg(268435456, 0);
   call lay_o(50332270, 19689, 0);
   call lay_o(33554499, 18271, 0);
   call lay_o(33554499, 18471, 0);
   call lay_o(33554499, 18472, 0);
   call lay_o(50332577, 18474, 0);
   call lay_o(50332575, 18476, 0);
   call lay_o(50332574, 18477, 0);
   call lay_o(50332573, 18478, 0);
   call lay_o(50332572, 18479, 0);
   call lay_o(50332269, 18480, 0);
   call lay_o(50332603, 18480, 0);
   call lay_o(33554499, 18672, 0);
   call lay_o(50332578, 18674, 0);
   call lay_o(50332576, 18675, 0);
   call lay_o(33554816, 18675, 0);
   call lay_o(33554819, 18675, 0);
   call lay_o(33554499, 18676, 0);
   call lay_o(33554499, 18677, 0);
   call lay_o(33554499, 18678, 0);
   call lay_o(50332270, 18679, 0);
   call lay_o(50332269, 18681, 0);
   call lay_o(33554499, 18682, 0);
   call lay_o(33554499, 18872, 0);
   call lay_o(50332579, 18874, 0);
   call lay_o(33554499, 18875, 0);
   call lay_o(33554499, 18876, 0);
   call lay_o(33555380, 18877, 0);
   call lay_o(33554499, 18878, 0);
   call lay_o(33554499, 18879, 0);
   call lay_o(130, 18879, 0);
   call lay_o(50332584, 18881, 0);
   call lay_o(33554499, 18882, 0);
   call lay_o(33554499, 18883, 0);
   call lay_o(33554820, 18884, 0);
   call lay_o(33554499, 19071, 0);
   call lay_o(50332580, 19074, 0);
   call lay_o(33554499, 19079, 0);
   call lay_o(50332585, 19081, 0);
   call lay_o(33554499, 19084, 0);
   call lay_o(33554499, 19271, 0);
   call lay_o(50332581, 19274, 0);
   call lay_o(50332269, 19281, 0);
   call lay_o(33554654, 19283, 0);
   call lay_flg(0, 536870912);
   call lay_o(33554499, 19284, 0);
   call lay_o(50332582, 19474, 0);
   call lay_o(50332597, 19481, 0);
   call lay_o(33554499, 19482, 0);
   call lay_o(33554499, 19483, 0);
   call lay_o(50332269, 19674, 0);
   call lay_o(50332598, 19681, 0);
   call lay_o(33554499, 19682, 0);
   call lay_o(33554655, 19683, 0);
   call lay_flg(0, 536870912);
   call lay_o(50332599, 19881, 0);
   call lay_o(33554499, 19883, 0);
   call lay_o(33554499, 20072, 0);
   call lay_o(33554499, 20073, 0);
   call lay_o(33554499, 20074, 0);
   call lay_o(50332602, 20076, 0);
   call lay_flg(268435456, 0);
   call lay_o(33554817, 20077, 0);
   call lay_o(50332591, 20080, 0);
   call lay_flg(268435456, 0);
   call lay_o(50332589, 20081, 0);
   call lay_flg(268435456, 0);
   call lay_o(33554499, 20082, 0);
   call lay_o(33554499, 20083, 0);
   call lay_o(33554820, 20084, 0);
   call lay_o(33554821, 20272, 0);
   call lay_o(33554499, 20273, 0);
   call lay_o(50332596, 20275, 0);
   call lay_flg(268435456, 0);
   call lay_o(50332270, 20276, 0);
   call lay_o(50332601, 20277, 0);
   call lay_flg(268435456, 0);
   call lay_o(50332600, 20279, 0);
   call lay_flg(268435456, 0);
   call lay_o(50332270, 20280, 0);
   call lay_o(50332590, 20281, 0);
   call lay_flg(268435456, 0);
   call lay_o(33554499, 20282, 0);
   call lay_o(33554499, 20283, 0);
   call lay_o(50332270, 20475, 0);
   call lay_o(50332270, 19874, 0);
end

// Уровень 2: мастерская (сарай) и гараж (грузовик), объектов 41
procedure base_lv2 begin
   call lay_o(33554499, 16904, 0);
   call lay_o(33554499, 16906, 0);
   call lay_o(50331786, 17102, 0);
   call lay_o(50331777, 17103, 0);
   call lay_o(50331778, 17104, 0);
   call lay_o(50331777, 17105, 0);
   call lay_o(50332015, 17106, 0);
   call lay_o(50331768, 17302, 0);
   call lay_o(33554499, 17303, 0);
   call lay_o(180, 17303, 0);
   call lay_o(50332269, 17306, 0);
   call lay_o(50331898, 17502, 0);
   call lay_o(50332392, 17506, 0);
   call lay_o(50331768, 17702, 0);
   call lay_o(33554499, 17703, 0);
   call lay_o(180, 17703, 0);
   call lay_o(33555282, 17706, 0);
   call lay_o(50331898, 17902, 0);
   call lay_o(50332393, 17906, 0);
   call lay_o(33554499, 18103, 0);
   call lay_o(180, 18103, 0);
   call lay_o(50331763, 18106, 0);
   call lay_o(50331787, 18302, 0);
   call lay_o(50331745, 18303, 0);
   call lay_o(50331744, 18304, 0);
   call lay_o(50331745, 18305, 0);
   call lay_o(50332382, 18306, 0);
   call lay_o(33554438, 18503, 0);
   call lay_o(33554499, 18504, 0);
   call lay_o(33554499, 18505, 0);
   call lay_o(33554499, 18506, 0);
   call lay_o(33554499, 20680, 0);
   call lay_o(33554499, 20682, 0);
   call lay_o(33554499, 20684, 0);
   call lay_o(33554499, 20879, 0);
   call lay_o(33554499, 20881, 0);
   call lay_o(33554755, 20882, 0);
   call lay_flg(0, 536870912);
   call lay_o(33554499, 20883, 0);
   call lay_o(33554499, 20885, 0);
   call lay_o(33554499, 21481, 0);
   call lay_o(33554499, 21482, 0);
end

// Уровень 3: арсенал (будка), объектов 13
procedure base_lv3 begin
   call lay_o(33554499, 18906, 0);
   call lay_o(33554499, 19104, 0);
   call lay_o(33554499, 19105, 0);
   call lay_o(33554499, 19107, 0);
   call lay_o(33554499, 19108, 0);
   call lay_o(33554499, 19304, 0);
   call lay_o(33555029, 19306, 0);
   call lay_flg(0, 536870912);
   call lay_o(33554499, 19308, 0);
   call lay_o(33554499, 19504, 0);
   call lay_o(33554499, 19506, 0);
   call lay_o(33554499, 19508, 0);
   call lay_o(33554499, 19705, 0);
   call lay_o(33554499, 19707, 0);
end

#endif
