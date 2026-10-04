#!/usr/bin/env python3
"""Сверяет номера всех SCRIPT_* из f2mod.h (наши и взятые из RPU) со строками scripts.lst (номер скрипта = номер строки с 1)."""
import re
import sys

header, lst = sys.argv[1:3]
lines = [l.split(";")[0].strip().lower() for l in open(lst, encoding="cp1251").read().splitlines()]
bad = 0
for name, num in re.findall(r"#define\s+SCRIPT_(\w+)\s+\((\d+)\)", open(header, encoding="utf-8").read()):
    want = f"{name.lower()}.int"
    got = lines[int(num) - 1] if int(num) <= len(lines) else "(нет строки)"
    if got != want:
        print(f"SCRIPT_{name} = {num}, а в этой строке scripts.lst: {got}; нужен {want}")
        bad += 1
sys.exit(1 if bad else 0)
