/**
 * UserConfig.cpp - apply the configuration compiled in from config/repeater.json
 *
 * Called from setup() after the EEPROM, identity, advert generator, repeater
 * helper and region map have been initialised. Writes the settings into the
 * existing storage paths (identity block, NodeConfig, region map) and records
 * the configuration fingerprint, so the next start with an unchanged
 * config/repeater.json does nothing at all.
 */

#include "UserConfig.h"
#include "../generated/UserConfigData.h"

#if USERCFG_PRESENT

#include <Arduino.h>
#include "globals.h"
#include "Config.h"

// Tables generated from config/repeater.json
extern const char* const userCfgRegions[];
#if USERCFG_DENY_COUNT > 0
extern const char* const userCfgDenyFlood[];
#endif

#ifndef SILENT
#define UCFG_LOG(...) Serial.printf(__VA_ARGS__)
#else
#define UCFG_LOG(...)
#endif

static void applyRegions() {
    // The stored list is replaced completely, so removing a name from the JSON
    // also removes it from the repeater.
    regionMap.clear();

    for (uint8_t i = 0; i < USERCFG_REGION_COUNT; i++) {
        if (!regionMap.put(userCfgRegions[i])) {
            UCFG_LOG("[U] region '%s' not accepted\n\r", userCfgRegions[i]);
        }
    }

    // Clear region with an explicit deny entry first, then the wildcard default:
    // "*" listed in the config = flood without a region match is forwarded,
    // omitted = such packets are dropped.
    if (USERCFG_WILDCARD) regionMap.allowFlood("*");
    else                  regionMap.denyFlood("*");

#if USERCFG_DENY_COUNT > 0
    for (uint8_t i = 0; i < USERCFG_DENY_COUNT; i++) {
        if (!regionMap.denyFlood(userCfgDenyFlood[i])) {
            UCFG_LOG("[U] deny '%s' failed\n\r", userCfgDenyFlood[i]);
        }
    }
#endif

    if (!regionMap.save()) {
        UCFG_LOG("[U] region map not saved\n\r");
    }
}

bool applyCompiledUserConfig(bool force) {
    if (!force && storedUserConfigHash == USERCFG_FINGERPRINT) return false;

    UCFG_LOG("[U] apply %08lX\n\r", (unsigned long)USERCFG_FINGERPRINT);

    // --- Identity: name and location -------------------------------------
    bool identityChanged = false;
#if defined(USERCFG_NAME)
    if (USERCFG_NAME[0] != '\0' &&
        strcmp(nodeIdentity.getNodeName(), USERCFG_NAME) != 0) {
        nodeIdentity.setNodeName(USERCFG_NAME);
        identityChanged = true;
    }
#endif
#if USERCFG_HAS_LOCATION
    if (nodeIdentity.getLatitude() != USERCFG_LAT_E6 ||
        nodeIdentity.getLongitude() != USERCFG_LON_E6) {
        nodeIdentity.setLocationInt(USERCFG_LAT_E6, USERCFG_LON_E6);
        identityChanged = true;
    }
#endif
    if (identityChanged && !nodeIdentity.save()) {
        UCFG_LOG("[U] identity not saved\n\r");
    }

    // --- Regions ---------------------------------------------------------
    applyRegions();

    // --- Advertising -----------------------------------------------------
    advertGen.setInterval((uint32_t)USERCFG_ADV_LOCAL_MIN * 60000UL);
    floodAdvertIntervalMs = (uint32_t)USERCFG_ADV_FLOOD_HRS * 3600000UL;

    // --- Forwarding / loop detection -------------------------------------
    repeaterHelper.setMaxFloodHops(USERCFG_MAX_FLOOD_HOPS);
    loopDetectMode = USERCFG_LOOP_DETECT;
    autoAddMaxHops = USERCFG_AUTOADD_MAXHOPS;

    // --- Power -----------------------------------------------------------
    powerSaveMode = USERCFG_POWER_SAVING;
    deepSleepEnabled = (USERCFG_DEEP_SLEEP != 0);
    rxBoostEnabled = (USERCFG_RX_BOOST != 0);

    // --- Credentials (empty = keep what the EEPROM holds) ----------------
#if defined(USERCFG_ADMIN_PASSWORD)
    if (USERCFG_ADMIN_PASSWORD[0] != '\0') {
        sessionManager.setAdminPassword(USERCFG_ADMIN_PASSWORD);
        sessionManager.setGuestPassword(USERCFG_GUEST_PASSWORD);
    }
#endif

    // --- Persist ---------------------------------------------------------
    // saveConfig() stores the values above together with the fingerprint, so
    // the configuration is applied exactly once per JSON change.
    storedUserConfigHash = USERCFG_FINGERPRINT;
    saveConfig();
    return true;
}

uint32_t getUserConfigFingerprint() {
    return USERCFG_FINGERPRINT;
}

bool hasCompiledUserConfig() {
    return true;
}

#else   // no config/repeater.json in the build

bool applyCompiledUserConfig(bool force) {
    (void)force;
    return false;
}

uint32_t getUserConfigFingerprint() {
    return 0;
}

bool hasCompiledUserConfig() {
    return false;
}

#endif  // USERCFG_PRESENT
