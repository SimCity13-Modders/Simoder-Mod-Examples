# Host-only Base conformance fixture

`task-profile.luau` executes only in the Core isolated conformance target, with
its exact source hash pinned by `tests/base_sdk_profile.lock.toml`. The host
creates the actual reviewed `fixture.echo` descriptor, original scope and grant;
the script itself grants no authority. `fixture.echo` is not a shipped API,
production capability, installed example or SDK declaration.

The actual Base presentation exercises a copied value, queued task, deferred
success/failure callbacks, cancellation and registered coroutine await.
`BASE_TASK_PROFILE_COMPLETE` is emitted only after script assertions complete.
Native assertions must separately verify exact effects, ownership and cleanup.
This directory stays outside the CMake-installed `examples/` tree.
