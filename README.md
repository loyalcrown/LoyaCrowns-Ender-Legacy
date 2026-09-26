# LoyalCrown's Ender Legacy

A Minecraft **1.20.1 / Forge 47.4.x** addon for **Ender IO 6.2.15-beta** that restores legacy Ender IO content removed from the modern rewrite.

The project now uses **Ender IO 1.12.2-5.3.72** as the preferred legacy reference whenever a block still existed in that release, while using older 1.7.10 assets only for content that had already disappeared by 1.12.2. The addon still runs on Minecraft 1.20.1; no legacy bytecode is loaded at runtime.

## Restored blocks

Farming Station, Reservoir, Combustion Generator, Zombie Generator, **Frank'n'Zombie Generator**, **Ender Generator**, Photovoltaic Cell, Advanced Photovoltaic Cell, Hyper Cube / deprecated Dimensional Transceiver, Dimensional Transceiver, Power Monitor, **Graphical Power Monitor**, The Vat, Wireless Charger, Killer Joe, Attractor Obelisk, Item Buffer, Power Buffer, Omni Buffer, Creative Buffer, Dark Steel Anvil, **Dark Paper Anvil**, Painted Carpet, Ender Rail, **Exit Rail**, and the legacy Ender IO remote-access block.

## 0.2.0-alpha — 1.12.2 reference pass

- Dark Steel Anvil now uses proper anvil geometry plus the exact Ender IO 5.3.72 body/top artwork.
- Ender Rail now has complete powered-rail state coverage so slopes/orientations do not fall back to missing models. Because Ender Rail was gone by 1.12.2, its surviving 1.7.10 rail artwork is used.
- Added **Exit Rail** from Ender IO 5.3.72 with its exact texture and recreated eject/destroy minecart behavior.
- Added **Graphical Power Monitor** with the 5.3.72 animated frame/screen artwork and the existing 1.20.1-compatible Power Monitor logic.
- Added **Dark Paper Anvil** with the legacy anvil model/artwork and fragile block properties.
- Added **Frank'n'Zombie Generator** and **Ender Generator** with 5.3.72 generator artwork and legacy default generation/buffer/fuel-duration values.
- Farming Station now uses the exact 5.3.72 block geometry and textures rather than a cube approximation.
- Reservoir, Combustion Generator, Power Monitor, Dimensional Transceiver, and Photovoltaic Cells now use 5.3.72 textures/models where practical.
- CI validates JSON plus every registered LoyalCrown block's blockstate, item model, loot table, and owned model/texture references before publishing a JAR. This is specifically intended to catch missing-texture/model problems like the early anvil and rail issues.

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

GitHub Actions compiles and reobfuscates the mod, validates resource JSON, audits registered-block resources, checks model/texture references, verifies packaged metadata and key restored classes/models, and uploads a testable Forge JAR.

The production Ender IO 6.2.15-beta release JAR cannot be used as a ForgeGradle mapped-userdev smoke-test dependency because its release mixins reference production/obfuscated names. Final runtime testing should therefore be done in a normal Forge 1.20.1 installation with Ender IO 6.2.15-beta.

## Testing note

This is still alpha software. Back up important worlds before testing.

## License / attribution

Apache-2.0 for this addon. Legacy reference material comes from Ender IO's public-domain releases; see `LICENSE`, `NOTICE`, and `REFERENCE_1_12_2.md` in the generated source tree.
