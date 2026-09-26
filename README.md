# LoyalCrown's Ender Legacy

A Minecraft **1.20.1 / Forge 47.4.x** addon for **Ender IO 6.2.15-beta** that restores legacy Ender IO content removed from the modern rewrite.

The project now uses **Ender IO 1.12.2-5.3.72** as the preferred legacy reference whenever a block still existed in that release, while using older 1.7.10 assets only for content that had already disappeared by 1.12.2. The addon still runs on Minecraft 1.20.1; no legacy bytecode is loaded at runtime.

## Restored blocks

Farming Station, Reservoir, Combustion Generator, Zombie Generator, Photovoltaic Cell, Advanced Photovoltaic Cell, Hyper Cube / deprecated Dimensional Transceiver, Dimensional Transceiver, Power Monitor, Graphical Power Monitor, The Vat, Wireless Charger, Killer Joe, Attractor Obelisk, Item Buffer, Power Buffer, Omni Buffer, Creative Buffer, Dark Steel Anvil, Painted Carpet, Ender Rail, Exit Rail, and the legacy Ender IO remote-access block.

## 0.2.0-alpha — 1.12.2 reference pass

- Dark Steel Anvil uses proper anvil geometry and the exact Ender IO 5.3.72 anvil body/top artwork.
- Ender Rail now has complete powered-rail state coverage so curves/slopes/orientations do not fall back to missing models. Because Ender Rail was gone by 1.12.2, its exact surviving 1.7.10 rail textures are used.
- Added **Exit Rail** from Ender IO 5.3.72 with the original texture and recreated eject/destroy minecart behavior.
- Added **Graphical Power Monitor** using the 5.3.72 animated frame/screen artwork and the existing 1.20.1-compatible Power Monitor logic.
- Farming Station, Reservoir, Combustion Generator, Power Monitor, Dimensional Transceiver, and Photovoltaic Cells now use 5.3.72 textures where practical.
- CI now validates JSON plus every LoyalCrown-owned model and texture reference before publishing a JAR, specifically to catch missing-texture/model problems.

## Farming Station

The Farming Station has dedicated hoe/axe/supply/output/capacitor slots, capacitor-based range upgrades, automatic tilling, vanilla crop farming, sapling planting/tree chopping, and melon/pumpkin/sugar-cane/cactus handling.

Still planned for closer legacy parity: a graphical Farming Station interface, supply-slot locking, fake-player enchantment behavior, broader modded-crop farmer handlers, and additional machines/systems found in Ender IO 5.3.72.

## Compatibility target

- Minecraft **1.20.1**
- Forge **47.4.x** (CI currently compiles against **47.4.0**)
- Ender IO **6.2.15-beta**
- Java **17**

`mods.toml` requires Ender IO in the range **[6.2.15-beta, 6.3)**. The addon avoids duplicating content already present in modern Ender IO and uses Forge APIs/registry IDs rather than loading 1.12.2 classes.

## Build validation

GitHub Actions compiles and reobfuscates the mod, validates resource JSON, checks model/texture references, checks the packaged metadata and required restored block models, and uploads a testable Forge JAR.

The production Ender IO 6.2.15-beta release JAR cannot be used as a ForgeGradle mapped-userdev smoke-test dependency because its release mixins reference production/obfuscated names. Final runtime testing should therefore be done in a normal Forge 1.20.1 installation with Ender IO 6.2.15-beta.

## Testing note

This is still alpha software. Back up important worlds before testing.

## License / attribution

Apache-2.0 for this addon. Legacy reference material comes from Ender IO's public-domain releases; see `LICENSE`, `NOTICE`, and `REFERENCE_1_12_2.md` in the generated source tree.
