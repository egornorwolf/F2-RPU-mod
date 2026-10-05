#!/usr/bin/env python3
"""Сверяет номера строк, которые скрипты берут из своего .msg (mstr, Reply, NOption, floater(random(a, b))),
с файлами mod/data/text/russian/dialog/<скрипт>.msg (тестовые — mod/test/...). Ищет и дубли номеров в .msg."""
import glob
import os
import re
import sys

root = sys.argv[1]
msgdir = f"{root}/mod/data/text/russian/dialog"
bad = 0


def ids_in(path):
    ids, seen = set(), set()
    global bad
    for n in re.findall(r"^\{(\d+)\}", open(path, encoding="utf-8").read(), re.M):
        if n in seen:
            print(f"{os.path.basename(path)}: номер {n} повторяется")
            bad += 1
        seen.add(n)
        ids.add(int(n))
    return ids


def num(expr):
    expr = expr.strip()
    if re.fullmatch(r"[\d\s+\-]+", expr):
        return eval(expr)
    return None


for ssl in glob.glob(f"{root}/scripts_src/**/*.ssl", recursive=True):
    src = open(ssl, encoding="utf-8").read()
    if not re.search(r"#define\s+NAME\s", src):
        continue
    name = re.search(r'SCRIPT_REALNAME\s+"(\w+)"', src).group(1)
    msg = f"{msgdir}/{name}.msg"
    if "/test/" in ssl:  # тестовые скрипты: свои .msg в mod/test (f2mod_test.dat)
        msg = f"{root}/mod/test/text/russian/dialog/{name}.msg"
    if not os.path.exists(msg):
        print(f"{name}: нет файла {msg}")
        bad += 1
        continue
    have = ids_in(msg)
    want = set()
    for m in re.finditer(r"\b(?:mstr|Reply)\(([^()]*)\)", src):
        n = num(m.group(1))
        if n is not None:
            want.add(n)
    for m in re.finditer(r"\bN(?:Low)?Option\(\s*(\d+)\s*,", src):
        want.add(int(m.group(1)))
    for m in re.finditer(r"floater\(random\(([^,()]*),([^()]*)\)\)", src):
        a, b = num(m.group(1)), num(m.group(2))
        if a is not None and b is not None:
            want.update(range(a, b + 1))
    for n in sorted(want - have):
        print(f"{name}: в скрипте строка {n}, а в {name}.msg ее нет")
        bad += 1
sys.exit(1 if bad else 0)
