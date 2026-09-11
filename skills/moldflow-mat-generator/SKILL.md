---
name: moldflow-mat-generator
description: Generate a Moldflow .mat material file (Cross-WLF viscosity model + 2-domain modified Tait PVT model, plus general material info) from screenshots of Moldflow's material database editor. Use whenever the user shares screenshots of a material's General Information, Viscosity (Cross-WLF), and/or PVT (2-Domain Modified Tait) property screens and wants a .mat file for the multiple-injectors-multiple-materials Moldflow solver plugin, or asks to "make a mat file", "digitize this material", "add this grade to Moldflow", etc.
---

# Moldflow .mat file generator

Turns screenshots of Moldflow's material database editor into a `.mat` text
file in the exact format this project's solver plugin reads. Read
`reference/mat-field-reference.md` first — it has the full field order,
units, and per-field typical ranges. `examples/*.mat` are three real,
verified material files to pattern-match against.

## Why this needs care

These are engineering coefficients that feed a physics solver — a
misread digit or missed unit conversion produces a `.mat` file that loads
fine and fails silently (wrong viscosity/PVT behavior in the simulation,
no error message). Treat vision extraction from a screenshot as a first
draft, not ground truth: always run the validator and always show the
extracted numbers back to the user before writing the final file.

## Procedure

1. **Ask for what's missing.** You need three groups of information,
   normally three separate screenshots from Moldflow's material database
   editor (Synergy or the standalone Material database app):
   - **General Information** tab: Manufacturer, Trade Name, Family, Grade
     Code, Filler description.
   - **Viscosity: Cross-WLF** tab: the 7 coefficients (n, Tau*, D1, D2, D3,
     A1, A2~).
   - **PVT: 2-Domain Modified Tait** tab: the 10 (or 13, if the material has
     a transition-region correction) coefficients.
   If the user only provides one or two screenshots, generate what you can
   and clearly say what's still missing rather than inventing values.

2. **Extract.** Read each screenshot carefully. For every numeric field,
   note the exact digits, the exponent, and the unit label printed next to
   it. Cross-check unit labels against `reference/mat-field-reference.md`'s
   "Units gotcha" section — convert to SI (Pa, K, m³/kg, 1/K, 1/Pa) if the
   screenshot shows something else (e.g. MPa, cm³/g).

3. **Assemble** the `.mat` text using the exact skeleton and field order in
   `reference/mat-field-reference.md` (keep the header comment lines - they
   document field order in the file itself, matching every example).

4. **Validate.** Write the draft to a temp file and run:
   ```
   python scripts/validate_mat.py <path>
   ```
   This is a deterministic range/format check, not a correctness check - it
   catches misreads (wrong value count) and order-of-magnitude errors
   (missed unit conversion, misread exponent). Fix anything it flags by
   re-checking the relevant screenshot region before proceeding; a value
   can legitimately be outside the typical range for an unusual material,
   but re-verify against the screenshot rather than assuming the tool is
   wrong.

5. **Show your work before finalizing.** Present the extracted values in a
   compact table (field → value → source screenshot) and ask the user to
   confirm, especially for any value the validator flagged. This is the
   main defense against a silent misread - the user can look at their own
   screenshot and catch it faster than re-OCRing.

6. **Write the file.** Once confirmed, save as `<Trade_Name>.mat` (or
   wherever the user wants it - per the format's convention, shown in
   `examples/*.mat`, one file per material, referenced from Moldflow's
   Solver API "Parameter text" field).

## Edge cases

- **Unfilled material**: omit the `Filler` line entirely rather than
  writing `Filler = None` or `Filler = Unfilled`.
- **No transition-region PVT terms**: omit `b7 b8 b9` entirely (10 values,
  not 13 padded with zeros) - Moldflow only shows these for materials it
  models with a smoothed transition. This applies whether the fields are
  absent from the screenshot *or* present but explicitly valued at `0` -
  a zeroed transition term has no effect on the model, so it's written the
  same way as an absent one: omitted, not included as literal zeros.
- **Family name is a generic category, not material-specific**: some
  material families (e.g. "BLENDS") show a generic multi-example label like
  `BLENDS (PC+PBT, PC+ABS, ...)` in the General Information screen instead
  of a label specific to this material. If a separate "Family abbreviation"
  field gives this material's actual composition (e.g. `PC+ABS`), use that
  in place of the generic parenthetical (e.g. `Family = BLENDS (PC+ABS)`)
  rather than copying the generic example list verbatim.
- **Grade_Code vs. other codes**: Moldflow's General Information screen can
  show multiple codes (a Moldflow-internal "Material ID"/"Grade code" and a
  manufacturer-facing "Supplier code"). Prefer the manufacturer's own short
  code (labeled "Supplier code" or similar) for `Grade_Code`, matching the
  pattern in the example files - not Moldflow's internal database ID.
- **D3 shown as blank/dash in the screenshot**: this almost always means
  `0`, not a missing value - confirm with the user if genuinely ambiguous.
- **Multiple grades/fill levels in one screenshot set**: generate one
  `.mat` file per distinct grade; don't merge them.
- **Low-confidence read** (blurry screenshot, cut-off digits, ambiguous
  exponent): say so explicitly and ask the user to re-crop/re-screenshot
  that field rather than guessing.
