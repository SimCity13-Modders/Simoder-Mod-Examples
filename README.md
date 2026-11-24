# Simoder-Mod-Examples

[![Download Latest (Nightly)](https://img.shields.io/github/last-commit/SimCity13-Modders/Simoder-Mod-Examples/main?label=Download%20latest%20(nightly)&logo=github)](https://github.com/SimCity13-Modders/Simoder-Mod-Examples/archive/refs/heads/main.zip)
[![Download Latest Release](https://img.shields.io/github/v/release/SimCity13-Modders/Simoder-Mod-Examples?label=Download%20latest%20release&logo=github)](https://github.com/SimCity13-Modders/Simoder-Mod-Examples/releases/latest)
[![Star](https://img.shields.io/github/stars/SimCity13-Modders/Simoder-Mod-Examples?style=social)](https://github.com/SimCity13-Modders/Simoder-Mod-Examples/stargazers)

**Simoder-Mod-Examples** is a curated collection of self-contained example mods for **Simoder**, demonstrating `simoder.authoring` (Schema 2) manifests across Luau scripts, `Simoder-Base` APIs, `PROP` overrides, TOML declarations, and TypeScript authoring. No game assets or runtime binaries are included.

## Dependencies & Requirements

- **Runtime**: [Simoder](https://github.com/SimCity13-Modders/Simoder) (`d3d9.dll`) + [Simoder-Base](https://github.com/SimCity13-Modders/Simoder-Base) (`mods/simoder.base`)
- **Offline verification (optional)**: Python 3.11+ and CMake 3.20+

## Installation

1. Install [Simoder](https://github.com/SimCity13-Modders/Simoder) and [Simoder-Base](https://github.com/SimCity13-Modders/Simoder-Base).
2. Download the examples from the **Release** or **Nightly** badge above (or clone this repository).
3. Copy any example folder from `examples/<Project>/` into `<SimCity Install>\mods\<Project>\`:

```text
<SimCity Install>/
  mods/
    BaseApiExample/
      mod.toml
      scripts/...
```

4. Launch SimCity and enable the example mod from the in-game **Mods** menu.

---

## Included Examples

| Example | Demonstrated Features |
| --- | --- |
| `BaseApiExample` | `Simoder-Base` (`base-luau-alpha-v1`) read-only snapshots and lifecycle subscription |
| `LuauExample` | Luau lifecycle callbacks, local `require` module loading, and periodic logging |
| `PropApiExample` | Owner-scoped scalar `PROP` overrides using verified resource aliases |
| `TOMLExample` | Declarative `[[patches]]` scalar `PROP` overrides in `mod.toml` |
| `TypeScriptExample` | TypeScript-authored lifecycle example with pinned SDK declarations |

## Offline Verification & Packaging

```powershell
cmake -S . -B build -DBUILD_TESTING=ON
ctest --test-dir build --output-on-failure
cmake --install build --prefix build/stage
```

To additionally run SDK provenance checks against a local [Simoder-SDK](https://github.com/SimCity13-Modders/Simoder-SDK) checkout, pass `-DSIMODER_SDK_SOURCE_DIR=<path-to-Simoder-SDK>`.
