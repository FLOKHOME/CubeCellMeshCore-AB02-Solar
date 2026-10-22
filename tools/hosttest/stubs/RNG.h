// Minimal RNG stub for the host test (shadows the library's RNG.h).
#pragma once
#include <stdint.h>
#include <stddef.h>

class RNGClassStub {
public:
    void stir(const uint8_t*, size_t) {}
    void loop() {}
    void rand(uint8_t* out, size_t len) {
        for (size_t i = 0; i < len; i++) out[i] = (uint8_t)(0x30 + i);
    }
};
static RNGClassStub RNG;
