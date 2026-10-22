// Minimal Arduino stub so the real src/mesh/*.h can be compiled on the host.
#pragma once
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

typedef uint8_t byte;

static inline uint32_t millis() { return 0; }
static inline void delay(uint32_t) {}
static inline int analogRead(int) { return 0; }
static inline uint64_t getID() { return 0x1122334455667788ULL; }

struct SerialStub {
    int printf(const char*, ...) { return 0; }
    void print(const char*) {}
    void println(const char*) {}
};
static SerialStub Serial;
