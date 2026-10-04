// Общие номера мода. Должны совпадать с записями в mod/append (city.txt, maps.txt, scripts.lst);
// сборка сверяет номера скриптов со строками scripts.lst.
#ifndef F2MOD_H
#define F2MOD_H

#define AREA_F2MOD_CAMP     (61)    // [Area 61] в city.txt
#define MAP_F2MOD_CAMP      (173)   // [Map 173] в maps.txt
#define MAP_F2MOD_CARAVAN   (174)   // [Map 174] в maps.txt: встреча с караваном

// Номера скриптов = номер строки в scripts.lst
#define SCRIPT_F2MCAMP      (1559)  // карта лагеря
#define SCRIPT_F2MCRVN      (1560)  // карта встречи с караваном
#define SCRIPT_F2MCMST      (1561)  // караванщик
#define SCRIPT_F2MCGRD      (1562)  // охранник каравана
#define SCRIPT_ECBRAHMN     (631)   // брамин случайной встречи из RPU (не меняем)

// Глобальные переменные sfall (имя ровно 8 символов, хранятся в сохранении)
#define GV_CARAVAN          "f2mcrvst"  // встреча «Хорошее место»: 0 не было, 1 координаты получены
#define GV_CARAVAN_REFUSED  "f2mcrvrf"  // сколько раз герой отказал каравану
#define GV_CARAVAN_HERE     "f2mcrvnw"  // 1 = эту карту загрузила наша встреча

#define CARAVAN_NONE        (0)
#define CARAVAN_DONE        (1)
#define CARAVAN_MIN_LEVEL   (10)
#define CARAVAN_PRICE       (500)

#endif
