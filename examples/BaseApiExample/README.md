# Base API example

Targets the supported `base-luau-alpha-v1` profile in Simoder-SDK 0.2.0.
The actual Base-bound mod VM supplies the immutable `base` global. Calls use
dot syntax: `base.snapshot()`, `base.subscribe(callback)`, `base.descriptors()`.
See the canonical SDK `Luau/BASE_API.md` and `Luau/base.d.luau` for declarations.

This read-only example subscribes after activation, verifies copied immutable
snapshots and reaches `BASE_API_EXAMPLE_COMPLETE` after deferred delivery.
It accepts an empty native descriptor catalog and requests no task or grant.
An ordinary unbound runtime prints `BASE_API_EXAMPLE_UNAVAILABLE` instead.
Denied/unavailable operations are reported without inventing permissions.
Native generation cleanup retires the subscription when the mod is stopped;
this example introduces no manual unsubscribe API.

This source is not proof that production installation/cutover is enabled.
The Core conformance target executes the exact content-pinned script in actual
isolated hosts. No compiler, SDK checkout or test harness is an end-user
dependency. Legacy examples remain unchanged. Preserve the repository's MIT
notice when reusing this authored source.
