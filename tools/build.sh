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

# Шрифт игры не знает букву «ё» (показывает запятую): в текстах мода ее быть не должно
if grep -rlE "ё|Ё" "$ROOT/scripts_src" "$ROOT/mod"; then
  echo "Ошибка: в файлах выше есть буква «ё», замените на «е»." >&2
  exit 1
fi

rm -rf "$OUT"
mkdir -p "$OUT/tmp" "$OUT/data/scripts" "$OUT/test/scripts"
# sslc берёт только одну папку -I, поэтому заголовки RPU и sfall кладём рядом с исходником,
# а sfall ещё и в ../sfall, куда на него ссылается define.h из RPU
mkdir -p "$OUT/tmp/sfall" "$OUT/tmp/src"
cp "$HEADERS"/*.h "$OUT/tmp/sfall/"
cp "$RPU_HEADERS"/*.h "$HEADERS"/*.h "$ROOT"/scripts_src/*.h "$OUT/tmp/src/"

# Исходники в UTF-8, игра ждёт cp1251: перекодируем перед компиляцией
compile() {
  local src="$1" dest="$2" name
  name="$(basename "$src" .ssl)"
  iconv -f UTF-8 -t CP1251 "$src" > "$OUT/tmp/src/$name.ssl"
  (cd "$OUT/tmp/src" && "$SSLC" -q -l -p -O2 "$name.ssl" -o "$dest/$name.int")
}
for src in "$ROOT"/scripts_src/*.ssl "$ROOT"/scripts_src/maps/*.ssl "$ROOT"/scripts_src/critters/*.ssl; do compile "$src" "$OUT/data/scripts"; done
# Тестовые клавиши — отдельный f2mod_test.dat, в релиз не входит
for src in "$ROOT"/scripts_src/test/*.ssl; do compile "$src" "$OUT/test/scripts"; done

# Списки игры (city.txt, maps.txt, scripts.lst, map.msg): копия из RPU и наши строки в конце
BASE="$ROOT/base/rpu-2.4.34"
(cd "$ROOT/mod/append" && find . -type f) | while read -r rel; do
  mkdir -p "$OUT/data/$(dirname "$rel")"
  cp "$BASE/$rel" "$OUT/data/$rel"
  case "$rel" in
    *.msg) iconv -f UTF-8 -t CP1251 "$ROOT/mod/append/$rel" >> "$OUT/data/$rel" ;;
    *) cat "$ROOT/mod/append/$rel" >> "$OUT/data/$rel" ;;
  esac
done

# Свои файлы мода (диалоги и т. п.): .msg в UTF-8 перекодируем в cp1251 с переводом строк Windows
(cd "$ROOT/mod/data" && find . -type f) | while read -r rel; do
  mkdir -p "$OUT/data/$(dirname "$rel")"
  case "$rel" in
    *.msg) iconv -f UTF-8 -t CP1251 "$ROOT/mod/data/$rel" | sed 's/$/\r/' > "$OUT/data/$rel" ;;
    *) cp "$ROOT/mod/data/$rel" "$OUT/data/$rel" ;;
  esac
done

# Номера скриптов в f2mod.h должны совпадать со строками scripts.lst
python3 "$ROOT/tools/check_ids.py" "$ROOT/scripts_src/f2mod.h" "$OUT/data/scripts/scripts.lst"
python3 "$ROOT/tools/check_msgs.py" "$ROOT"

# Карты
mkdir -p "$OUT/data/maps"
python3 "$ROOT/tools/make_maps.py" "$BASE" "$OUT/data/scripts/scripts.lst" "$OUT/data"

python3 "$ROOT/tools/dat2.py" pack "$OUT/data" "$OUT/f2mod.dat"
python3 "$ROOT/tools/dat2.py" pack "$OUT/test" "$OUT/f2mod_test.dat"
rm -rf "$OUT/tmp"
echo "Готово: $OUT/f2mod.dat, $OUT/f2mod_test.dat"
