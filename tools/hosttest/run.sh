#!/usr/bin/env bash
#
# Host test for the MAC-then-decrypt buffer handling in src/mesh/Crypto.h.
#
# Compiles the *real* firmware header against the portable Crypto library and
# checks that
#   - normal traffic still round-trips,
#   - an oversized ciphertext (the crafted ANON_REQ case) is rejected instead of
#     writing past the 128 byte output buffer,
#   - a zero-length input encrypts a zeroed block instead of uninitialised stack.
#
# Usage:
#   tools/hosttest/run.sh                 # test the working tree
#   tools/hosttest/run.sh <commit>        # ... and the given commit for comparison
#
# Requires g++ and a finished PlatformIO build (the Crypto library then lives in
# .pio/libdeps/<env>/Crypto).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ENV_NAME="${PIOENV:-cubecell_board_plus}"
LIBC="$ROOT/.pio/libdeps/$ENV_NAME/Crypto"
BUILD="$ROOT/tools/hosttest/build"
BASE_COMMIT="${1:-}"

if [ ! -d "$LIBC" ]; then
    echo "error: $LIBC not found - run 'pio run' once so PlatformIO fetches the libraries" >&2
    exit 1
fi

mkdir -p "$BUILD"

# --- ed25519 (C) ------------------------------------------------------------
for f in fe ge sc sha512 sign verify keypair key_exchange ge_scalarmult_base_compact; do
    gcc -c -O1 -w -include string.h -I "$ROOT/lib/ed25519/src" \
        -o "$BUILD/ed_$f.o" "$ROOT/lib/ed25519/src/$f.c"
done

# --- portable Crypto library (AES-128 + SHA-256 + clean) --------------------
for f in AES128 AESCommon BlockCipher SHA256 Hash Crypto; do
    g++ -c -O1 -w -I "$ROOT/tools/hosttest/stubs" -I "$LIBC" \
        -o "$BUILD/lib_$f.o" "$LIBC/$f.cpp"
done

build_and_run() {
    local tag="$1" src_root="$2" extra="$3"
    # shellcheck disable=SC2086
    g++ -std=gnu++11 -O1 -w $extra \
        -o "$BUILD/test_$tag" "$ROOT/tools/hosttest/test_crypto.cpp" \
        "$BUILD"/ed_*.o "$BUILD"/lib_*.o \
        -I "$ROOT/tools/hosttest/stubs" -I "$src_root" -I "$LIBC" -I "$ROOT/lib/ed25519/src"
    echo "=== $tag ==="
    "$BUILD/test_$tag" || true
    echo
}

build_and_run fixed "$ROOT/src" ""

if [ -n "$BASE_COMMIT" ]; then
    BASE_DIR="$BUILD/base-$BASE_COMMIT"
    rm -rf "$BASE_DIR"; mkdir -p "$BASE_DIR"
    git -C "$ROOT" archive "$BASE_COMMIT" src | tar -x -C "$BASE_DIR"
    build_and_run "base-$BASE_COMMIT" "$BASE_DIR/src" "-DOLD_CRYPTO"
fi
