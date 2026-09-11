# moldflow-mat-generator

A Claude Code plugin (and self-hosted marketplace) that generates Moldflow
`.mat` material files — Cross-WLF viscosity model + 2-domain modified Tait
PVT model, plus general material info — from screenshots of Moldflow's
material database editor.

## Install

**Claude Code CLI or an interface with a terminal/TUI layer** (the `/plugin`
slash command opens an interactive picker panel):

```
/plugin marketplace add abakharev/moldflow-mat-generator
/plugin install moldflow-mat-generator@moldflow-mat-generator
```

The second argument after `@` is the *marketplace* name (set by `name` in
`.claude-plugin/marketplace.json`), not the repo name — they happen to match
here, but the `plugin@marketplace` form is the documented, reliable install
syntax regardless, so use it as written rather than the bare plugin name.

**Claude apps without a TUI layer** (e.g. some Agent-SDK-based desktop/web
clients — `/plugin` will say "isn't available in this environment" there,
which just means that client has no panel to draw the picker into, not that
anything is wrong with this repo): use the app's own Settings/Customize →
Plugins → Add marketplace UI instead, pointing it at
`abakharev/moldflow-mat-generator`, then install `moldflow-mat-generator`
from the list. Confirmed working this way.

Either path, or the `claude plugin marketplace add` / `claude plugin
install` non-interactive CLI subcommands if your Claude Code version has
them, install to the same user-level `~/.claude/plugins/` directory. No
Anthropic-specific account beyond whatever the user already uses to run
Claude Code is required.

## Use

Share screenshots of a material's three Moldflow property screens:
- General Information
- Viscosity: Cross-WLF
- PVT: 2-Domain Modified Tait

and ask Claude to generate a `.mat` file. The skill extracts, validates
(deterministic range/unit checks — see
`skills/moldflow-mat-generator/scripts/validate_mat.py`), shows you the
extracted values to confirm, then writes the file. Full procedure and field
reference: `skills/moldflow-mat-generator/SKILL.md`.

## Status

Licensed MIT. Published at github.com/abakharev/moldflow-mat-generator.
