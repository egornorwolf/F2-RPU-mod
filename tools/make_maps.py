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
