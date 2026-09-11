#!/usr/bin/env python3
"""
Deterministic sanity-checker for a generated .mat file, run BEFORE showing
the final file to the user. Catches the two most likely failure modes of
vision-extracting engineering coefficients from a screenshot: wrong field
count (mis-read/merged a value) and wrong order of magnitude (missed a unit
conversion or misread an exponent).

This does not validate correctness of the extraction (it can't know the
"right" answer) - it only flags values that are outside the range seen in
real Moldflow materials, so an outlier gets a second look before being
trusted.

Usage:
    python validate_mat.py path/to/material.mat
Exit code 0 = no warnings, 1 = warnings printed (not necessarily wrong,
but worth the user double-checking against the screenshot), 2 = malformed
file (missing required keys / wrong value count).
"""

import re
import sys

REQUIRED_KEYS = ["Manufacturer", "Trade_Name", "Family", "Viscosity_Model", "PVT_Model"]

# (label, low, high) - generous bounds spanning real Moldflow thermoplastics,
# not tight engineering tolerances. A miss here means "double-check the
# screenshot", not "this is definitely wrong".
VISCOSITY_RANGES = [
    ("n", 0.05, 1.0),
    ("Tau*", 1e2, 1e7),
    ("D1", 1e6, 1e20),
    ("D2", 150, 470),
    ("D3", -1e-3, 1e-3),
    ("A1", 5, 80),
    ("A2~", 20, 80),
]

PVT_RANGES = [
    ("b5", 300, 550),
    ("b6", 1e-9, 1e-5),
    ("b1m", 3e-4, 3e-3),
    ("b2m", 1e-8, 5e-6),
    ("b3m", 1e6, 5e8),
    ("b4m", 1e-4, 2e-2),
    ("b1s", 3e-4, 3e-3),
    ("b2s", 1e-8, 5e-6),
    ("b3s", 1e6, 5e8),
    ("b4s", 1e-4, 2e-2),
    ("b7", 1e-6, 1e-3),
    ("b8", 1e-3, 1.0),
    ("b9", 1e-11, 1e-6),
]


def parse_mat(path):
    fields = {}
    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.split("#", 1)[0].strip()
            if not line or "=" not in line:
                continue
            key, value = line.split("=", 1)
            fields[key.strip()] = value.strip()
    return fields


def parse_numbers(value_str):
    return [float(tok) for tok in re.split(r"[\s,]+", value_str.strip()) if tok]


def check_ranges(label, values, ranges):
    warnings = []
    if len(values) != len(ranges) and not (label == "PVT_Model" and len(values) == 10):
        warnings.append(
            f"{label}: expected {len(ranges)} values (or 10 for PVT with no "
            f"transition-region terms), got {len(values)} - likely a misread "
            f"or merged field."
        )
        return warnings
    for (name, lo, hi), v in zip(ranges, values):
        if not (lo <= v <= hi):
            warnings.append(
                f"{label}.{name} = {v:g} is outside the typical range "
                f"[{lo:g}, {hi:g}] - check units and exponent against the "
                f"screenshot."
            )
    return warnings


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    path = sys.argv[1]
    fields = parse_mat(path)

    missing = [k for k in REQUIRED_KEYS if k not in fields]
    if missing:
        print(f"MALFORMED: missing required key(s): {', '.join(missing)}")
        return 2

    warnings = []
    try:
        visc = parse_numbers(fields["Viscosity_Model"])
        warnings += check_ranges("Viscosity_Model", visc, VISCOSITY_RANGES)
    except ValueError as e:
        print(f"MALFORMED: Viscosity_Model not all numeric ({e})")
        return 2

    try:
        pvt = parse_numbers(fields["PVT_Model"])
        pvt_ranges = PVT_RANGES if len(pvt) > 10 else PVT_RANGES[:10]
        warnings += check_ranges("PVT_Model", pvt, pvt_ranges)
    except ValueError as e:
        print(f"MALFORMED: PVT_Model not all numeric ({e})")
        return 2

    if warnings:
        print(f"{len(warnings)} warning(s) for {path}:")
        for w in warnings:
            print(f"  - {w}")
        return 1

    print(f"OK: {path} - {len(visc)} viscosity values, {len(pvt)} PVT values, all within typical ranges.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
