# MeowForge 1.21.1

## Current implementation

The runtime foundation is NeoForge's Minecraft 1.21.1 branch, upstream commit
`89e887b367ab0c11cb58ce8500920efadc17b803`. The public game brand is MeowForge.
The `neoforge` mod ID, Java packages, module names, dependency coordinates and
version checks remain intact so NeoForge mods can link to their native platform.
Original copyright and license notices are retained.

The previous Forge foundation remains on branch `laprforge-1.21.1`.
Forge compatibility is not implemented by this change. Neither arbitrary
NeoForge modpacks nor mixed Forge/NeoForge modpacks have been verified yet.

## Target behavior

Unmodified NeoForge and Forge mods for Minecraft 1.21.1 share the game's `mods`
directory. NeoForge remains the single owner of game state, registries, lifecycle
and event dispatch. Forge-facing adapters delegate to that runtime.
Compatibility always respects Minecraft versions and dependency requirements.
It does not promise that otherwise conflicting mods can coexist.

## Implementation boundaries

1. Native NeoForge baseline: build the distribution and run the supplied Mouse
   Tweaks 2.26.1 JAR unchanged. Verify mouse events, configuration UI and its
   accessor mixin, not just successful mod discovery.
2. Forge discovery: introduce a loader extension for `META-INF/mods.toml`,
   dependency resolution, language providers and nested dependencies. FML is
   currently external (`net.neoforged.fancymodloader:loader`); inspect its
   extension points before deciding whether a separate loader fork is necessary.
3. Binary compatibility: map equivalent symbols and implement adapters where
   signatures or behavior differ. Keep transformed copies in a versioned cache;
   never overwrite users' original JARs. Package substitution alone is insufficient.
4. Semantics: bridge events including cancellation, priority and threading;
   registries, configuration, capabilities, networking and lifecycle. Do not
   create a second independent event/registry system.
5. Transformers: validate Mixins, access transformers, service loading and
   reflection. Unsupported integrations must produce actionable diagnostics.
6. Regression matrix: exercise client, dedicated server, world save/reload and
   mixed modpacks. Record the exact loader/mod versions and observed results.

## First native fixture

`MouseTweaks-neoforge-mc1.21-2.26.1.jar`

SHA-256: `68e6f4201c5de97b77929a7215c9552495696ca6a3bf3ae4eacc34e135f6cc8b`

The fixture is supplied locally by the repository owner and is not committed or
redistributed. Its startup and inventory behavior remain unverified.
