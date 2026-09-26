# LoyaCrown's Ender Legacy

A Minecraft **1.20.1 / Forge 47.4.x** addon for **Ender IO 6.2.15-beta** that restores legacy Ender IO blocks removed from the modern rewrite.

This project was created from a comparison between:

- Ender IO **1.7.10-2.2.8.381** (legacy reference)
- Ender IO **1.20.1-6.2.15-beta** (target installation)

The addon deliberately does **not** duplicate legacy blocks that already have a modern Ender IO equivalent.

## Restored blocks

- Farming Station
- Reservoir
- Combustion Generator
- Zombie Generator
- Photovoltaic Cell
- Advanced Photovoltaic Cell
- Dimensional Transceiver (Deprecated / Hyper Cube)
- Dimensional Transceiver
- Power Monitor
- The Vat
- Wireless Charger
- Killer Joe
- Attractor Obelisk
- Item Buffer
- Power Buffer
- Omni Buffer
- Creative Buffer
- Dark Steel Anvil
- Painted Carpet
- Ender Rail
- Ender IO remote-access block

## Farming Station 0.1.1

The Farming Station now more closely follows the 1.7.10 machine: dedicated hoe/axe/supply/output/capacitor slots, legacy-style capacitor range upgrades, automatic tilling, vanilla crop farming, sapling planting/tree chopping, and melon/pumpkin/sugar-cane/cactus harvesting. See `patches/0.1.1/CHANGELOG.md` for details.

Still planned for closer legacy parity: a graphical Farming Station interface, supply-slot locking, fake-player enchantment behavior, and broader modded-crop farmer handlers.

## Target

- Minecraft: **1.20.1**
- Forge: **47.4.x**
- Ender IO: **6.2.15-beta**
- Java: **17**

## Build status

GitHub Actions compiles, reobfuscates, validates resources, checks the packaged mod metadata, and uploads a testable Forge JAR. Ender IO is a mandatory runtime dependency declared in `mods.toml`; this addon intentionally uses Forge capabilities and registry IDs instead of Ender IO internal classes.

The previous attempt to launch the production Ender IO JAR inside ForgeGradle's mapped `runServer` environment was removed because Ender IO's release mixins reference production/obfuscated names and therefore fail in that userdev environment. That failure was from the development test environment, not from LoyaCrown's Ender Legacy compilation.

## Testing note

This is still alpha software. Back up any important world before testing. The next validation step is a normal Minecraft Forge 1.20.1 client using Ender IO 6.2.15-beta and the generated LoyaCrown's Ender Legacy JAR.

## License / attribution

Apache-2.0. Some visual assets are modified from the legacy Ender IO 1.7.10 build. See `LICENSE` and `NOTICE`.
