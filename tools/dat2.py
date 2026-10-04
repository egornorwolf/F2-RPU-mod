#!/usr/bin/env python3
"""Упаковка папки в архив Fallout 2 (.dat, формат DAT2) и чтение списка файлов.

Использование:
  dat2.py pack <папка> <архив.dat>
  dat2.py list <архив.dat>
  dat2.py extract <архив.dat> <путь в архиве> <файл>
"""
import os
import struct
import sys
import zlib


def pack(src, out):
    entries = []
    blob = bytearray()
    for root, _, files in os.walk(src):
        for name in sorted(files):
            full = os.path.join(root, name)
            rel = os.path.relpath(full, src).replace("/", "\\")
            data = open(full, "rb").read()
            packed = zlib.compress(data, 9)
            if len(packed) < len(data):
                comp, payload = 1, packed
            else:
                comp, payload = 0, data
            entries.append((rel, comp, len(data), len(payload), len(blob)))
            blob += payload
    tree = bytearray(struct.pack("<I", len(entries)))
    for rel, comp, real, size, off in sorted(entries, key=lambda e: e[0].lower()):
        name = rel.encode("ascii")
        tree += struct.pack("<I", len(name)) + name + struct.pack("<BIII", comp, real, size, off)
    total = len(blob) + len(tree) + 8
    with open(out, "wb") as f:
        f.write(blob)
        f.write(tree)
        f.write(struct.pack("<II", len(tree), total))
    return len(entries)


def read_tree(path):
    with open(path, "rb") as f:
        f.seek(-8, 2)
        tree_size, total = struct.unpack("<II", f.read(8))
        f.seek(total - 8 - tree_size)
        data = f.read(tree_size)
    count = struct.unpack("<I", data[:4])[0]
    pos = 4
    for _ in range(count):
        n = struct.unpack("<I", data[pos:pos + 4])[0]
        pos += 4
        name = data[pos:pos + n].decode("ascii")
        pos += n
        comp, real, size, off = struct.unpack("<BIII", data[pos:pos + 13])
        pos += 13
        yield name, comp, real, size, off


def listing(path):
    for name, comp, real, _, _ in read_tree(path):
        print(f"{name}\t{real}\t{'zlib' if comp else 'raw'}")


def extract(path, inner, out):
    for name, comp, _, size, off in read_tree(path):
        if name.lower() == inner.lower():
            with open(path, "rb") as f:
                f.seek(off)
                data = f.read(size)
            open(out, "wb").write(zlib.decompress(data) if comp else data)
            return
    sys.exit(f"нет файла {inner} в {path}")


if __name__ == "__main__":
    if sys.argv[1] == "pack":
        print(pack(sys.argv[2], sys.argv[3]), "files")
    elif sys.argv[1] == "extract":
        extract(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        listing(sys.argv[2])
