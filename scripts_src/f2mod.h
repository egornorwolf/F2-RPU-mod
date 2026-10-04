// Общие номера мода. Должны совпадать с записями в mod/append (city.txt, maps.txt, scripts.lst);
// сборка сверяет номера скриптов со строками scripts.lst.
#ifndef F2MOD_H
#define F2MOD_H

#define AREA_F2MOD_CAMP     (61)    // [Area 61] в city.txt
#define MAP_F2MOD_CAMP      (173)   // [Map 173] в maps.txt
#define MAP_F2MOD_CARAVAN   (174)   // [Map 174] в maps.txt: встреча с караваном
#define MAP_F2MOD_ESCORT    (175)   // [Map 175] в maps.txt: дорога с караваном, 1-е нападение
#define MAP_F2MOD_ESCORT2   (176)   // [Map 176]: 2-е нападение (своя карта: движок не перегружает текущую)
#define MAP_F2MOD_ESCORT3   (177)   // [Map 177]: 3-е нападение
#define escort_map(stage)   (MAP_F2MOD_ESCORT + (stage) - 1)
#define is_escort_map(m)    ((m) >= MAP_F2MOD_ESCORT and (m) <= MAP_F2MOD_ESCORT3)

// Номера скриптов = номер строки в scripts.lst
#define SCRIPT_F2MCAMP      (1559)  // карта лагеря
#define SCRIPT_F2MCRVN      (1560)  // карта встречи с караваном
#define SCRIPT_F2MCMST      (1561)  // караванщик
#define SCRIPT_F2MCGRD      (1562)  // охранник каравана
#define SCRIPT_F2MESCT      (1563)  // карта дороги с караваном
#define SCRIPT_F2MCCIV      (1564)  // мирный переселенец каравана
#define SCRIPT_F2MCBRM      (1565)  // брамин каравана (в бою убегает)
#define SCRIPT_ECBRAHMN     (631)   // брамин случайной встречи из RPU (не меняем)
#define SCRIPT_ECRAIDER     (256)   // налетчик случайной встречи из RPU
#define SCRIPT_ECSCORP      (616)   // скорпион случайной встречи из RPU
#define SCRIPT_ECDTHCLW     (791)   // коготь смерти случайной встречи из RPU
#define SCRIPT_ECGECKO      (615)   // геккон случайной встречи из RPU

// Глобальные переменные sfall (имя ровно 8 символов, хранятся в сохранении)
#define GV_CARAVAN          "f2mcrvst"  // встреча «Хорошее место»: CARAVAN_* ниже
#define GV_ESCORT_STAGE     "f2mescst"  // нападение в пути: 1 налетчики, 2 скорпионы, 3 когти смерти
#define GV_ESCORT_MOVING    "f2mescmv"  // 1 = караван сам переходит на следующую карту
#define GV_CARAVAN_DEAD     "f2mcvded"  // кто из каравана погиб в пути: биты CV_SLOT_* (f2mcdead.h)
#define GV_ESCORT_S3        "f2mesc3k"  // кого убили гекконы до прихода героя: 1 Сара, 2 брамин, 4 мирные;
                                        // 8 = это уже случилось (при повторе гекконов никого заново не убиваем)
#define GV_ESCORT_RESUME    "f2mescrs"  // герой бросил дорогу: с какого нападения продолжить (0 = с начала)
#define GV_CARAVAN_LAST     "f2mcrvls"  // чем кончилась прошлая встреча: CARAVAN_LAST_* ниже
#define GV_ESCORT_WMX       "f2mescwx"  // точка встречи на карте мира (x), от нее идет караван
#define GV_ESCORT_WMY       "f2mescwy"  // то же, y
#define GV_CAMP_CARAVAN     "f2mcmpcv"  // 1 = караван уже поставлен в лагере
#define GV_CARAVAN_HOSTILE  "f2mcrvhs"  // 1 = караван воюет с героем (прицельный выстрел или убитый охранник)

// Массив случайных попаданий по каравану: объект -> 1, если по нему попали не прицельно
#define ARR_CARAVAN_HITS    "f2mhits"

// Свой герою: сам герой или его спутник
#define is_dude_side(x)     ((x) == dude_obj or obj_in_party(x))
#define GV_CARAVAN_REFUSED  "f2mcrvrf"  // сколько раз герой отказал каравану

#define CARAVAN_LAST_REFUSED   (1)  // герой отказал в разговоре
#define CARAVAN_LAST_ABANDONED (2)  // герой бросил караван на дороге

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
#define ESCORT_LEVEL_STEP   (8)     // +1 враг на участке за каждые 8 уровней героя сверх 10-го
#define ESCORT_EXTRA_MAX    (2)     // но не больше двух лишних

// Враги на дороге: только те, кого ставит карта дороги. По команде считать нельзя:
// скрипты RPU меняют команды (брамины уходят в свою).
#define is_escort_enemy(pid) ((pid) == PID_RAIDER_MALE or (pid) == PID_RAIDER_FEMALE \
                              or (pid) == PID_LARGE_RADSCORPION or (pid) == PID_FIRE_GECKO)
#define ESCORT_WM_STEP      (25)    // на сколько точек карты мира караван продвигается к лагерю за участок
#define CAMP_WM_X           (800)   // лагерь на карте мира (city.txt, Area 61)
#define CAMP_WM_Y           (720)

// Отладочные сообщения в окне игры (на время тестов)
#define F2MOD_DEBUG

#endif
