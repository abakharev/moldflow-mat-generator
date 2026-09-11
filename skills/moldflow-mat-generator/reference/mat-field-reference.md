# .mat field reference

This is the ground truth for the file format. It's a plain-text keyword/value
format (not Moldflow's proprietary binary `.udb`), confirmed against real,
working material files (see `examples/*.mat` - numeric coefficients are
real, verified data; manufacturer/trade names are anonymized placeholders)
and against Moldflow's Synergy API field layout for the "Thermoplastics
material" property (T-code 21000): field 1313 for the Cross-WLF composite
value, field 1310 for the viscosity model selector.

## File skeleton

```
# Moldflow material data file
# Format: Keyword = value(s)  (spaces or commas as separators, # for comments)

Manufacturer    = <string>
Trade_Name      = <string>
Family          = <string>
Grade_Code      = <string>
Filler          = <string, omit line if unfilled>

# Cross-WLF viscosity model coefficients
# Order: n  Tau*(Pa)  D1(Pa.s)  D2(K)  D3(K/Pa)  A1  A2~(K)
Viscosity_Model = <n> <Tau*> <D1> <D2> <D3> <A1> <A2~>

# 2-domain modified Tait PVT model coefficients
# Order: b5(K)  b6(K/Pa)  b1m(m3/kg)  b2m(m3/kg.K)  b3m(Pa)  b4m(1/K)
#        b1s(m3/kg)  b2s(m3/kg.K)  b3s(Pa)  b4s(1/K)  [b7(m3/kg)  b8(1/K)  b9(1/Pa)]
PVT_Model = <b5> <b6> <b1m> <b2m> <b3m> <b4m> <b1s> <b2s> <b3s> <b4s> [<b7> <b8> <b9>]
```

Keep the comment lines — they document the field order in the file itself,
matching all three example files. Values are space-separated (commas also
accepted per the header comment, but space-separated matches every real
example and is preferred).

## General info fields (from the material's "General Information" screen)

| Keyword | Meaning | Notes |
|---|---|---|
| `Manufacturer` | Material supplier name | copy verbatim from the "Manufacturer" field |
| `Trade_Name` | Commercial grade name | copy verbatim from the "Trade name" field |
| `Family` | Material family | e.g. "POLYPROPYLENES (PP)" — copy Moldflow's own family label verbatim, including the abbreviation in parens. If the family field shows a generic multi-example category (e.g. "BLENDS (PC+PBT, PC+ABS, ...)") rather than one specific to this material, substitute this material's actual composition from a "Family abbreviation" field if present (e.g. "BLENDS (PC+ABS)") instead of copying the generic list |
| `Grade_Code` | Manufacturer's own short/supplier code, if shown separately from Trade_Name | Prefer a field labeled "Supplier code" over Moldflow's internal "Material ID"/"Grade code" database identifiers - see `examples/*.mat` |
| `Filler` | Filler/reinforcement description | Omit the whole line if the material is unfilled (don't write `Filler = None`) |

## Cross-WLF viscosity model — 7 values, in this exact order

Moldflow's "Viscosity: Cross-WLF" property screen shows these as separate
labeled fields; some screens use "~" (tilde) for A2, some spell it "A2*" —
always output the key as `A2~` in the comment/order regardless of the
screenshot's exact glyph.

| # | Symbol | Unit | Typical range | What it controls |
|---|---|---|---|---|
| 1 | `n` | dimensionless | 0.1 – 0.5 | power-law index |
| 2 | `Tau*` (tau-star) | Pa | 1e3 – 1e6 | shear stress transition |
| 3 | `D1` | Pa·s | 1e10 – 1e18 | zero-shear viscosity scale |
| 4 | `D2` | K | 200 – 470 | glass-transition reference temp — ≈263.15 K for many semi-crystalline materials (e.g. PP), but 380–420 K is normal for high-Tg amorphous materials/blends (PC, ABS, PC+ABS) — don't assume ~263 K is universal |
| 5 | `D3` | K/Pa | usually `0` | pressure dependence of D2 (most thermoplastics leave this 0) |
| 6 | `A1` | dimensionless | 20 – 50 | WLF constant |
| 7 | `A2~` | K | almost always `51.6` | WLF constant (universal default Moldflow uses unless overridden) |

If a screenshot's D1 is scientific notation like `4.822e+12`, keep it in that
notation (matches the examples) rather than expanding it.

## 2-domain modified Tait PVT model — 10 required + 3 optional values, in this exact order

Moldflow's "PVT: 2-Domain Modified Tait" screen splits these into a "melt"
(m-suffix) group and "solid" (s-suffix) group, plus the two Tait constants
`b5`/`b6`, plus an optional transition-region group (`b7`/`b8`/`b9`) that
only appears for materials Moldflow models with a smoothed melt/solid
transition — omit the trailing three values entirely if the screenshot
doesn't show them (don't pad with zeros).

| # | Symbol | Unit | Typical range | Group |
|---|---|---|---|---|
| 1 | `b5` | K | 350 – 500 | Tait transition temperature |
| 2 | `b6` | K/Pa | ~1e-8 – 1e-6 | Tait transition temp pressure-dependence |
| 3 | `b1m` | m³/kg | 0.0008 – 0.0015 | melt specific volume |
| 4 | `b2m` | m³/(kg·K) | ~5e-7 – 1e-6 | melt thermal expansion |
| 5 | `b3m` | Pa | 5e7 – 2e8 | melt Tait pressure constant |
| 6 | `b4m` | 1/K | ~0.003 – 0.006 | melt Tait pressure temp-dependence |
| 7 | `b1s` | m³/kg | 0.0008 – 0.0015 | solid specific volume |
| 8 | `b2s` | m³/(kg·K) | ~4e-7 – 8e-7 | solid thermal expansion |
| 9 | `b3s` | Pa | 5e7 – 2e8 | solid Tait pressure constant |
| 10 | `b4s` | 1/K | ~0.003 – 0.007 | solid Tait pressure temp-dependence |
| 11 (opt) | `b7` | m³/kg | ~5e-5 – 1e-4 | transition-region specific volume jump |
| 12 (opt) | `b8` | 1/K | ~0.05 – 0.2 | transition-region temp sensitivity |
| 13 (opt) | `b9` | 1/Pa | ~1e-9 – 5e-8 | transition-region pressure sensitivity |

## Units gotcha

Moldflow's UI sometimes lets a user toggle displayed units (e.g. specific
volume in cm³/g vs m³/kg, pressure in MPa vs Pa). The `.mat` format here
always uses **base SI** (Pa, K, m³/kg, 1/K, 1/Pa) — check the unit labels
printed next to each field in the screenshot and convert if they're not
already SI:
- cm³/g → m³/kg: multiply by 0.001
- MPa → Pa: multiply by 1e6
- °C → K: add 273.15 (rare for these fields, but check D2/b5 if a screenshot
  shows Celsius)

Silently trusting the screenshot's raw numbers without checking the unit
label is the single most likely source of an order-of-magnitude error.
