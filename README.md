# F2-RPU-mod

Мод «Поселение» для Fallout 2 (Restoration Project). Строительство поселения, караваны, оборона и набеги.

- Дизайн-документ: [docs/design.md](docs/design.md)
- План карты: [docs/map-plan.md](docs/map-plan.md)
- Рост и цены: [docs/growth.md](docs/growth.md)
- Здания: [docs/buildings.md](docs/buildings.md)
- Спутники: [docs/companions.md](docs/companions.md)
- События и пасхалки: [docs/events.md](docs/events.md)
- Питомцы: [docs/tamed-creatures.md](docs/tamed-creatures.md)
- Реплики налётчиков: [docs/raiders-dialogs.md](docs/raiders-dialogs.md)
- Турели: [docs/turrets.md](docs/turrets.md)
- Механик Братства и силовая броня: [docs/power-armor.md](docs/power-armor.md)
- Охрана: численность, броня, оружие: [docs/guards.md](docs/guards.md)
- Фразы жителей: [docs/resident-phrases.md](docs/resident-phrases.md)
- Нашествие роботов и свои роботы: [docs/robots.md](docs/robots.md)
- План реализации: [docs/implementation-plan.md](docs/implementation-plan.md)
- Экономика: [docs/economy.md](docs/economy.md)
- Все квесты: [docs/quests.md](docs/quests.md)

## Сборка

`tools/build.sh` компилирует скрипты (`scripts_src/`) компилятором sfall и упаковывает всё в `build/f2mod.dat`. Нужны git, cmake, gcc с 32-битной поддержкой (`gcc-multilib`), iconv и python3. Компилятор и заголовки sfall скачиваются в `.deps/` при первой сборке.

## Установка

1. Скопировать `f2mod.dat` в папку `mods` игры (у Эгора `D:\Projects\F2mod\RPU\mods`).
2. Добавить строку `f2mod.dat` в конец `mods\mods_order.txt`.
