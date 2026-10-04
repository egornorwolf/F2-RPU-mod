# F2-RPU-mod

Мод «Поселение» для Fallout 2 (Restoration Project). Строительство поселения, караваны, оборона и набеги.

- Дизайн-документ: [docs/design.md](docs/design.md)
- План карты: [docs/map-plan.md](docs/map-plan.md)
- Рост и цены: [docs/growth.md](docs/growth.md)
- Здания: [docs/buildings.md](docs/buildings.md)
- Спутники: [docs/companions.md](docs/companions.md)
- События и пасхалки: [docs/events.md](docs/events.md)
- Питомцы: [docs/tamed-creatures.md](docs/tamed-creatures.md)
- Реплики налетчиков: [docs/raiders-dialogs.md](docs/raiders-dialogs.md)
- Турели: [docs/turrets.md](docs/turrets.md)
- Механик Братства и силовая броня: [docs/power-armor.md](docs/power-armor.md)
- Охрана: численность, броня, оружие: [docs/guards.md](docs/guards.md)
- Фразы жителей: [docs/resident-phrases.md](docs/resident-phrases.md)
- Нашествие роботов и свои роботы: [docs/robots.md](docs/robots.md)
- План реализации: [docs/implementation-plan.md](docs/implementation-plan.md)
- Экономика: [docs/economy.md](docs/economy.md)
- Все квесты: [docs/quests.md](docs/quests.md)

## Сборка

`tools/build.sh` компилирует скрипты (`scripts_src/`) компилятором sfall и упаковывает все в `build/f2mod.dat`. Нужны git, cmake, gcc с 32-битной поддержкой (`gcc-multilib`), iconv и python3. Компилятор и заголовки sfall скачиваются в `.deps/` при первой сборке.

## Установка

1. Скопировать `f2mod.dat` в папку `mods` игры (у Эгора `D:\Projects\F2mod\RPU\mods`).
2. Добавить строку `f2mod.dat` в конец `mods\mods_order.txt`.

## Тестовые клавиши (только для проверки)

`build/f2mod_test.dat` ставится так же, как основной: в `mods` и строкой `f2mod_test.dat` в `mods_order.txt`. Для релиза файл просто убрать.

| Клавиши | Что делает |
|---|---|
| Ctrl+1…7 | СПЕЦИАЛ +1 (Сила, Восприятие, Выносливость, Привлекательность, Интеллект, Ловкость, Удача) |
| Ctrl+Shift+1…7 | СПЕЦИАЛ −1 |
| Ctrl+K | +10 очков навыков (раздать в окне персонажа) |
| Ctrl+N | все навыки 300% |
| Ctrl+E | открыть «Лагерь у скал» на карте мира |
| Ctrl+R | сбросить встречу с караваном: лагерь снова скрыт, караван ждет на следующей случайной встрече |
| Ctrl+B | переносимый вес +100 фунтов за нажатие (игра не дает больше 999) |
| Ctrl+O | +1 перк |
| Ctrl+U | +1 уровень |
| Ctrl+H | полное лечение |
| Ctrl+I | сундук рядом с героем: вся броня, все стрелковое и энергетическое оружие, гранаты, все патроны по 10 пачек, 30 стимпаков и 20 суперстимпаков |
| Ctrl+M | +5000 крышек |
| Ctrl+G | справка в окне сообщений |
