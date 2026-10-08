// Общие номера мода. Должны совпадать с записями в mod/append (city.txt, maps.txt, scripts.lst);
// сборка сверяет номера скриптов со строками scripts.lst.
#ifndef F2MOD_H
#define F2MOD_H

// Потолок основных статов героя (Егор, 2026-10-05): 15 вместо 10, ставит sfall при каждой загрузке
#define F2MOD_STAT_MAX 15

#define AREA_F2MOD_CAMP     (61)    // [Area 61] в city.txt
#define MAP_F2MOD_CAMP_OLD  (173)   // [Map 173]: прежняя временная карта лагеря (desert1), больше не используется
#define MAP_F2MOD_CAMP      (179)   // [Map 179] в maps.txt: лагерь у скал на карте города (0.5.0)
#define MAP_F2MOD_CARAVAN   (174)   // [Map 174] в maps.txt: встреча с караваном
#define MAP_F2MOD_ESCORT    (175)   // [Map 175] в maps.txt: дорога с караваном, 1-е нападение
#define MAP_F2MOD_ESCORT2   (176)   // [Map 176]: 2-е нападение (своя карта: движок не перегружает текущую)
#define MAP_F2MOD_ESCORT3   (177)   // [Map 177]: 3-е нападение
#define escort_map(stage)   (MAP_F2MOD_ESCORT + (stage) - 1)
#define is_escort_map(m)    ((m) >= MAP_F2MOD_ESCORT and (m) <= MAP_F2MOD_ESCORT3)
#define AREA_F2MOD_TOWN     (62)    // [Area 62]: песочница для обкатки стройки (только с f2mod_test.dat)
#define MAP_F2MOD_TOWN      (178)   // [Map 178]: карта песочницы f2mtown

// Номера скриптов = номер строки в scripts.lst
#define SCRIPT_F2MCAMP      (1559)  // карта лагеря
#define SCRIPT_F2MCRVN      (1560)  // карта встречи с караваном
#define SCRIPT_F2MCMST      (1561)  // караванщик
#define SCRIPT_F2MCGRD      (1562)  // охранник каравана
#define SCRIPT_F2MESCT      (1563)  // карта дороги с караваном
#define SCRIPT_F2MCCIV      (1564)  // мирный переселенец каравана
#define SCRIPT_F2MCBRM      (1565)  // брамин каравана (в бою убегает)
#define SCRIPT_F2MCFRM      (1566)  // прораб Хэнк
#define SCRIPT_F2MWELL      (1567)  // колодцы лагеря (старый, починенный, новый)
#define SCRIPT_F2MTOWN      (1568)  // карта песочницы (тест)
#define SCRIPT_F2MTBLD      (1569)  // строитель песочницы (тест)
#define SCRIPT_F2MTUR       (1570)  // турель песочницы (тест)
#define SCRIPT_F2MCMIL      (1571)  // ополченец у ворот лагеря (нанимает Рик)
#define SCRIPT_F2MBOSS      (1572)  // главарь налетчиков Кейн у ворот (1.3а)
#define SCRIPT_F2MRDR       (1573)  // налетчик Кейна у ворот (1.3а)
#define SCRIPT_F2MRADIO     (1574)  // радист Сэм Мортон (0.7.1)
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
#define GV_CAMP_CARAVAN     "f2mcmpcv"  // 1 = караван уже поставлен в лагере (на прежней карте 173)
#define GV_TOWN_LAYOUT      "f2mtlayt"  // 1 = лагерь расставлен на карте города (0.5.0)
#define GV_TOWN_RUINS       "f2mtruin"  // 5 = руины city1/city2 на участках будущих зданий (0.5.6); 1-4 = развалины 0.5.1-0.5.5, их убираем
#define GV_TOWN_PEOPLE      "f2mtpple"  // 1 = люди лагеря поставлены на карте города (до 0.5.6 имя было из 7 букв, sfall его не хранил)
#define GV_CARAVAN_HOSTILE  "f2mcrvhs"  // 1 = караван воюет с героем (прицельный выстрел или убитый охранник)

// Лагерь у скал (М3)
#define GV_CAMP_LAYOUT      "f2mclayt"  // 1 = лагерь расставлен (палатки, костер, старый колодец, прораб)
#define GV_CAMP_DAY         "f2mcmpdy"  // когда основан лагерь: game_time / ONE_GAME_HOUR
#define GV_CAMP_BUILT       "f2mcbult"  // что построил прораб: биты по местам LAY_* (0 колодец, 1-2 огороды, 3-6 палатки)
#define GV_WELL_OLD         "f2mwlold"  // старый колодец: WELL_OLD_* ниже
#define GV_QUEST_WATER      "f2mqwatr"  // квест «Вода»: 0 не начат, 1 Тед рассказал, 2 выполнен

#define WELL_OLD_BROKEN     (0)
#define WELL_OLD_PARTS      (1)     // детали куплены у прораба
#define WELL_OLD_FIXED      (2)     // герой починил (Ремонт 50%)
#define WELL_FIX_SKILL      (50)    // Ремонт для починки старого колодца
#define WELL_PARTS_PRICE    (20)    // детали у прораба
#define CAMP_WATER_DAYS     (14)    // воды из бочек каравана на 2 недели
#define WATER_XP            (200)   // квест «Вода»: первый рабочий колодец

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

// Набег 1.3 и главарь у ворот 1.3а (f2mraid.h)
#define GV_HANK_MOVED       "f2mhankm"  // 1 = Хэнк переставлен к начальнику охраны (0.6.4), 2 = на дорогу рядом с Риком (0.6.6, Егор 2026-10-08)
#define GV_BURY_ON          "f2mburon"  // 1 = идут похороны: людей у могилы не трогать (f2mbury.h, f2mhome.h)
#define GV_CAMP_FINE        "f2mcfine"  // штраф за стрельбу по своим в лагере, крышки (f2mfine.h)
#define GV_FINE_TALK        "f2mfntlk"  // 1 = герой уже уговаривал снизить этот штраф
#define GV_GRAVE_FIX        "f2mgrvfx"  // 1 = надгробие переставлено без чужого скрипта могилы (0.6.6)
#define GV_FENCE            "f2mfence"  // 1 = частокол вокруг лагеря построен (Хэнк)
#define GV_MIL_HIRED        "f2mmilhr"  // 1 = ополчение нанято у Рика
#define GV_COMP_STAY        "f2mcomps"  // 1 = герой ушел из лагеря, оставив там спутника
#define GV_RAID_AWAY        "f2mraway"  // 1 = герой ушел с карты лагеря (набег ждет, пока он там)
#define GV_RAID             "f2mraid1"  // первый набег: 0 не было, 1 был
#define GV_RAID_OUT         "f2mrout1"  // итог набега: RAID_OUT_* (f2mraid.h)
#define GV_RAID_HOUR        "f2mrhour"  // когда был набег: game_time / ONE_GAME_HOUR
#define GV_RAID_DECOR       "f2mrdeco"  // 1 = следы набега еще не расставлены на карте лагеря
#define GV_RAID_FOOD        "f2mrfood"  // сколько пайков еды унесли
#define GV_RAID_WATER       "f2mrwatr"  // сколько пайков воды унесли
#define GV_RAID_TENTS       "f2mrtent"  // биты мест палаток прораба (3-7), которые сломали
#define GV_RAID_DEAD        "f2mrdead"  // PID погибшего жителя (0 — никто не погиб)
#define GV_RAID_BURY        "f2mrbury"  // 1 = погибшего похоронили
#define GV_RAID_TOLD        "f2mrtold"  // 1 = Тед рассказал о набеге; 2 = и Рик тоже
#define GV_RAID_TRACK       "f2mrtrck"  // следы: 1 прочитаны (намек на логово), 2 не вышло
#define GV_RAID_PAID        "f2mrpaid"  // 1 = унесенные запасы восполнили деньгами
#define GV_RAID_NEXT        "f2mrnext"  // на сколько налетчиков следующий набег сильнее
#define GV_WAGON            "f2mwagon"  // 1 = фургон угнан (Тед купит новый с ближайшим караваном)
#define GV_BOSS             "f2mboss1"  // главарь у ворот: BOSS_* ниже
#define GV_BOSS_WEAK        "f2mbweak"  // 1 = Кейн проговорился про погреб (путь с динамитом в 1.4)
#define GV_BOSS_NOTE        "f2mbnote"  // 1 = герой обыскал Кейна и знает, где логово; 2 = обыскал Рик, пока героя не было (сказать при входе)

// Ворота частокола в южной стене (x 97-104, f2mfence.h): клетка внутри у ворот и снаружи перед ними
#define RAID_GATE_IN        (32500)     // x 100, y 162: тут встает ополчение
#define RAID_GATE_OUT       (34500)     // x 100, y 172: тут встает Кейн

#define BOSS_NONE           (0)
#define BOSS_WAIT           (1)     // стоит у ворот, ждет разговора
#define BOSS_LEFT           (2)     // герой отказал, банда ушла
#define BOSS_FIGHT          (3)     // бой у ворот
#define BOSS_BEATEN         (4)     // бой кончился: Кейн убит или банда разбежалась
#define PID_MILITIA_MALE    (16777575)  // ополчение Рика (1.3)
#define PID_MILITIA_FEMALE  (16777427)
// Штраф за стрельбу по своим в лагере (Егор 2026-10-08): ранение 500, убийство 2000, брамин 500
#define CAMP_FINE_HIT       (500)
#define CAMP_FINE_KILL      (2000)
#define camp_fine_add(n)    if (cur_map_index == MAP_F2MOD_CAMP) then set_sfall_global(GV_CAMP_FINE, get_sfall_global_int(GV_CAMP_FINE) + (n))
// Прицельно ранил своего, пока лагерь не воюет: штраф за ранение (убитому — за убийство в destroy_p_proc)
#define camp_fine_wound     if (not get_sfall_global_int(GV_CARAVAN_HOSTILE) and not is_critter_dead(self_obj)) then camp_fine_add(CAMP_FINE_HIT)
#define TEAM_F2M_GANG       (TEAM_RND_RAIDERS)
#define is_gang(c)          (obj_pid(c) == PID_RAIDER_MALE and has_trait(TRAIT_OBJECT, c, OBJECT_TEAM_NUM) == TEAM_F2M_GANG)
#define boss_fight_on       (cur_map_index == MAP_F2MOD_CAMP and get_sfall_global_int(GV_BOSS) == BOSS_FIGHT)

// Отладочные сообщения в окне игры (на время тестов)
#define F2MOD_DEBUG

#endif
