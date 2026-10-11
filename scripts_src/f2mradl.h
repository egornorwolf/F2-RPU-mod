// Сгенерировано tools/layout/levels_emit.py: временный стол радиста (mdesk1 + mdesk2) у построенных зданий лагеря.
// Не править руками. Порядок выбора здания — RADIO_ORDER в levels_emit.py (центр, склад, мастерская...).
#ifndef F2MRADL_H
#define F2MRADL_H
#define RADIO_ORDER_N  (16)
procedure radio_unit(variable i) begin
   if (i == 0) then return 13;
   else if (i == 1) then return 12;
   else if (i == 2) then return 14;
   else if (i == 3) then return 15;
   else if (i == 4) then return 17;
   else if (i == 5) then return 18;
   else if (i == 6) then return 16;
   else if (i == 7) then return 19;
   else if (i == 8) then return 4;
   else if (i == 9) then return 5;
   else if (i == 10) then return 6;
   else if (i == 11) then return 7;
   else if (i == 12) then return 8;
   else if (i == 13) then return 9;
   else if (i == 14) then return 10;
   else if (i == 15) then return 11;
   return -1;
end
procedure radio_spot(variable u) begin
   if (u == 13) then return 17684;   // 84, 88: Центр
   if (u == 12) then return 29550;   // 150, 147: Склад
   if (u == 14) then return 24147;   // 147, 120: Мастерская
   if (u == 15) then return 33103;   // 103, 165: Охрана
   if (u == 17) then return 21501;   // 101, 107: Бар
   if (u == 18) then return 28321;   // 121, 141: Медпункт
   if (u == 16) then return 14941;   // 141, 74: Ферма браминов
   if (u == 19) then return 11639;   // 39, 58: Дом героя
   if (u == 4) then return 11872;   // 72, 59: Жилье 1
   if (u == 5) then return 10885;   // 85, 54: Жилье 2
   if (u == 6) then return 10458;   // 58, 52: Жилье 3
   if (u == 7) then return 7871;   // 71, 39: Жилье 4
   if (u == 8) then return 9685;   // 85, 48: Жилье 5
   if (u == 9) then return 9059;   // 59, 45: Жилье 6
   if (u == 10) then return 8646;   // 46, 43: Жилье 7
   if (u == 11) then return 7232;   // 32, 36: Жилье 8
   return 0;
end
procedure radio_sam(variable u) begin
   if (u == 13) then return 17685;
   if (u == 12) then return 29551;
   if (u == 14) then return 24148;
   if (u == 15) then return 33104;
   if (u == 17) then return 21302;
   if (u == 18) then return 28322;
   if (u == 16) then return 14742;
   if (u == 19) then return 11440;
   if (u == 4) then return 11873;
   if (u == 5) then return 10686;
   if (u == 6) then return 10459;
   if (u == 7) then return 8072;
   if (u == 8) then return 9486;
   if (u == 9) then return 8860;
   if (u == 10) then return 8647;
   if (u == 11) then return 7233;
   return 0;
end
#endif
