# Расстановка лагеря

Скрипты для разметки карты лагеря и проверки ее картинкой (без игры).

- `mapparse.py` читает .map (формат по fallout2-ce: заголовок, тайлы, скрипты, объекты).
- `render.py` рисует кусок карты: пол и объекты из `master.dat` и `art` RPU.
- `tent.py` берет палатку (стены ybk/ylf/yrt, шесты, веревки) из `desert7.map`.
- `gen.py` — сама расстановка: точки `P`, постройки лагеря `L`, готовые постройки `DONE`.
- `emit.py` пишет `scripts_src/f2mlay.h`. `final.py` — картинки лагеря до и после стройки.

Нужны: `master.dat` (`/mnt/project-files/f2mod/game-data/`), клон RPU с `data/art` и `data/proto` в `/home/claude/rpu`,
`desert7.map` (достать из master.dat), Pillow.
