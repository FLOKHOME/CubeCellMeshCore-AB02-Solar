// Minimal EEPROM stub (the crypto paths under test do not touch it).
#pragma once
#include <stdint.h>
#include <string.h>
#include <stddef.h>

class EEPROMClassStub {
public:
    void begin(size_t) {}
    template <typename T> T& get(int, T& t) { return t; }
    template <typename T> const T& put(int, const T& t) { return t; }
    bool commit() { return true; }
};
static EEPROMClassStub EEPROM;
