# Модели НПС (предложение 2026-10-07)

Все модели из `critter.dat` (FID из `artfid.h`). Колонка «оружие» это коды видов оружия, для которых у модели есть анимация стойки (D нож, E дубина, F молот, G копье, H пистолет, I пистолет-пулемет, J винтовка, K тяжелое, L пулемет, M ракетница). Картинка: [npc_models.png](/mnt/project-files/f2mod/pictures-models/npc_models.png), все модели: [all_models.png](/mnt/project-files/f2mod/pictures-models/all_models.png).

| НПС | Модель | Оружие |
|---|---|---|
| Тед Бернс | NMBSNP (утв.) | E I |
| Хэнк, прораб | NMLTHR | E G H J |
| Рик, начальник охраны | HMCMBT | все D-M |
| Охранники | HMLTHR, NMMAXZ, HFLTHR | все D-M |
| Старший фермер | NMBRLP | D J |
| Лавочник | NMFATT | D H J |
| Механик | NMMAXX | D H I |
| Бармен | NMPEAS | D E H |
| Доктор | NMDOCC | без оружия |
| Оружейник | NMMETB | все D-M |
| Бронник | NFMETL | D G |
| Барахольщик | NMLOSR | без оружия |
| Радист | NMLABB | H |
| Инструктор | HMMETL | все D-M |
| Говорящий цветок | MAPLNR (красноватое споровое растение) | без оружия |
| Отто Келлер | NAROBE (утв.); после квеста с броней меняем на паладина HAPOWR («сделал себе из остатков») | D G, у HAPOWR все D-M |
| Пациент с гипсом | NMOLDD | H J |
| Парень в свитере | NMBPEA (Житель 1, оранжевый свитер) | D F J |
| Жители | NMBPEA, NFPEAS, NFBRLP, NMASIA, NMPEAS, NFVALT | по модели |
| Главарь налетчиков | NMMETB | все D-M |
| Налетчики | NMLTBB, NMMAXZ, NMRGNG | все / D H I J K |
| Караванщики | NMMEXI | D H I J |
| Глава мафии / бойцы | NMNICE / NMBRSR, NMBONC | D H I / J |
| Работорговец | NMRGNG | D H I J K |
| Отшельник-стрелок | NMKROM | G H I J |
| Химик в фургоне | NMMYRN | D H |
| Дезертир | NMCOPP | H I J K |
| Рокки | NMBOXX | кулаки |
| Беглый раб | NMPRMB | G |
| Вор | NFTRMP | D H |
| Хорриган, паладины, Анклав | MABOSS, HAPOWR, HANPWR (утв.) | по [military-base.md](military-base.md) |

Правило: бойцам (охрана, налетчики, оружейник, Рик, инструктор) даем модели с полным набором D-M. Торговцам и жителям оружие только из колонки, иначе движок не покажет выстрел.
