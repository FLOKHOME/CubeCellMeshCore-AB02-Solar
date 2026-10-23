#!/usr/bin/env python3
"""
gen_user_config.py - build config/repeater.json into the firmware.

Runs automatically before every PlatformIO build (see extra_scripts in
platformio.ini) and can be called by hand:

    py -3 tools\\gen_user_config.py                  (Windows)
    python3 tools/gen_user_config.py [--config FILE] [--check]

It validates config/repeater.json and writes two generated files:

    src/generated/UserConfigData.h   - compile-time defines (name, radio, ...)
    src/generated/UserConfigData.cpp - region name tables

There is deliberately NO JSON parser in the firmware: a parser plus the JSON
text would not fit into the remaining flash (the image is ~97% full). Parsing
at build time costs zero flash.

The fingerprint is an FNV-1a hash over the normalised JSON. It is written into
the firmware and compared against the value stored in the EEPROM; only when the
two differ (first start or after editing the file) are the settings applied and
persisted once.
"""

import argparse
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = None             # resolved lazily, see project_root()
DEFAULT_CONFIG_REL = Path("config") / "repeater.json"
GENERATED_REL = Path("src") / "generated"


def project_root():
    """Project directory, works both from the CLI and as a PlatformIO pre-script.

    PlatformIO/SCons executes this file with SCons globals injected and without
    __file__, so the path must not be derived from __file__ unconditionally.
    """
    global PROJECT_ROOT
    if PROJECT_ROOT is not None:
        return PROJECT_ROOT
    root = None
    try:
        Import("env")                      # noqa: F821 - injected by SCons
        try:
            root = Path(env.subst("$PROJECT_DIR"))   # noqa: F821
        except Exception:
            root = Path.cwd()
    except NameError:
        root = Path(__file__).resolve().parent.parent
    PROJECT_ROOT = root.resolve()
    return PROJECT_ROOT


def default_config():
    return project_root() / DEFAULT_CONFIG_REL


def generated_dir():
    return project_root() / GENERATED_REL

MAX_NAME_LEN = 15
MAX_REGION_NAME_LEN = 11        # REGION_SAVE_NAME_LEN (12) minus NUL
MAX_REGIONS = 5                 # REGION_MAX_ENTRIES
MAX_PASSWORD_LEN = 15           # CONFIG_PASSWORD_LEN (16) minus NUL

# Bandwidths the SX1262 supports (kHz) with the MeshCore/Narrow presets in mind
BW_CHOICES = [7.8, 10.4, 15.6, 20.8, 31.25, 41.7, 62.5, 125.0, 250.0, 500.0]

DEFAULTS = {
    "name": "",
    "location": {"latitude": 0.0, "longitude": 0.0},
    "radio": {
        "frequency_mhz": 869.618,
        "bandwidth_khz": 62.5,
        "spreading_factor": 8,
        "coding_rate": 8,
        "tx_power_dbm": 21,
        "preamble_len": 16,
    },
    "advertising": {"local_interval_minutes": 120, "flood_interval_hours": 6},
    "regions": {"allow": ["*"], "deny_flood": [], "default": ""},
    "network": {"max_flood_hops": 8, "loop_detect": 3, "auto_add_max_hops": 0,
                "path_hash_mode": 2},
    "power": {"power_saving": 1, "deep_sleep": True, "rx_boost": False},
    "security": {"admin_password": "", "guest_password": ""},
}


class ConfigError(Exception):
    pass


def _get(data, path, default):
    """Fetch a nested value, ignoring the '_comment' keys used in the file."""
    node = data
    for key in path.split("."):
        if not isinstance(node, dict) or key not in node:
            return default
        node = node[key]
    return node


def _num(value, what, lo, hi, integer=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError(f"{what}: expected a number, got {value!r}")
    if integer and int(value) != value:
        raise ConfigError(f"{what}: expected a whole number, got {value!r}")
    value = int(value) if integer else float(value)
    if not lo <= value <= hi:
        raise ConfigError(f"{what}: must be between {lo} and {hi}, got {value}")
    return value


def _bool(value, what):
    if not isinstance(value, bool):
        raise ConfigError(f"{what}: expected true or false, got {value!r}")
    return value


def _string(value, what, max_len=None):
    if not isinstance(value, str):
        raise ConfigError(f"{what}: expected a string, got {value!r}")
    if max_len is not None and len(value) > max_len:
        raise ConfigError(
            f"{what}: max {max_len} characters, got {len(value)} "
            f"({value!r}) - the firmware stores at most {max_len}")
    if any(ord(c) < 32 or ord(c) > 126 for c in value):
        raise ConfigError(f"{what}: only printable ASCII characters are allowed ({value!r})")
    if '"' in value or "\\" in value:
        raise ConfigError(f"{what}: quotes and backslashes are not allowed ({value!r})")
    return value


def validate(raw):
    """Validate the parsed JSON and return a normalised dict."""
    if not isinstance(raw, dict):
        raise ConfigError("top level of the configuration must be a JSON object")

    cfg = {
        "name": _string(_get(raw, "name", DEFAULTS["name"]), "name", MAX_NAME_LEN),
        "location": {},
        "radio": {},
        "advertising": {},
        "regions": {},
        "network": {},
        "power": {},
        "security": {},
    }

    lat = _num(_get(raw, "location.latitude", DEFAULTS["location"]["latitude"]),
               "location.latitude", -90.0, 90.0)
    lon = _num(_get(raw, "location.longitude", DEFAULTS["location"]["longitude"]),
               "location.longitude", -180.0, 180.0)
    cfg["location"] = {"latitude": lat, "longitude": lon,
                       "set": not (lat == 0.0 and lon == 0.0)}

    r = DEFAULTS["radio"]
    cfg["radio"] = {
        "frequency_mhz": _num(_get(raw, "radio.frequency_mhz", r["frequency_mhz"]),
                              "radio.frequency_mhz", 400.0, 960.0),
        "bandwidth_khz": None,
        "spreading_factor": _num(_get(raw, "radio.spreading_factor", r["spreading_factor"]),
                                 "radio.spreading_factor", 5, 12, integer=True),
        "coding_rate": _num(_get(raw, "radio.coding_rate", r["coding_rate"]),
                            "radio.coding_rate", 5, 8, integer=True),
        "tx_power_dbm": _num(_get(raw, "radio.tx_power_dbm", r["tx_power_dbm"]),
                             "radio.tx_power_dbm", -9, 22, integer=True),
        "preamble_len": _num(_get(raw, "radio.preamble_len", r["preamble_len"]),
                             "radio.preamble_len", 6, 32, integer=True),
    }
    bw = _num(_get(raw, "radio.bandwidth_khz", r["bandwidth_khz"]),
              "radio.bandwidth_khz", 7.8, 500.0)
    if not any(abs(bw - c) < 1e-6 for c in BW_CHOICES):
        raise ConfigError(
            f"radio.bandwidth_khz: {bw} is not a supported SX1262 bandwidth; "
            f"use one of {BW_CHOICES}")
    cfg["radio"]["bandwidth_khz"] = bw

    a = DEFAULTS["advertising"]
    flood_h = _num(_get(raw, "advertising.flood_interval_hours", a["flood_interval_hours"]),
                   "advertising.flood_interval_hours", 0, 48, integer=True)
    if 0 < flood_h < 3:
        raise ConfigError(
            "advertising.flood_interval_hours: 0 disables it, otherwise 3-48 is required "
            "(1-2 hours would flood the network)")
    cfg["advertising"] = {
        "local_interval_minutes": _num(
            _get(raw, "advertising.local_interval_minutes", a["local_interval_minutes"]),
            "advertising.local_interval_minutes", 1, 240, integer=True),
        "flood_interval_hours": flood_h,
    }

    allow = _get(raw, "regions.allow", DEFAULTS["regions"]["allow"])
    deny = _get(raw, "regions.deny_flood", DEFAULTS["regions"]["deny_flood"])
    default_region = _string(_get(raw, "regions.default", DEFAULTS["regions"]["default"]),
                             "regions.default", MAX_REGION_NAME_LEN)
    if not isinstance(allow, list) or not isinstance(deny, list):
        raise ConfigError("regions.allow and regions.deny_flood must be JSON arrays")

    wildcard = False
    names = []
    for i, entry in enumerate(allow):
        name = _string(entry, f"regions.allow[{i}]", MAX_REGION_NAME_LEN)
        if name == "*":
            wildcard = True
            continue
        if not name:
            raise ConfigError(f"regions.allow[{i}]: empty region name")
        if name not in names:
            names.append(name)
    if len(names) > MAX_REGIONS:
        raise ConfigError(
            f"regions.allow: {len(names)} named regions, at most {MAX_REGIONS} are supported "
            f"by this firmware")

    deny_entries = []
    for i, entry in enumerate(deny):
        name = _string(entry, f"regions.deny_flood[{i}]", MAX_REGION_NAME_LEN)
        if name == "*":
            if "*" in allow:
                raise ConfigError(
                    "regions: '*' is listed in both 'allow' and 'deny_flood' - leave it out of "
                    "'allow' to drop flood packets that match no named region")
            wildcard = True
            deny_entries.append("*")
            continue
        if name not in names:
            raise ConfigError(
                f"regions.deny_flood[{i}]: region {name!r} is not in regions.allow")
        if name not in deny_entries:
            deny_entries.append(name)

    if default_region and default_region not in names:
        raise ConfigError(
            f"regions.default: region {default_region!r} is not listed in regions.allow")
    cfg["regions"] = {"names": names, "wildcard": wildcard, "deny": deny_entries,
                      "default": default_region}

    n = DEFAULTS["network"]
    cfg["network"] = {
        "max_flood_hops": _num(_get(raw, "network.max_flood_hops", n["max_flood_hops"]),
                               "network.max_flood_hops", 1, 15, integer=True),
        "loop_detect": _num(_get(raw, "network.loop_detect", n["loop_detect"]),
                            "network.loop_detect", 0, 3, integer=True),
        "auto_add_max_hops": _num(_get(raw, "network.auto_add_max_hops", n["auto_add_max_hops"]),
                                  "network.auto_add_max_hops", 0, 64, integer=True),
        # 0 = 1 byte, 1 = 2 bytes, 2 = 3 bytes. MeshCore expects this in the
        # top two bits of pathLen; 1-byte hashes collide in larger meshes.
        "path_hash_mode": _num(_get(raw, "network.path_hash_mode", n["path_hash_mode"]),
                               "network.path_hash_mode", 0, 2, integer=True),
    }

    p = DEFAULTS["power"]
    cfg["power"] = {
        "power_saving": _num(_get(raw, "power.power_saving", p["power_saving"]),
                             "power.power_saving", 0, 2, integer=True),
        "deep_sleep": _bool(_get(raw, "power.deep_sleep", p["deep_sleep"]), "power.deep_sleep"),
        "rx_boost": _bool(_get(raw, "power.rx_boost", p["rx_boost"]), "power.rx_boost"),
    }

    cfg["security"] = {
        "admin_password": _string(_get(raw, "security.admin_password", ""),
                                  "security.admin_password", MAX_PASSWORD_LEN),
        "guest_password": _string(_get(raw, "security.guest_password", ""),
                                  "security.guest_password", MAX_PASSWORD_LEN),
    }
    if cfg["security"]["guest_password"] and not cfg["security"]["admin_password"]:
        raise ConfigError("security.guest_password is set but security.admin_password is empty")

    return cfg


def fingerprint(cfg):
    """FNV-1a 32 bit over the normalised configuration.

    Uses the validated values, not the raw file: editing a comment or
    reordering keys therefore does not trigger a needless EEPROM write.
    """
    canonical = json.dumps(cfg, sort_keys=True, separators=(",", ":")).encode("utf-8")
    h = 0x811C9DC5
    for byte in canonical:
        h ^= byte
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h


def c_float(value):
    """Render a float as a valid C float literal."""
    if abs(value - round(value)) < 1e-9 and abs(value) >= 1000:
        return "%.1ff" % value
    text = ("%.3f" % value).rstrip("0").rstrip(".")
    return (text or "0") + "f"


def emit_header(cfg, fp):
    lines = [
        "// AUTO-GENERATED by tools/gen_user_config.py from config/repeater.json",
        "// Do not edit - edit config/repeater.json and rebuild instead.",
        "#pragma once",
        "",
        "#define USERCFG_PRESENT 1",
        f"#define USERCFG_FINGERPRINT 0x{fp:08X}UL",
        "",
        "// Node identity",
        f'#define USERCFG_NAME "{cfg["name"]}"',
        f'#define USERCFG_HAS_LOCATION {1 if cfg["location"]["set"] else 0}',
        f'#define USERCFG_LAT_E6 {int(round(cfg["location"]["latitude"] * 1e6))}L',
        f'#define USERCFG_LON_E6 {int(round(cfg["location"]["longitude"] * 1e6))}L',
        "",
        "// Radio (used by main.h instead of the built-in region presets)",
        f'#define MC_FREQUENCY {c_float(cfg["radio"]["frequency_mhz"])}',
        f'#define MC_BANDWIDTH {c_float(cfg["radio"]["bandwidth_khz"])}',
        f'#define MC_SPREADING {cfg["radio"]["spreading_factor"]}',
        f'#define MC_CODING_RATE {cfg["radio"]["coding_rate"]}',
        f'#define MC_TX_POWER {cfg["radio"]["tx_power_dbm"]}',
        f'#define MC_PREAMBLE_LEN {cfg["radio"]["preamble_len"]}',
        "",
        "// Advertising",
        f'#define USERCFG_ADV_LOCAL_MIN {cfg["advertising"]["local_interval_minutes"]}',
        f'#define USERCFG_ADV_FLOOD_HRS {cfg["advertising"]["flood_interval_hours"]}',
        "",
        "// Regions (the wildcard entry is managed by USERCFG_WILDCARD)",
        f'#define USERCFG_WILDCARD {1 if cfg["regions"]["wildcard"] else 0}',
        f'#define USERCFG_REGION_COUNT {len(cfg["regions"]["names"])}',
        f'#define USERCFG_DENY_COUNT {len(cfg["regions"]["deny"])}',
        f'#define USERCFG_DEFAULT_REGION "{cfg["regions"]["default"]}"',
        "",
        "// Forwarding / loop detection",
        f'#define USERCFG_MAX_FLOOD_HOPS {cfg["network"]["max_flood_hops"]}',
        f'#define USERCFG_LOOP_DETECT {cfg["network"]["loop_detect"]}',
        f'#define USERCFG_AUTOADD_MAXHOPS {cfg["network"]["auto_add_max_hops"]}',
        f'#define USERCFG_PATH_HASH_MODE {cfg["network"]["path_hash_mode"]}',
        "",
        "// Power",
        f'#define USERCFG_POWER_SAVING {cfg["power"]["power_saving"]}',
        f'#define USERCFG_DEEP_SLEEP {1 if cfg["power"]["deep_sleep"] else 0}',
        f'#define USERCFG_RX_BOOST {1 if cfg["power"]["rx_boost"] else 0}',
        "",
        "// Credentials (empty = keep whatever is stored in the EEPROM)",
        f'#define USERCFG_ADMIN_PASSWORD "{cfg["security"]["admin_password"]}"',
        f'#define USERCFG_GUEST_PASSWORD "{cfg["security"]["guest_password"]}"',
        "",
    ]
    return "\n".join(lines)


def emit_source(cfg):
    names = cfg["regions"]["names"]
    deny = cfg["regions"]["deny"]
    lines = [
        "// AUTO-GENERATED by tools/gen_user_config.py - do not edit.",
        '#include "UserConfigData.h"',
        "",
        "#if USERCFG_PRESENT",
        "",
    ]
    if names:
        entries = ",\n".join(f'    "{n}"' for n in names)
        lines += [
            # "extern" is required: a const-qualified variable at namespace scope
            # would otherwise get internal linkage and the tables would not be
            # visible outside this translation unit.
            f"extern const char* const userCfgRegions[USERCFG_REGION_COUNT] = {{",
            entries,
            "};",
            "",
        ]
    if deny:
        entries = ",\n".join(f'    "{n}"' for n in deny)
        lines += [
            f"extern const char* const userCfgDenyFlood[USERCFG_DENY_COUNT] = {{",
            entries,
            "};",
            "",
        ]
    lines += ["#endif // USERCFG_PRESENT", ""]
    return "\n".join(lines)


def generate(config_path, verbose=True):
    out_dir = generated_dir()
    if not config_path.exists():
        # No user configuration: emit an empty stub so the build still works and
        # the firmware keeps its built-in defaults.
        out_dir.mkdir(parents=True, exist_ok=True)
        stub_h = ("// No config/repeater.json found - firmware uses its built-in defaults.\n"
                  "#pragma once\n#define USERCFG_PRESENT 0\n")
        stub_c = ('#include "UserConfigData.h"\n'
                  "#if USERCFG_PRESENT\n#error generated files are stale\n#endif\n")
        (out_dir / "UserConfigData.h").write_text(stub_h, encoding="utf-8")
        (out_dir / "UserConfigData.cpp").write_text(stub_c, encoding="utf-8")
        if verbose:
            print(f"[userconfig] {config_path} not found - using built-in defaults")
        return None

    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"{config_path.name} is not valid JSON: {exc}") from exc

    cfg = validate(raw)
    fp = fingerprint(cfg)

    out_dir.mkdir(parents=True, exist_ok=True)
    header = out_dir / "UserConfigData.h"
    source = out_dir / "UserConfigData.cpp"
    new_header = emit_header(cfg, fp)
    new_source = emit_source(cfg)

    # Only touch the files when something actually changed, so the build stays
    # incremental and the config is not re-applied on unchanged sources.
    if not header.exists() or header.read_text(encoding="utf-8") != new_header:
        header.write_text(new_header, encoding="utf-8")
    if not source.exists() or source.read_text(encoding="utf-8") != new_source:
        source.write_text(new_source, encoding="utf-8")

    if verbose:
        print(f"[userconfig] name={cfg['name'] or '(unchanged)'} "
              f"radio={cfg['radio']['frequency_mhz']}MHz/"
              f"BW{cfg['radio']['bandwidth_khz']}/SF{cfg['radio']['spreading_factor']}/"
              f"CR{cfg['radio']['coding_rate']}/{cfg['radio']['tx_power_dbm']}dBm "
              f"regions={cfg['regions']['names']} "
              f"deny={cfg['regions']['deny'] or '-'} fingerprint=0x{fp:08X}")
    return cfg


def _cli(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate config/repeater.json and generate the firmware constants.")
    parser.add_argument("--config", default=None,
                        help="path to the JSON configuration (default: config/repeater.json)")
    parser.add_argument("--check", action="store_true",
                        help="only validate, write nothing")
    args = parser.parse_args(argv)

    path = Path(args.config) if args.config else default_config()

    if not path.exists():
        # Matches the pre-script path: no configuration file, build with the
        # firmware's built-in defaults instead of failing.
        print(f"[userconfig] {path} not found - using built-in defaults")
        if not args.check:
            generate(path)
        return 0

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"{path.name} is not valid JSON: {exc}") from exc

    if args.check:
        cfg = validate(raw)
        print(f"OK: {path} is valid (fingerprint 0x{fingerprint(cfg):08X})")
        return 0
    generate(path)
    return 0


def _main():
    try:
        sys.exit(_cli())
    except ConfigError as exc:
        print(f"[userconfig] CHECK FAILED: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    _main()
else:
    # Loaded as a PlatformIO pre-script: generate before the build starts.
    try:
        Import("env")          # noqa: F821 - injected by SCons
        try:
            _cli([])
        except ConfigError as _exc:      # fail the build with a readable message
            print(f"[userconfig] CHECK FAILED: {_exc}", file=sys.stderr)
            raise
    except NameError:
        pass                   # imported as a module (tests) - do nothing
