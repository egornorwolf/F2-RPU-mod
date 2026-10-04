// Общие номера мода. Должны совпадать с записями в mod/append (city.txt, maps.txt, scripts.lst);
// сборка сверяет номера скриптов со строками scripts.lst.
#ifndef F2MOD_H
#define F2MOD_H

#define AREA_F2MOD_CAMP     (61)    // [Area 61] в city.txt
#define MAP_F2MOD_CAMP      (173)   // [Map 173] в maps.txt
#define MAP_F2MOD_CARAVAN   (174)   // [Map 174] в maps.txt: встреча с караваном
#define MAP_F2MOD_ESCORT    (175)   // [Map 175] в maps.txt: дорога с караваном (три нападения)

// Номера скриптов = номер строки в scripts.lst
#define SCRIPT_F2MCAMP      (1559)  // карта лагеря
#define SCRIPT_F2MCRVN      (1560)  // карта встречи с караваном
#define SCRIPT_F2MCMST      (1561)  // караванщик
#define SCRIPT_F2MCGRD      (1562)  // охранник каравана
#define SCRIPT_F2MESCT      (1563)  // карта дороги с караваном
#define SCRIPT_F2MCCIV      (1564)  // мирный переселенец каравана
#define SCRIPT_ECBRAHMN     (631)   // брамин случайной встречи из RPU (не меняем)
#define SCRIPT_ECRAIDER     (256)   // налетчик случайной встречи из RPU
#define SCRIPT_ECSCORP      (616)   // скорпион случайной встречи из RPU
#define SCRIPT_ECDTHCLW     (791)   // коготь смерти случайной встречи из RPU

// Глобальные переменные sfall (имя ровно 8 символов, хранятся в сохранении)
#define GV_CARAVAN          "f2mcrvst"  // встреча «Хорошее место»: CARAVAN_* ниже
#define GV_ESCORT_STAGE     "f2mescst"  // нападение в пути: 1 налетчики, 2 скорпионы, 3 когти смерти
#define GV_ESCORT_MOVING    "f2mescmv"  // 1 = караван сам переходит на следующую карту
#define GV_ESCORT_LOSSES    "f2mesclo"  // 1 = в пути погибли охранник и брамин
#define GV_CAMP_CARAVAN     "f2mcmpcv"  // 1 = караван уже поставлен в лагере
#define GV_CARAVAN_HOSTILE  "f2mcrvhs"  // 1 = караван воюет с героем (прицельный выстрел или убитый охранник)

// Массив случайных попаданий по каравану: объект -> 1, если по нему попали не прицельно
#define ARR_CARAVAN_HITS    "f2mhits"

// Свой герою: сам герой или его спутник
#define is_dude_side(x)     ((x) == dude_obj or obj_in_party(x))
#define GV_CARAVAN_REFUSED  "f2mcrvrf"  // сколько раз герой отказал каравану

#define CARAVAN_NONE        (0)
#define CARAVAN_DONE        (1)     // координаты получены
#define CARAVAN_ESCORT      (2)     // герой сопровождает караван
#define CARAVAN_FAILED      (3)     // караванщик погиб в пути
#define CARAVAN_MIN_LEVEL   (10)
#define CARAVAN_PRICE       (500)
#define CARAVAN_XP_TALK     (500)   // опыт за координаты уговором
#define CARAVAN_XP_BUY      (200)   // опыт за купленные координаты
#define CARAVAN_ESCORT_PAY  (300)   // плата за сопровождение
#define CARAVAN_XP_ESCORT   (500)   // опыт за сопровождение
#define ESCORT_STAGES       (3)

// Отладочные сообщения в окне игры (на время тестов)
#define F2MOD_DEBUG

#endif
