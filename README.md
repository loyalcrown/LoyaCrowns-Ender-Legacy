# LoyaCrown's Ender Legacy

A Minecraft **1.20.1 / Forge 47.4.x** addon for **Ender IO 6.2.15-beta** that restores legacy Ender IO blocks removed from the modern rewrite.

This project was created from a comparison between:

- Ender IO **1.7.10-2.2.8.381** (legacy reference)
- Ender IO **1.20.1-6.2.15-beta** (target installation)

The addon deliberately does **not** duplicate legacy blocks that already have a modern Ender IO equivalent.

## Restored blocks in the first alpha

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

See `PORT_STATUS.md` for the feature-by-feature status and the legacy blocks intentionally omitted because Ender IO 6.2.15 already contains their modern equivalents.

## Target

- Minecraft: **1.20.1**
- Forge: **47.4.0+** (source target is 47.4.0)
- Ender IO: **6.2.15-beta**
- Java: **17**

## Important alpha note

This is an early functional port. The source/resources have been statically checked, but this snapshot has **not yet been compiled or launched inside a Forge runtime in this workspace** because the Forge development dependencies are not available offline here. Use the included GitHub Actions workflow or a Forge development environment to produce and test the JAR. Do not treat the alpha as world-safe until it has passed a test-world cycle.

## Building

With Java 17 and Gradle 8.8 installed:

```text
gradle clean build
```

The output JAR will be in `build/libs/`.

If using GitHub, the included `.github/workflows/build.yml` builds the JAR automatically and uploads it as an Actions artifact.

## License / attribution

Apache-2.0. Some visual assets are modified from the legacy Ender IO 1.7.10 build. See `LICENSE` and `NOTICE`.
