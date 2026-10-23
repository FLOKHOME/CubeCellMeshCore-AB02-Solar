/**
 * Config.h - EEPROM configuration management for CubeCellMeshCore
 *
 * Handles loading, saving and resetting of node configuration
 */

#pragma once

#include <Arduino.h>
#include <EEPROM.h>
#include "globals.h"

//=============================================================================
// EEPROM Configuration defines
//
// Previously duplicated from main.h with a DIFFERENT EEPROM_SIZE (576 here,
// 640 in main.h). Because this translation unit only saw the local value, the
// runtime EEPROM window was 576 bytes while the region map writes up to offset
// 580 - the EEPROM emulation drops such writes silently and still reports a
// successful commit, so the 5th region lost its flags byte and part of its
// name on every reboot. All layout constants now live in StorageLayout.h.
//=============================================================================
#include "StorageLayout.h"


//=============================================================================
// Loop Detection Modes
//=============================================================================
#define LOOP_DETECT_OFF       0  // No loop detection (allow unlimited)
#define LOOP_DETECT_MINIMAL   1  // Minimal: allow 4+ repeats in path
#define LOOP_DETECT_MODERATE  2  // Moderate: allow 2+ repeats
#define LOOP_DETECT_STRICT    3  // Strict: allow only 1 occurrence (original behavior)

//=============================================================================
// NodeConfig structure - defined once in StorageLayout.h (included above).
//=============================================================================

// Default configuration - declared extern, defined in Config.cpp
extern const NodeConfig defaultConfig;

//=============================================================================
// Persistent Statistics - offsets, magic, version and save interval come from
// StorageLayout.h. The local fallbacks previously used a save interval of
// 5 minutes, which is what actually took effect (288 full flash commits per
// day); the 30 minute value in main.h never reached this translation unit.
//=============================================================================

//=============================================================================
// Configuration Functions
//=============================================================================

void loadConfig();
void saveConfig();
void resetConfig();

//=============================================================================
// Persistent Statistics Functions
//=============================================================================

void loadPersistentStats();
void savePersistentStats();
void checkStatsSave();

// Stat recording functions
void statsRecordRx();
void statsRecordTx();
void statsRecordFwd();
void statsRecordUniqueNode();
void statsRecordLogin();
void statsRecordLoginFail();
void statsRecordRateLimited();
void statsSetFirstBootTime(uint32_t unixTime);
// Remember/restore the time of the last ADVERT we sent (Unix time, 0=unknown).
void statsSetLastAdvertUnix(uint32_t unixTime);
uint32_t statsGetLastAdvertUnix();
uint32_t statsGetTotalUptime();
const PersistentStats* getPersistentStats();
