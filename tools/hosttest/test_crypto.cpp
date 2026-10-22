// Host test for the MAC-then-decrypt buffer overflow in src/mesh/Crypto.h.
//
// Compiles the *real* firmware header against the portable Crypto library.
// Run twice: once against the fixed tree and once against the original one
// (-DOLD_CRYPTO -I <base>/src) to show the difference.
// In the firmware these come from mesh/Repeater.h, which is included before
// Crypto.h by core/globals.h; the host test provides them directly.
#define PERM_ACL_NONE    0x00
#define PERM_ACL_ADMIN   0x01
#define PERM_ACL_GUEST   0x02
#define MAX_CLIENT_SESSIONS 8

#include "mesh/Crypto.h"

#include <cstdio>
#include <cstring>

static const uint8_t KEY[MC_SHARED_SECRET_SIZE] = {
    0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88,
    0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00,
    0x0F, 0x1E, 0x2D, 0x3C, 0x4B, 0x5A, 0x69, 0x78,
    0x87, 0x96, 0xA5, 0xB4, 0xC3, 0xD2, 0xE1, 0xF0
};

// The 128 byte output buffer used by decryptAnonReq() and the two callers in
// main.cpp, followed by a canary to detect any write beyond it.
struct Guarded {
    uint8_t out[128];
    uint8_t canary[32];
};

static int failures = 0;

static void check(bool ok, const char* what) {
    printf("  %-58s %s\n", what, ok ? "ok" : "FAILED");
    if (!ok) failures++;
}

static uint16_t decCall(uint8_t* out, const uint8_t* in, uint16_t len, uint16_t maxOut) {
#ifdef OLD_CRYPTO
    (void)maxOut;
    return MeshCrypto().MACThenDecrypt(out, in, len, KEY, KEY);
#else
    return MeshCrypto().MACThenDecrypt(out, in, len, KEY, KEY, maxOut);
#endif
}

int main() {
#ifdef OLD_CRYPTO
    printf("== original Crypto.h (base commit) ==\n");
#else
    printf("== fixed Crypto.h ==\n");
#endif

    // ---- 1) normal traffic still round-trips -----------------------------
    const char* msg = "harsum01-password";
    uint8_t plain[64];
    memcpy(plain, msg, strlen(msg));
    uint16_t plainLen = (uint16_t)strlen(msg);

    uint8_t enc[256];
    uint16_t encLen = MeshCrypto().encryptThenMAC(enc, plain, plainLen, KEY, KEY);
    printf("  plaintext %u bytes -> encrypted %u bytes\n", plainLen, encLen);

    Guarded g;
    memset(&g, 0xAA, sizeof(g));
    uint16_t got = decCall(g.out, enc, encLen, sizeof(g.out));
    check(got == plainLen || (got >= plainLen && got % 16 == 0),
          "legit packet decrypts (returns padded length)");
    check(got > 0 && memcmp(g.out, plain, plainLen) == 0, "legit packet content matches");
    bool canaryOk = true;
    for (size_t i = 0; i < sizeof(g.canary); i++) if (g.canary[i] != 0xAA) canaryOk = false;
    check(canaryOk, "no write past the 128 byte buffer for legit input");

    // ---- 2) the attack: huge ciphertext with a valid MAC -----------------
    // cipherLen = len - 2, so 147 gives 145 bytes = 9 full blocks + 1 byte.
    // The old code wrote a full 16 byte block for the partial tail as well.
    uint8_t attack[147];
    memset(&attack[MC_CIPHER_MAC_SIZE], 0x5A, 147 - MC_CIPHER_MAC_SIZE);
    MeshCrypto::computeHMAC(attack, KEY, &attack[MC_CIPHER_MAC_SIZE],
                            (uint16_t)(147 - MC_CIPHER_MAC_SIZE));

    Guarded a;
    memset(&a, 0xAA, sizeof(a));
    uint16_t attackRet = decCall(a.out, attack, sizeof(attack), sizeof(a.out));
    bool attackCanary = true;
    for (size_t i = 0; i < sizeof(a.canary); i++) if (a.canary[i] != 0xAA) attackCanary = false;

    printf("  oversized packet: cipherLen=%u, return=%u, canary intact=%s\n",
           (unsigned)(sizeof(attack) - MC_CIPHER_MAC_SIZE), attackRet,
           attackCanary ? "yes" : "NO");

    // ---- 3) empty input no longer encrypts uninitialised memory ----------
    uint8_t e1[64], e2[64];
    memset(e1, 0, sizeof(e1));
    memset(e2, 0, sizeof(e2));
    uint16_t l1 = MeshCrypto().encryptThenMAC(e1, plain, 0, KEY, KEY);
    uint16_t l2 = MeshCrypto().encryptThenMAC(e2, plain, 0, KEY, KEY);
    // 2 bytes MAC + one padded block
    check(l1 == 18 && l2 == 18, "zero-length input pads to one block (+MAC)");
    check(memcmp(e1, e2, l1) == 0, "zero-length input is reproducible");

    // The padded block must be zeroed, i.e. identical to encrypting 16 zero
    // bytes. Before the fix zeroPad() returned 16 without writing anything, so
    // whatever was on the stack got encrypted and transmitted.
    uint8_t zeros16[16] = {0};
    uint8_t ref[64];
    uint16_t lref = MeshCrypto().encryptThenMAC(ref, zeros16, 16, KEY, KEY);
    check(l1 == lref && memcmp(e1, ref, lref) == 0,
          "zero-length input encrypts as a zero block (no stack leak)");

#ifdef OLD_CRYPTO
    printf("\n  => overflow detected: %s\n", attackCanary ? "no" : "YES (canary clobbered)");
#else
    check(attackCanary, "ATTACK BLOCKED: nothing written past the output buffer");
#endif

    printf("%s\n", failures ? "\nFAILED" : "");
    return failures ? 1 : 0;
}
