# MeowForge 1.21.1

## Current implementation

The runtime foundation is NeoForge's Minecraft 1.21.1 branch, upstream commit
`89e887b367ab0c11cb58ce8500920efadc17b803`. The public game brand is MeowForge.
The `neoforge` mod ID, Java packages, module names, dependency coordinates and
version checks remain intact so NeoForge mods can link to their native platform.
Original copyright and license notices are retained.

The previous Forge foundation remains on branch `laprforge-1.21.1`.
Forge runtime compatibility is not implemented yet. The first implemented stage
is a read-only preflight and an API inventory, described below. Neither arbitrary
NeoForge modpacks nor mixed Forge/NeoForge modpacks have been verified yet.

## Forge bridge: implemented preflight

`scripts/forge_compat.py` reads Forge/NeoForge TOML metadata, declared Minecraft
version ranges and Forge class references without executing or modifying mods.
Native NeoForge metadata takes precedence for dual-platform JARs. Unknown version
syntax is recorded as unverified, never interpreted as proof of compatibility.
The launcher runs this check before startup. Forge JARs currently stop with
`bridge_required`; wrong Minecraft versions stop with `minecraft_mismatch`.
This prevents the NeoForge loader silently skipping an unsupported Forge mod.

Run the unit tests with `python -m unittest discover -s scripts -p test_forge_compat.py -v`.
Run `python scripts/forge_compat.py MODS_DIRECTORY --strict --report .local/compatibility-report.json`
to inspect a pack. A native candidate still requires actual startup and gameplay tests.

`scripts/forge_api_catalog.py MOD.jar --report .local/api-plan.json` inventories
candidate class mappings against local NeoForge build outputs and cached modules.
Class existence does not establish method, field, inheritance or behavioral compatibility.

The supplied Forge Xaero Minimap 26.6.0 targets Minecraft 1.21.1 and references
54 Forge API classes. Initial inventory finds 14 without a direct candidate:
configuration screen factories, texture stitching events, legacy tick events,
display-test extensions, loading stages/context and Forge registry interfaces.
The remaining candidate classes also need signature and behavior validation.
Xaero has not been transformed or successfully loaded; no third-party JAR is
committed or redistributed. The next runtime milestone is an FML discovery
extension and tested adapters for those API families.

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

## Native smoke test

The client with the supplied cat window icon and Mouse Tweaks 2.26.1 was launched.
A separate creative test world was created, the inventory opened, an item moved
to the hotbar, and the world saved back to the title screen without a crash.
This is a native NeoForge smoke test, not proof that Forge Xaero works or that
all Mouse Tweaks-specific gestures are correct. The original user modpack was untouched.
