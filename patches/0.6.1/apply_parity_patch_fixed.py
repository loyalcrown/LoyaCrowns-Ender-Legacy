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

# These two GUI payloads were truncated when the original large patch file was
# written through the GitHub API. Keep clean, validated copies here so CI can
# reconstruct the exact intended 0.6.1 sources without depending on those
# damaged strings.
payloads["src/main/java/com/loyacrown/enderlegacy/client/DimensionalTransceiverScreen.java"] = "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"
payloads["src/main/java/com/loyacrown/enderlegacy/client/InventoryPanelScreen.java"] = "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"

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
