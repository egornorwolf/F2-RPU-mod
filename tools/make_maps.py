#!/usr/bin/env python3
"""Карты мода. Карта лагеря (М1) и карта встречи с караваном (М2) — копии пустынных карт desert1 и desert2
из RPU со своим именем и своим скриптом карты (без скрипта случайных встреч).

Использование: make_maps.py <base> <scripts.lst мода> <папка data сборки>
"""
import shutil
import struct
import sys

base, scripts_lst, out = sys.argv[1:4]


def script_index(name):
    lines = open(scripts_lst, encoding="cp1251").read().splitlines()
    for i, line in enumerate(lines):
        if line.split(";")[0].strip().lower() == name:
            return i + 1  # в заголовке карты номер строки с 1, 0 значит «без скрипта»
    sys.exit(f"нет {name} в scripts.lst")


def make(src, dst, script):
    data = bytearray(open(f"{base}/maps/{src}.map", "rb").read())
    data[4:20] = f"{dst.upper()}.MAP".encode("ascii").ljust(16, b"\0")
    struct.pack_into(">i", data, 36, script_index(script))  # 20 вход, 24 уровень, 28 поворот, 32 число переменных, 36 скрипт
    open(f"{out}/maps/{dst}.map", "wb").write(data)
    shutil.copy(f"{base}/maps/{src}.edg", f"{out}/maps/{dst}.edg")


make("desert1", "f2mcamp", "f2mcamp.int")
make("desert2", "f2mcrvn", "f2mcrvn.int")
make("desert3", "f2mesct", "f2mesct.int")
make("desert2", "f2mesc2", "f2mesct.int")  # 2-й участок дороги
make("desert1", "f2mesc3", "f2mesct.int")  # 3-й участок дороги
make("desert2", "f2mremn", "f2mremn.int")  # остатки банды (1.4б)

# Карьер (логово налетчиков, 1.4): копия горной карты mountn5 из RPU (палатки у скалы). Герой входит с юго-востока,
# за деревьями (LAIR_HERO из f2mlairl.h, точки пишет tools/layout/lair_emit.py), лицом к лагерю
import os, re
_lay = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts_src", "f2mlairl.h"), encoding="utf-8").read()
make("mountn5", "f2mlair", "f2mlair.int")
_lair = f"{out}/maps/f2mlair.map"
_d = bytearray(open(_lair, "rb").read())
struct.pack_into(">i", _d, 20, int(re.search(r"#define LAIR_HERO\s+\((\d+)\)", _lay).group(1)))
struct.pack_into(">i", _d, 28, 5)
open(_lair, "wb").write(_d)


# Погреб под логовом (1.4): карту f2mcell пишет tools/layout/cellar_emit.py (копия пещеры CAVE7 без выходов
# на карту мира), здесь только номер скрипта и точка, куда спускается герой
_celll = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts_src", "f2mcelll.h"), encoding="utf-8").read()
cell = f"{out}/maps/f2mcell.map"
_d = bytearray(open(cell, "rb").read())
struct.pack_into(">i", _d, 36, script_index("f2mcell.int"))
struct.pack_into(">i", _d, 20, int(re.search(r"#define CELL_HERO\s+\((\d+)\)", _celll).group(1)))
struct.pack_into(">i", _d, 28, 2)
open(cell, "wb").write(_d)

# Лагерь у скал на карте города (0.5.0): пол и выходы пишет tools/layout/settle_emit.py, здесь только номер скрипта
settle = f"{out}/maps/f2mset.map"
data = bytearray(open(settle, "rb").read())
struct.pack_into(">i", data, 36, script_index("f2mcamp.int"))
open(settle, "wb").write(data)

# Песочница стройки (тест): карту пишет tools/layout/town_emit.py, здесь только номер скрипта карты
test_map = f"{out}/../test/maps/f2mtown.map"
data = bytearray(open(test_map, "rb").read())
struct.pack_into(">i", data, 36, script_index("f2mtown.int"))
open(test_map, "wb").write(data)
