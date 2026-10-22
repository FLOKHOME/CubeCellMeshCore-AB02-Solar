/**
 * StorageLayout.h - Single source of truth for the EEPROM/flash user area
 *
 * The CubeCell (ASR6501/ASR6502) EEPROM library emulates EEPROM in the
 * 3 x 256 byte user flash rows (768 bytes max). EEPROM.read()/write() and
 * EEPROM.get()/put() silently ignore any access outside the size passed to
 * EEPROM.begin(), and commit() still reports success. Therefore every
 * consumer of the layout must agree on the same size, otherwise data is
 * dropped without any error being reported.
 *
 * Include this header instead of re-declaring the constants locally.
 */

#pragma once

#include <stdint.h>

//=============================================================================
// Configuration block (NodeConfig) - offset 0
//=============================================================================
#define EEPROM_SIZE             640     // Must be >= STORAGE_LAYOUT_END
#define EEPROM_MAGIC            0xCC3C
#define EEPROM_VERSION          6       // Config version (6 = removed invalid region/scope fields)
#define CONFIG_EEPROM_OFFSET    0
#define CONFIG_PASSWORD_LEN     16
#define REPORT_PUBKEY_SIZE      32      // Ed25519 public key size

//=============================================================================
// Identity block (NodeIdentity) - offset 128, 132 bytes -> ends at 259
//=============================================================================
#define IDENTITY_EEPROM_OFFSET  128
#define MC_PRIVATE_KEY_SIZE     64
#define MC_PUBLIC_KEY_SIZE      32
#define MC_NODE_NAME_MAX        16
#define IDENTITY_STRUCT_SIZE    132     // sizeof(NodeIdentity); static_assert in Identity.h

//=============================================================================
// Persistent statistics block (PersistentStats) - offset 280, 52 bytes
//=============================================================================
#define STATS_EEPROM_OFFSET     280
#define STATS_EEPROM_MAGIC      0x5754  // "ST"
#define STATS_EEPROM_VERSION    1
#define STATS_STRUCT_SIZE       52      // sizeof(PersistentStats)
// 30 minutes. Every commit rewrites the whole buffer (flash wear), so keep
// this interval generous on a permanently powered solar node.
#define STATS_SAVE_INTERVAL_MS  1800000UL

//=============================================================================
// Region map block - offset 512, 69 bytes -> ends at 580
//=============================================================================
#define REGION_EEPROM_OFFSET    512
#define REGION_EEPROM_MAGIC     0x5247  // "RG"
#define REGION_MAX_ENTRIES      5
#define REGION_SAVE_NAME_LEN    12      // Compact name in EEPROM, 11 chars + NUL
#define REGION_SAVE_ENTRY_BYTES (REGION_SAVE_NAME_LEN + 1)
#define REGION_SAVE_HEADER_LEN  4       // magic(2) + count(1) + wildcard flags(1)
#define REGION_SAVE_BYTES       (REGION_SAVE_HEADER_LEN + REGION_MAX_ENTRIES * REGION_SAVE_ENTRY_BYTES)

//=============================================================================
// Layout consistency checks (compile time, no flash cost)
//=============================================================================
#define STORAGE_LAYOUT_END      (REGION_EEPROM_OFFSET + REGION_SAVE_BYTES)

#if STORAGE_LAYOUT_END > EEPROM_SIZE
#error "EEPROM_SIZE is smaller than the storage layout; region data would be dropped silently"
#endif

#if IDENTITY_EEPROM_OFFSET < CONFIG_EEPROM_OFFSET + 112
#error "Identity block overlaps the configuration block"
#endif

#if STATS_EEPROM_OFFSET < IDENTITY_EEPROM_OFFSET + IDENTITY_STRUCT_SIZE
#error "Statistics block overlaps the identity block - recheck EEPROM offsets"
#endif

#if REGION_EEPROM_OFFSET < STATS_EEPROM_OFFSET + STATS_STRUCT_SIZE
#error "Region map block overlaps the statistics block - recheck EEPROM offsets"
#endif

#if EEPROM_SIZE > 768
#error "EEPROM_SIZE exceeds the 3 user flash rows (768 bytes) available on ASR6501/ASR6502"
#endif

//=============================================================================
// Persisted structures
//
// Defined exactly once, here. Previously main.h and core/Config.h each had
// their own NodeConfig definition: same total size by coincidence, but the
// last four bytes meant "reserved[4]" in one translation unit and
// "maxFloodHops/advertIntervalMin/floodAdvertHrs/reserved1" in the other.
// Adding a field on one side would have silently corrupted the stored config.
//=============================================================================

#ifndef NODECONFIG_DEFINED
#define NODECONFIG_DEFINED
struct NodeConfig {
    uint16_t magic;                         // Magic number to validate
    uint8_t version;                        // Config version
    uint8_t powerSaveMode;                  // 0=perf, 1=balanced, 2=powersave
    bool rxBoostEnabled;
    bool deepSleepEnabled;
    char adminPassword[CONFIG_PASSWORD_LEN]; // Admin password (persistent)
    char guestPassword[CONFIG_PASSWORD_LEN]; // Guest password (persistent)
    // Daily report settings (v3)
    bool reportEnabled;                     // Daily report enabled
    uint8_t reportHour;                     // Hour to send report (0-23)
    uint8_t reportMinute;                   // Minute to send report (0-59)
    uint8_t reportDestPubKey[REPORT_PUBKEY_SIZE]; // Destination public key
    // Node alert settings (v4)
    bool alertEnabled;                      // Node alert enabled
    uint8_t alertDestPubKey[REPORT_PUBKEY_SIZE]; // Alert destination public key
    // Loop detection & auto-add (v5)
    uint8_t loopDetectMode;                 // 0=off, 1=minimal, 2=moderate, 3=strict
    uint8_t autoAddMaxHops;                 // 0=no limit, 1-64=max hops for auto-add contacts
    // Flood/advert tuning (v6)
    uint8_t maxFloodHops;                   // 0=default(8), 1-15=max flood hops
    uint8_t advertIntervalMin;              // 0=default(5), 1-240=advert interval in minutes
    uint8_t floodAdvertHrs;                 // 0=auto, 3-48=flood advert interval in hours
    uint8_t reserved1;                      // Reserved for future use
};
#endif

#ifndef PERSISTENTSTATS_DEFINED
#define PERSISTENTSTATS_DEFINED
struct PersistentStats {
    uint16_t magic;             // Magic number to validate
    uint8_t version;            // Stats version
    uint8_t reserved;           // Padding
    // Lifetime counters (never reset)
    uint32_t totalRxPackets;    // Total packets received
    uint32_t totalTxPackets;    // Total packets transmitted
    uint32_t totalFwdPackets;   // Total packets forwarded
    uint32_t totalUniqueNodes;  // Unique nodes ever seen
    uint32_t totalUptime;       // Total uptime in seconds
    uint32_t totalLogins;       // Total successful logins
    uint32_t totalLoginFails;   // Total failed login attempts
    uint32_t totalRateLimited;  // Total rate-limited requests
    uint16_t bootCount;         // Number of boots
    uint16_t lastBootReason;    // Last boot reason code
    uint32_t firstBootTime;     // Unix timestamp of first boot
    uint32_t lastSaveTime;      // Unix timestamp of last save
    uint16_t checksum;          // CRC16 of data
};
#endif

static_assert(sizeof(NodeConfig) == 112, "NodeConfig size changed - EEPROM layout needs a version bump");
static_assert(sizeof(PersistentStats) == 52, "PersistentStats size changed - EEPROM layout needs a version bump");
