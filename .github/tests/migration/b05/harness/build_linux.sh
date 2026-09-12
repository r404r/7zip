#!/bin/sh
# B05-MAN Linux build script.
#
# Builds:
#   1. The unmodified retained 7z engine as a shared library (7z.so), from
#      CPP/7zip/Bundles/Format7zF, using the repository's own makefile.gcc
#      (no source changes).
#   2. The retained sample client's support objects, from
#      CPP/7zip/UI/Client7z, using the repository's own makefile.gcc.
#   3. This harness's own b05_password_harness.cpp, compiled with the SAME
#      compiler flags as Client7z.cpp (see makefile.gcc's g++ invocation),
#      using -I to reach Client7z's StdAfx.h so the retained relative
#      #include paths inside Common/Windows headers resolve unchanged.
#   4. Links the harness's object against Client7z's support objects
#      (everything Client7z.cpp itself links against, minus Client7z.o,
#      plus this harness's own object).
#
# This script does not modify any file under CPP/. It only reads from the
# repository and writes to $BUILD_DIR (default: ./b05-build, outside the
# repository tree is also fine -- pass any writable directory).
#
# Usage:
#   sh build_linux.sh <path-to-repo-root> [build-dir]
#
# Verified: this exact script (transcribed from the commands actually run)
# was exercised end-to-end on this task's Linux CI/dev host; see the
# runbook's "Linux self-check performed by the AI" appendix for the
# transcript. It has NOT been run on a second, independent Linux machine --
# the human's own Linux run in the runbook is the independent confirmation.

set -e

REPO="${1:?usage: build_linux.sh <repo-root> [build-dir]}"
BUILD="${2:-$(pwd)/b05-build}"

CLIENT7Z_DIR="$REPO/CPP/7zip/UI/Client7z"
FORMAT7ZF_DIR="$REPO/CPP/7zip/Bundles/Format7zF"
HARNESS_CPP="$REPO/.github/tests/migration/b05/harness/b05_password_harness.cpp"

if [ ! -f "$REPO/AGENTS.md" ]; then
  echo "error: $REPO does not look like the repository root (no AGENTS.md)" >&2
  exit 1
fi
if [ ! -f "$HARNESS_CPP" ]; then
  echo "error: harness source not found at $HARNESS_CPP" >&2
  exit 1
fi

mkdir -p "$BUILD/client7z_objs" "$BUILD/format7zf" "$BUILD/harness"

echo "== 1/4: building retained 7z engine (7z.so) from CPP/7zip/Bundles/Format7zF (unmodified) =="
( cd "$FORMAT7ZF_DIR" && make -f makefile.gcc O="$BUILD/format7zf" -j"$(nproc)" )
test -f "$BUILD/format7zf/7z.so" || { echo "error: 7z.so was not produced"; exit 1; }

echo "== 2/4: building retained Client7z support objects (unmodified) =="
( cd "$CLIENT7Z_DIR" && make -f makefile.gcc O="$BUILD/client7z_objs" -j"$(nproc)" )
test -f "$BUILD/client7z_objs/7zcl" || { echo "error: reference 7zcl was not produced"; exit 1; }

echo "== 3/4: compiling this harness's own .cpp (same flags as Client7z.cpp) =="
g++ -O2 -c -Wall -Wextra -DNDEBUG -D_REENTRANT -D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE -fPIC \
  -I "$CLIENT7Z_DIR" \
  -o "$BUILD/harness/b05_password_harness.o" \
  "$HARNESS_CPP"

echo "== 4/4: linking harness against Client7z's (unmodified) support objects =="
g++ -o "$BUILD/harness/b05_password_harness" -s -DNDEBUG -z noexecstack \
  "$BUILD/client7z_objs/Alloc.o" \
  "$BUILD/client7z_objs/IntToString.o" "$BUILD/client7z_objs/MyString.o" "$BUILD/client7z_objs/MyVector.o" \
  "$BUILD/client7z_objs/NewHandler.o" "$BUILD/client7z_objs/StringConvert.o" "$BUILD/client7z_objs/StringToInt.o" \
  "$BUILD/client7z_objs/UTFConvert.o" "$BUILD/client7z_objs/Wildcard.o" \
  "$BUILD/client7z_objs/DLL.o" "$BUILD/client7z_objs/FileDir.o" "$BUILD/client7z_objs/FileFind.o" \
  "$BUILD/client7z_objs/FileIO.o" "$BUILD/client7z_objs/FileName.o" "$BUILD/client7z_objs/PropVariant.o" \
  "$BUILD/client7z_objs/PropVariantConv.o" "$BUILD/client7z_objs/TimeUtils.o" \
  "$BUILD/client7z_objs/MyWindows.o" \
  "$BUILD/client7z_objs/FileStreams.o" \
  "$BUILD/harness/b05_password_harness.o" \
  -lpthread -ldl

cp "$BUILD/format7zf/7z.so" "$BUILD/harness/7z.so"

echo
echo "Build complete."
echo "Harness binary: $BUILD/harness/b05_password_harness"
echo "Engine library: $BUILD/harness/7z.so (must stay beside the harness binary)"
echo
echo "Self-check:"
"$BUILD/harness/b05_password_harness" selftest-leak
