#!/usr/bin/env python3
"""
test_user_config.py - checks the config/repeater.json validation.

Runs the generator in --check mode against temporary configuration files, so it
needs neither a board nor PlatformIO:

    python3 tools/test_user_config.py
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "gen_user_config.py"
BASE = json.loads((ROOT / "config" / "repeater.json").read_text(encoding="utf-8"))


def radio(**kw):
    return {"radio": {**BASE["radio"], **kw}}


def adv(**kw):
    return {"advertising": {**BASE["advertising"], **kw}}


def regions(allow, deny=()):
    return {"regions": {"allow": allow, "deny_flood": list(deny)}}


def security(admin="", guest=""):
    return {"security": {"admin_password": admin, "guest_password": guest}}


# label, patch (None = shipped configuration), expected exit code, expected message part
CASES = [
    ("shipped configuration",      None,                                   0, None),
    ("bandwidth not supported",    radio(bandwidth_khz=100.0),             1, "not a supported SX1262 bandwidth"),
    ("SF out of range",            radio(spreading_factor=13),             1, "must be between 5 and 12"),
    ("tx power too high",          radio(tx_power_dbm=30),                 1, "must be between -9 and 22"),
    ("latitude out of range",      {"location": {"latitude": 91.0, "longitude": 0.0}},
                                                                           1, "must be between -90.0 and 90.0"),
    ("six named regions",          regions(["*", "a", "b", "c", "d", "e", "f"]), 1, "at most 5 are supported"),
    ("five named regions is fine", regions(["*", "a", "b", "c", "d"]),      0, None),
    ("region name too long",       regions(["*", "de-nord-ostsee"]),        1, "max 11 characters"),
    ("deny without allow",         regions(["*", "de"], ["de-west"]),       1, "is not in regions.allow"),
    ("wildcard in allow and deny", regions(["*", "de"], ["*"]),             1, "both 'allow' and 'deny_flood'"),
    ("wildcard only in deny",      regions(["de"], ["*"]),                  0, None),
    ("flood interval 2 h",         adv(flood_interval_hours=2),             1, "3-48 is required"),
    ("flood interval 0 h (off)",   adv(flood_interval_hours=0),             0, None),
    ("name too long",              {"name": "DE-NI-HARSUM01-LANG"},         1, "max 15 characters"),
    ("password too long",          security("x" * 16),                      1, "max 15 characters"),
    ("guest password w/o admin",   security("", "g"),                       1, "admin_password is empty"),
    ("non-ASCII name",             {"name": "HÖRSELBERG"},                  1, "printable ASCII"),
]


def run_generator(config_path=None):
    cmd = [sys.executable, str(SCRIPT), "--check"]
    if config_path:
        cmd += ["--config", str(config_path)]
    return subprocess.run(cmd, capture_output=True, text=True)


def check(label, patch, expected_rc, needle, failures):
    if patch is None:
        proc = run_generator()
    else:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump({**BASE, **patch}, tmp)
        tmp.close()
        try:
            proc = run_generator(tmp.name)
        finally:
            Path(tmp.name).unlink()

    output = proc.stdout + proc.stderr
    problem = None
    if proc.returncode != expected_rc:
        problem = f"exit code {proc.returncode}, expected {expected_rc}"
    elif needle and needle not in output:
        problem = f"message does not contain {needle!r}: {output.strip()}"

    if problem:
        print(f"FAIL  {label}: {problem}")
        return failures + 1
    print(f"ok    {label}")
    return failures


def main():
    failures = 0
    for label, patch, expected_rc, needle in CASES:
        failures = check(label, patch, expected_rc, needle, failures)

    # A missing configuration file must not break the build path.
    proc = run_generator("/nonexistent/repeater.json")
    if proc.returncode == 0 and "built-in defaults" in proc.stdout + proc.stderr:
        print("ok    missing file falls back to built-in defaults")
    else:
        failures += 1
        print(f"FAIL  missing file fallback: rc={proc.returncode} {proc.stdout}{proc.stderr}")

    total = len(CASES) + 1
    print(f"\n{total - failures}/{total} checks passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
