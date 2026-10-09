// Сгенерировано tools/layout/lair_emit.py: точки на карте логова (f2mlair, копия mountn5). Не править руками.
#ifndef F2MLAIRL_H
#define F2MLAIRL_H
#define LAIR_HERO     (24084)   // 84, 120: герой входит с юга, за деревьями
#define LAIR_POST0    (21688)   // 88, 108: пост у входа
#define LAIR_POST1    (21479)   // 79, 107: пост у входа
#define LAIR_KANE     (17291)   // 91, 86: главарь в шатре
#define LAIR_CHEST    (17289)   // 89, 86: сундук в шатре за главарем (тайник)
#define LAIR_CELLAR   (18313)   // 113, 91: погреб под камнями у западной палатки
#define LAIR_WATER    (18282)   // 82, 91: бак с водой посреди лагеря
#define LAIR_STORE    (18895)   // 95, 94: ящик со складом (яд)
#define LAIR_DYNBOX   (18708)   // 108, 93: ящик с динамитом у западной палатки, рядом с погребом
#define LAIR_SPAWN0   (19688)   // 88, 98: патруль
#define LAIR_SPAWN1   (19481)   // 81, 97: патруль
#define LAIR_SPAWN2   (20096)   // 96, 100: патруль
#define LAIR_SPAWN3   (18505)   // 105, 92: у западной палатки
#define LAIR_SPAWN4   (18092)   // 92, 90: у шатра
#define LAIR_SPAWN5   (18676)   // 76, 93: у восточной палатки
#define LAIR_SPAWN6   (18070)   // 70, 90: у машины
#define LAIR_SPAWN7   (19110)   // 110, 95: у бочек
#define LAIR_SPAWN8   (19099)   // 99, 95: у ящиков
#define LAIR_SPAWN9   (18885)   // 85, 94: у костра
#define LAIR_SPAWN10  (19702)   // 102, 98: у костра
#define LAIR_SPAWN11  (19874)   // 74, 99: у восточной палатки
#define LAIR_SPAWNS     (12)
procedure lair_spawn(variable i) begin
   if (i == 0) then return LAIR_SPAWN0;
   else if (i == 1) then return LAIR_SPAWN1;
   else if (i == 2) then return LAIR_SPAWN2;
   else if (i == 3) then return LAIR_SPAWN3;
   else if (i == 4) then return LAIR_SPAWN4;
   else if (i == 5) then return LAIR_SPAWN5;
   else if (i == 6) then return LAIR_SPAWN6;
   else if (i == 7) then return LAIR_SPAWN7;
   else if (i == 8) then return LAIR_SPAWN8;
   else if (i == 9) then return LAIR_SPAWN9;
   else if (i == 10) then return LAIR_SPAWN10;
   else if (i == 11) then return LAIR_SPAWN11;
   return LAIR_SPAWN0;
end
#endif
