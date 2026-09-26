# LoyalCrown's Ender Legacy

A Minecraft **1.20.1 / Forge 47.4.x** addon for **Ender IO 6.2.15-beta** that restores legacy Ender IO blocks removed from the modern rewrite.

This project was created from a comparison between Ender IO **1.7.10-2.2.8.381** and Ender IO **1.20.1-6.2.15-beta**. The addon avoids duplicating content that modern Ender IO already restored.

## Restored blocks

Farming Station, Reservoir, Combustion Generator, Zombie Generator, Photovoltaic Cell, Advanced Photovoltaic Cell, Hyper Cube / deprecated Dimensional Transceiver, Dimensional Transceiver, Power Monitor, The Vat, Wireless Charger, Killer Joe, Attractor Obelisk, Item Buffer, Power Buffer, Omni Buffer, Creative Buffer, Dark Steel Anvil, Painted Carpet, Ender Rail, and the legacy Ender IO remote-access block.

## Farming Station 0.1.1

The Farming Station now more closely follows the 1.7.10 machine: dedicated hoe/axe/supply/output/capacitor slots, legacy-style capacitor range upgrades, automatic tilling, vanilla crop farming, sapling planting/tree chopping, and melon/pumpkin/sugar-cane/cactus harvesting. See `patches/0.1.1/CHANGELOG.md` for details.

Still planned for closer legacy parity: a graphical Farming Station interface, supply-slot locking, fake-player enchantment behavior, and broader modded-crop farmer handlers.

## Target

Minecraft **1.20.1**, Forge **47.4.x**, Ender IO **6.2.15-beta**, Java **17**.

## Build status

GitHub Actions compiles, reobfuscates, validates resources, checks the packaged mod metadata, and uploads a testable Forge JAR. Ender IO is a mandatory runtime dependency declared in `mods.toml`; this addon intentionally uses Forge capabilities and registry IDs instead of Ender IO internal classes.

The production Ender IO release JAR cannot be used as a ForgeGradle mapped-userdev smoke test because its release mixins reference production/obfuscated names. CI therefore validates the built release JAR structurally, while final runtime testing is performed in a normal Forge 1.20.1 installation with Ender IO 6.2.15-beta.

## Testing note

This is still alpha software. Back up important worlds before testing.

## License / attribution

Apache-2.0. Some visual assets are modified from the legacy Ender IO 1.7.10 build. See `LICENSE` and `NOTICE`.
