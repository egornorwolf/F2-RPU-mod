// Расстановка лагеря у скал. Файл создан tools/layout/emit.py, руками не править.
// Палатки собраны из тех же стен и шестов, что палатки торговцев в пустынных встречах (desert7).
#ifndef F2MLAY_H
#define F2MLAY_H

#define LAY_FIRE       (20083)
#define LAY_TABLE      (18884)
#define LAY_TED        (19283)
#define LAY_TENT0      (15479)
#define LAY_TENT1      (15667)
#define LAY_TENT2      (17661)
#define LAY_HEROTENT   (15495)
#define LAY_LOCKER     (14894)
#define LAY_OLDWELL    (24087)
#define LAY_FOREMAN    (22300)
#define LAY_CHIEF      (20899)
#define LAY_NEWWELL    (24504)
#define LAY_GARDEN0    (23916)
#define LAY_GARDEN1    (23527)
#define LAY_SLOT0      (16713)
#define LAY_SLOT1      (19925)
#define LAY_SLOT2      (13717)
#define LAY_SLOT3      (17329)

#define LAY_SLOTS      (7)    // 0 колодец, 1-2 огороды, 3-6 палатки

procedure lay_obj(variable pid, variable tile);
procedure lay_camp;
procedure lay_slot(variable slot);

procedure lay_obj(variable pid, variable tile) begin
   if (not tile_contains_pid_obj(tile, 0, pid)) then create_object(pid, tile, 0);
end

procedure lay_camp begin
   call lay_obj(33555632, 20083);
   call lay_obj(33554433, 20290);
   call lay_obj(33554433, 19673);
   call lay_obj(33554493, 18884);
   call lay_obj(33555028, 18284);
   call lay_obj(33554821, 15872);
   call lay_obj(50332578, 14274);
   call lay_obj(50332579, 14474);
   call lay_obj(50332580, 14674);
   call lay_obj(50332581, 14874);
   call lay_obj(50332582, 15074);
   call lay_obj(50332269, 15274);
   call lay_obj(33554816, 14275);
   call lay_obj(33554819, 14275);
   call lay_obj(50332576, 14275);
   call lay_obj(50332604, 15675);
   call lay_obj(50332596, 15875);
   call lay_obj(50332270, 16075);
   call lay_obj(50332602, 15676);
   call lay_obj(50332270, 15876);
   call lay_obj(50332270, 14277);
   call lay_obj(33554817, 15677);
   call lay_obj(50332601, 15877);
   call lay_obj(50332270, 14279);
   call lay_obj(50332600, 15879);
   call lay_obj(50332591, 15680);
   call lay_obj(50332270, 15880);
   call lay_obj(50332269, 14281);
   call lay_obj(50332584, 14481);
   call lay_obj(50332585, 14681);
   call lay_obj(50332269, 14881);
   call lay_obj(50332597, 15081);
   call lay_obj(50332598, 15281);
   call lay_obj(50332599, 15481);
   call lay_obj(50332589, 15681);
   call lay_obj(50332590, 15881);
   call lay_obj(33554820, 14484);
   call lay_obj(33554820, 15884);
   call lay_obj(33554641, 14677);
   call lay_obj(33554640, 15076);
   call lay_obj(33554640, 15080);
   call lay_obj(33554821, 16060);
   call lay_obj(50332578, 14462);
   call lay_obj(50332579, 14662);
   call lay_obj(50332580, 14862);
   call lay_obj(50332581, 15062);
   call lay_obj(50332582, 15262);
   call lay_obj(50332269, 15462);
   call lay_obj(33554816, 14463);
   call lay_obj(33554819, 14463);
   call lay_obj(50332576, 14463);
   call lay_obj(50332604, 15863);
   call lay_obj(50332596, 16063);
   call lay_obj(50332270, 16263);
   call lay_obj(50332602, 15864);
   call lay_obj(50332270, 16064);
   call lay_obj(50332270, 14465);
   call lay_obj(33554817, 15865);
   call lay_obj(50332601, 16065);
   call lay_obj(50332270, 14467);
   call lay_obj(50332600, 16067);
   call lay_obj(50332591, 15868);
   call lay_obj(50332270, 16068);
   call lay_obj(50332269, 14469);
   call lay_obj(50332584, 14669);
   call lay_obj(50332585, 14869);
   call lay_obj(50332269, 15069);
   call lay_obj(50332597, 15269);
   call lay_obj(50332598, 15469);
   call lay_obj(50332599, 15669);
   call lay_obj(50332589, 15869);
   call lay_obj(50332590, 16069);
   call lay_obj(33554820, 14672);
   call lay_obj(33554820, 16072);
   call lay_obj(33554641, 14865);
   call lay_obj(33554640, 15264);
   call lay_obj(33554640, 15268);
   call lay_obj(33554821, 18054);
   call lay_obj(50332578, 16456);
   call lay_obj(50332579, 16656);
   call lay_obj(50332580, 16856);
   call lay_obj(50332581, 17056);
   call lay_obj(50332582, 17256);
   call lay_obj(50332269, 17456);
   call lay_obj(33554816, 16457);
   call lay_obj(33554819, 16457);
   call lay_obj(50332576, 16457);
   call lay_obj(50332604, 17857);
   call lay_obj(50332596, 18057);
   call lay_obj(50332270, 18257);
   call lay_obj(50332602, 17858);
   call lay_obj(50332270, 18058);
   call lay_obj(50332270, 16459);
   call lay_obj(33554817, 17859);
   call lay_obj(50332601, 18059);
   call lay_obj(50332270, 16461);
   call lay_obj(50332600, 18061);
   call lay_obj(50332591, 17862);
   call lay_obj(50332270, 18062);
   call lay_obj(50332269, 16463);
   call lay_obj(50332584, 16663);
   call lay_obj(50332585, 16863);
   call lay_obj(50332269, 17063);
   call lay_obj(50332597, 17263);
   call lay_obj(50332598, 17463);
   call lay_obj(50332599, 17663);
   call lay_obj(50332589, 17863);
   call lay_obj(50332590, 18063);
   call lay_obj(33554820, 16666);
   call lay_obj(33554820, 18066);
   call lay_obj(33554641, 16859);
   call lay_obj(33554640, 17258);
   call lay_obj(33554640, 17262);
   call lay_obj(33554821, 15888);
   call lay_obj(50332578, 14290);
   call lay_obj(50332579, 14490);
   call lay_obj(50332580, 14690);
   call lay_obj(50332581, 14890);
   call lay_obj(50332582, 15090);
   call lay_obj(50332269, 15290);
   call lay_obj(33554816, 14291);
   call lay_obj(33554819, 14291);
   call lay_obj(50332576, 14291);
   call lay_obj(50332604, 15691);
   call lay_obj(50332596, 15891);
   call lay_obj(50332270, 16091);
   call lay_obj(50332602, 15692);
   call lay_obj(50332270, 15892);
   call lay_obj(50332270, 14293);
   call lay_obj(33554817, 15693);
   call lay_obj(50332601, 15893);
   call lay_obj(50332270, 14295);
   call lay_obj(50332600, 15895);
   call lay_obj(50332591, 15696);
   call lay_obj(50332270, 15896);
   call lay_obj(50332269, 14297);
   call lay_obj(50332584, 14497);
   call lay_obj(50332585, 14697);
   call lay_obj(50332269, 14897);
   call lay_obj(50332597, 15097);
   call lay_obj(50332598, 15297);
   call lay_obj(50332599, 15497);
   call lay_obj(50332589, 15697);
   call lay_obj(50332590, 15897);
   call lay_obj(33554820, 14500);
   call lay_obj(33554820, 15900);
   call lay_obj(33554641, 14693);
   call lay_obj(33554640, 15092);
   call lay_obj(33554640, 15096);
   call lay_obj(33554830, 25689);
   call lay_obj(33554833, 26089);
   call lay_obj(33554652, 25891);
   create_object_sid(33555425, LAY_OLDWELL, 0, SCRIPT_F2MWELL);   // старый заколоченный колодец
   call lay_obj(128, LAY_LOCKER);   // сундук героя (Footlocker)
end

procedure lay_slot(variable slot) begin
   if (slot == 0) then begin   // newwell
      if (not tile_contains_pid_obj(24504, 0, 33554815)) then create_object_sid(33554815, 24504, 0, SCRIPT_F2MWELL);
   end
   else if (slot == 1) then begin   // garden0
      call lay_obj(33555395, 23117);
      call lay_obj(33555396, 23315);
      call lay_obj(33555397, 23513);
      call lay_obj(33555398, 23711);
      call lay_obj(33554798, 23718);
      call lay_obj(33554799, 23916);
      call lay_obj(33554798, 24114);
      call lay_obj(33554799, 24312);
      call lay_obj(33555397, 24321);
      call lay_obj(33555398, 24519);
      call lay_obj(33555399, 24717);
      call lay_obj(33555400, 24915);
      call lay_obj(33554813, 23322);
   end
   else if (slot == 2) then begin   // garden1
      call lay_obj(33555395, 22528);
      call lay_obj(33555396, 22726);
      call lay_obj(33555397, 22924);
      call lay_obj(33555398, 23122);
      call lay_obj(33554798, 23329);
      call lay_obj(33554799, 23527);
      call lay_obj(33554798, 23725);
      call lay_obj(33554799, 23923);
      call lay_obj(33555397, 23732);
      call lay_obj(33555398, 23930);
      call lay_obj(33555399, 24128);
      call lay_obj(33555400, 24326);
      call lay_obj(33554813, 22933);
   end
   else if (slot == 3) then begin   // slot0
      call lay_obj(33554821, 17106);
      call lay_obj(50332578, 15508);
      call lay_obj(50332579, 15708);
      call lay_obj(50332580, 15908);
      call lay_obj(50332581, 16108);
      call lay_obj(50332582, 16308);
      call lay_obj(50332269, 16508);
      call lay_obj(33554816, 15509);
      call lay_obj(33554819, 15509);
      call lay_obj(50332576, 15509);
      call lay_obj(50332604, 16909);
      call lay_obj(50332596, 17109);
      call lay_obj(50332270, 17309);
      call lay_obj(50332602, 16910);
      call lay_obj(50332270, 17110);
      call lay_obj(50332270, 15511);
      call lay_obj(33554817, 16911);
      call lay_obj(50332601, 17111);
      call lay_obj(50332270, 15513);
      call lay_obj(50332600, 17113);
      call lay_obj(50332591, 16914);
      call lay_obj(50332270, 17114);
      call lay_obj(50332269, 15515);
      call lay_obj(50332584, 15715);
      call lay_obj(50332585, 15915);
      call lay_obj(50332269, 16115);
      call lay_obj(50332597, 16315);
      call lay_obj(50332598, 16515);
      call lay_obj(50332599, 16715);
      call lay_obj(50332589, 16915);
      call lay_obj(50332590, 17115);
      call lay_obj(33554820, 15718);
      call lay_obj(33554820, 17118);
      call lay_obj(33554641, 15911);
      call lay_obj(33554640, 16310);
      call lay_obj(33554640, 16314);
   end
   else if (slot == 4) then begin   // slot1
      call lay_obj(33554821, 20318);
      call lay_obj(50332578, 18720);
      call lay_obj(50332579, 18920);
      call lay_obj(50332580, 19120);
      call lay_obj(50332581, 19320);
      call lay_obj(50332582, 19520);
      call lay_obj(50332269, 19720);
      call lay_obj(33554816, 18721);
      call lay_obj(33554819, 18721);
      call lay_obj(50332576, 18721);
      call lay_obj(50332604, 20121);
      call lay_obj(50332596, 20321);
      call lay_obj(50332270, 20521);
      call lay_obj(50332602, 20122);
      call lay_obj(50332270, 20322);
      call lay_obj(50332270, 18723);
      call lay_obj(33554817, 20123);
      call lay_obj(50332601, 20323);
      call lay_obj(50332270, 18725);
      call lay_obj(50332600, 20325);
      call lay_obj(50332591, 20126);
      call lay_obj(50332270, 20326);
      call lay_obj(50332269, 18727);
      call lay_obj(50332584, 18927);
      call lay_obj(50332585, 19127);
      call lay_obj(50332269, 19327);
      call lay_obj(50332597, 19527);
      call lay_obj(50332598, 19727);
      call lay_obj(50332599, 19927);
      call lay_obj(50332589, 20127);
      call lay_obj(50332590, 20327);
      call lay_obj(33554820, 18930);
      call lay_obj(33554820, 20330);
      call lay_obj(33554641, 19123);
      call lay_obj(33554640, 19522);
      call lay_obj(33554640, 19526);
   end
   else if (slot == 5) then begin   // slot2
      call lay_obj(33554821, 14110);
      call lay_obj(50332578, 12512);
      call lay_obj(50332579, 12712);
      call lay_obj(50332580, 12912);
      call lay_obj(50332581, 13112);
      call lay_obj(50332582, 13312);
      call lay_obj(50332269, 13512);
      call lay_obj(33554816, 12513);
      call lay_obj(33554819, 12513);
      call lay_obj(50332576, 12513);
      call lay_obj(50332604, 13913);
      call lay_obj(50332596, 14113);
      call lay_obj(50332270, 14313);
      call lay_obj(50332602, 13914);
      call lay_obj(50332270, 14114);
      call lay_obj(50332270, 12515);
      call lay_obj(33554817, 13915);
      call lay_obj(50332601, 14115);
      call lay_obj(50332270, 12517);
      call lay_obj(50332600, 14117);
      call lay_obj(50332591, 13918);
      call lay_obj(50332270, 14118);
      call lay_obj(50332269, 12519);
      call lay_obj(50332584, 12719);
      call lay_obj(50332585, 12919);
      call lay_obj(50332269, 13119);
      call lay_obj(50332597, 13319);
      call lay_obj(50332598, 13519);
      call lay_obj(50332599, 13719);
      call lay_obj(50332589, 13919);
      call lay_obj(50332590, 14119);
      call lay_obj(33554820, 12722);
      call lay_obj(33554820, 14122);
      call lay_obj(33554641, 12915);
      call lay_obj(33554640, 13314);
      call lay_obj(33554640, 13318);
   end
   else if (slot == 6) then begin   // slot3
      call lay_obj(33554821, 17722);
      call lay_obj(50332578, 16124);
      call lay_obj(50332579, 16324);
      call lay_obj(50332580, 16524);
      call lay_obj(50332581, 16724);
      call lay_obj(50332582, 16924);
      call lay_obj(50332269, 17124);
      call lay_obj(33554816, 16125);
      call lay_obj(33554819, 16125);
      call lay_obj(50332576, 16125);
      call lay_obj(50332604, 17525);
      call lay_obj(50332596, 17725);
      call lay_obj(50332270, 17925);
      call lay_obj(50332602, 17526);
      call lay_obj(50332270, 17726);
      call lay_obj(50332270, 16127);
      call lay_obj(33554817, 17527);
      call lay_obj(50332601, 17727);
      call lay_obj(50332270, 16129);
      call lay_obj(50332600, 17729);
      call lay_obj(50332591, 17530);
      call lay_obj(50332270, 17730);
      call lay_obj(50332269, 16131);
      call lay_obj(50332584, 16331);
      call lay_obj(50332585, 16531);
      call lay_obj(50332269, 16731);
      call lay_obj(50332597, 16931);
      call lay_obj(50332598, 17131);
      call lay_obj(50332599, 17331);
      call lay_obj(50332589, 17531);
      call lay_obj(50332590, 17731);
      call lay_obj(33554820, 16334);
      call lay_obj(33554820, 17734);
      call lay_obj(33554641, 16527);
      call lay_obj(33554640, 16926);
      call lay_obj(33554640, 16930);
   end
end

#endif
