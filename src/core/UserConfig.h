/**
 * UserConfig.h - apply the configuration compiled in from config/repeater.json
 *
 * The JSON file is converted into firmware constants at build time by
 * tools/gen_user_config.py (see extra_scripts in platformio.ini); there is no
 * JSON parser in the firmware because the image is ~97% full. On the first
 * start - and whenever the file changed since the last apply - the values are
 * written into the EEPROM once, so no serial console session is needed after
 * flashing.
 */

#pragma once

#include <stdint.h>

/**
 * Apply the compiled-in user configuration.
 *
 * @param force  true  = apply even if the fingerprint already matches
 *                      (serial command "config apply")
 *               false = apply only when the configuration changed
 * @return true when settings were applied and persisted, false when the stored
 *         configuration was already up to date (or no JSON configuration was
 *         compiled in)
 */
bool applyCompiledUserConfig(bool force);

/** Fingerprint of the compiled-in configuration, 0 if none was compiled in. */
uint32_t getUserConfigFingerprint();

/** True when a configuration from config/repeater.json is part of this build. */
bool hasCompiledUserConfig();
