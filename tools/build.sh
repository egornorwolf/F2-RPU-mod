#!/usr/bin/env bash
# Сборка мода: компилирует скрипты и упаковывает всё в build/f2mod.dat.
# Нужны git, cmake, gcc с 32-битной поддержкой (gcc-multilib) и python3.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEPS="$ROOT/.deps"
OUT="$ROOT/build"
mkdir -p "$DEPS"

# Компилятор sfall и заголовки sfall
if [ ! -x "$DEPS/sslc/build/bin/sslc" ]; then
  git clone -q --depth 1 https://github.com/sfall-team/sslc.git "$DEPS/sslc"
  cmake -S "$DEPS/sslc" -B "$DEPS/sslc/build" -DCMAKE_BUILD_TYPE=Release >/dev/null
  make -s -C "$DEPS/sslc/build" -j"$(nproc)"
fi
if [ ! -f "$DEPS/sfall/artifacts/scripting/headers/sfall.h" ]; then
  git clone -q --depth 1 --filter=blob:none --sparse https://github.com/sfall-team/sfall.git "$DEPS/sfall"
  git -C "$DEPS/sfall" sparse-checkout set artifacts/scripting
fi
# Заголовки RPU (только читаем, не меняем)
if [ ! -f "$DEPS/rpu/scripts_src/headers/define.h" ]; then
  git clone -q --depth 1 --filter=blob:none --sparse https://github.com/BGforgeNet/Fallout2_Restoration_Project.git "$DEPS/rpu"
  git -C "$DEPS/rpu" sparse-checkout set scripts_src/headers scripts_src/sfall
fi
SSLC="$DEPS/sslc/build/bin/sslc"
RPU_HEADERS="$DEPS/rpu/scripts_src/headers"
HEADERS="$DEPS/sfall/artifacts/scripting/headers"

rm -rf "$OUT"
mkdir -p "$OUT/tmp" "$OUT/data/scripts"

# Исходники в UTF-8, игра ждёт cp1251: перекодируем перед компиляцией
for src in "$ROOT"/scripts_src/*.ssl; do
  name="$(basename "$src" .ssl)"
  iconv -f UTF-8 -t CP1251 "$src" > "$OUT/tmp/$name.ssl"
  (cd "$OUT/tmp" && "$SSLC" -q -l -p -O2 -I"$HEADERS" -I"$RPU_HEADERS" -I"$ROOT/scripts_src" "$name.ssl" -o "$OUT/data/scripts/$name.int")
done

python3 "$ROOT/tools/dat2.py" pack "$OUT/data" "$OUT/f2mod.dat"
rm -rf "$OUT/tmp"
echo "Готово: $OUT/f2mod.dat"
