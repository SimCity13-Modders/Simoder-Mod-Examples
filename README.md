# Simoder-Mod-Examples

Authored Simoder examples. The original ten Simoder-DevTools source files
remain unchanged; BaseApiExample adds the supported Base profile example. This package owns example projects; runtime
implementation belongs to Simoder, host authoring tools to DevTools, and API
declarations to Simoder-SDK. It contains no game assets or binaries.

| Project | Existing behavior |
| --- | --- |
| BaseApiExample | Read-only Base snapshots and deferred lifecycle subscription |
| LuauExample | Lifecycle callbacks, local module loading and periodic logging |
| PropApiExample | Owner-scoped scalar PROP override using verified resource aliases |
| TOMLExample | Declarative scalar PROP override with readable aliases |
| TypeScriptExample | Existing TypeScriptToLua lifecycle example and local module |

RoadBuilder and BusLine are future acceptance examples, not implemented here.
These are examples, not a template migration system. No standalone workspace
CLI is supplied or required by this extraction.

## Compatibility and ownership

The source baseline is Simoder-DevTools commit
`d4b2421da10e5d1168a37b8348664c34681869cf`, directory `examples/`.
Original DevTools history remains the historical reference; this extraction
starts a separate history. Preserve the MIT copyright notice when copying.
MIT permits reuse; cloning does not transfer original authorship or copyright.

The manifests use authoring schemaVersion 2. The current TypeScript example
targets the existing **TypeScriptToLua** authoring path, not a JavaScript VM or
the future Node.js + tsc architecture. Its `scripts/simoder.d.ts` is the preserved
SDK-derived compatibility artifact pinned by `sdk.lock.json`, not an independent
source. It remains tracked for direct clone/editor parity; edit the canonical
Simoder-SDK declaration, then refresh this exact copy and lock after compatibility
review. The provenance test rejects mismatched bytes. Optional CMake input
`-DSIMODER_SDK_SOURCE_DIR=<checkout>` also checks the exact clean canonical SDK
revision. Prepared offline operation needs no implicit fetch or source writes.
No native ABI declarations are claimed here.

The closed schema-2 lock also pins SDK package `0.2.0`, its manifest SHA-256,
and the exact `base-luau-alpha-v1` declaration/guide paths and hashes. Existing
TypeScript paths and payload hash remain unchanged. Missing, extra, duplicate
or incorrectly typed lock fields are rejected. The optional canonical check
requires exact clean Git provenance before comparing manifest/profile payloads;
dirty canonical files are errors. Base declarations remain owned by the SDK
and are not copied into example script directories.

Use a separately prepared compatible DevTools `simoder-build` authoring tool
with these source directories. Follow that tool's command-line help and pinned
toolchain instructions. Node.js and compiler dependencies are external; this
package downloads or bundles none. PROP examples require compatible runtime
hooks and the referenced game data. Offline structural tests do not prove
actual game behavior or runtime compatibility with arbitrary Simoder versions.

## Offline verification and packaging

Python 3.11+ provides the standard-library TOML parser used by the tests. CMake
3.20+ packages the content without a native compiler:

```text
cmake -S . -B build -DBUILD_TESTING=ON
ctest --test-dir build --output-on-failure
cmake --install build --prefix build/stage
```

Full SDK integrity qualification additionally supplies
`-DSIMODER_SDK_SOURCE_DIR=<explicit-prepared-clean-SDK>` and verifies that
`examples_sdk_integrity` is registered. That test uses fresh local Git fixtures
with inherited hook/filter/encoding preflight; it checks real revision, dirt,
missing/tampered payloads and profile-lock mismatches against the clean SDK.
Without the explicit input, these Git fixture cases are NOT_RUN. Its evidence
directory is exclusive per build; use a fresh build path for another run.
No implicit fetch, tool installation or canonical source mutation occurs.

Install paths remain `examples/<Project>/...`, identical to the original
DevTools example layout. Tests verify manifest entry containment, local script
imports, declarative targets, installed layout and unexpected content. No
game launch, network access or external compiler invocation is performed.

## Supported Base profile

`BaseApiExample` targets SDK 0.2.0/profile `base-luau-alpha-v1`; see its
README and the canonical SDK `Luau/BASE_API.md`. The actual Core host
conformance test executes its exact content-pinned script. The separate
`tests/fixtures/base/task-profile.luau` is a host-only fixture with a
native test descriptor and is excluded from installation. Declaration
grammar, structural/package checks and actual host execution are distinct
checks; none claims production installation or game qualification.
