from pathlib import Path
import ast
import base64
import binascii
import sys
import zlib

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
source_script = Path(__file__).with_name("apply_parity_patch.py")

module = ast.parse(source_script.read_text())
payloads = None
for node in module.body:
    if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "payloads" for target in node.targets):
        payloads = ast.literal_eval(node.value)
        break
if not isinstance(payloads, dict):
    raise RuntimeError("Could not locate the 0.6.1 payload dictionary")

parity_rules = """# LoyaCrown's Ender Legacy parity rules

## Functional source of truth

1. If a block/item/machine existed in the SkyFactory 3-era Ender IO build, reproduce that behavior first: inventory groups, recipes, energy use, capacitor/upgrades, redstone modes, side I/O, tanks, filters, automation behavior, range, drops and machine-specific mechanics.
2. If that old implementation is incomplete, broken on modern Minecraft, or a newer Ender IO implementation is demonstrably more complete, use the newest working implementation of the same feature while preserving the legacy gameplay intent.
3. Do not replace machine interactions with chat-only placeholders when the historical/newer implementation had a real GUI or configurable behavior.

## Visual source of truth

1. Block/item skins should match the legacy Ender IO appearance where the content is a restoration.
2. GUI composition should follow the newest working Ender IO Farming Station style: compact dark machine panel, left energy/status area, small right-side controls, overlays for configuration instead of permanently expanding the screen.
3. Functional controls from the legacy machine must remain available even when the screen is modernized.

## Compatibility target

Minecraft 1.20.1 / Forge 47.x / Java 17. The behavior and look are backported; the game version is not changed.
"""

props = root / "gradle.properties"
text = props.read_text()
if "mod_version=0.6.0-alpha" not in text:
    raise RuntimeError("Expected validated 0.6.0-alpha source as the patch base")
props.write_text(text.replace("mod_version=0.6.0-alpha", "mod_version=0.6.1-alpha", 1))

for relative, encoded in payloads.items():
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if relative == "PARITY_RULES.md":
        target.write_text(parity_rules)
        continue
    try:
        decoded = base64.b64decode(encoded, validate=True)
        target.write_bytes(zlib.decompress(decoded))
    except (binascii.Error, zlib.error) as exc:
        raise RuntimeError(f"Corrupt 0.6.1 payload for {relative}: {exc}") from exc

changelog = root / "CHANGELOG.md"
if changelog.exists():
    old = changelog.read_text()
    heading = """## 0.6.1-alpha - SkyFactory 3 behavior / modern Ender IO UI pass

- Replaced the Farming Station's permanent gray side panel with a compact current-Ender-IO-style control stack and I/O overlay.
- Restored four independent Farming Station supply-slot locks from the legacy machine behavior.
- Added a working Farming Station range visibility toggle with a world range preview.
- Kept per-side item I/O and redstone modes while presenting them through the compact machine UI.
- Restyled the Dimensional Transceiver and Inventory Panel screens into the same dark machine family without changing their legacy textures.
- Added explicit parity rules: SkyFactory 3-era behavior first; newest working Ender IO implementation when legacy behavior is incomplete; Forge 1.20.1 remains the target.

"""
    if "## 0.6.1-alpha" not in old:
        changelog.write_text(heading + old)

print(f"Applied repaired 0.6.1 parity/UI patch to {root}")
