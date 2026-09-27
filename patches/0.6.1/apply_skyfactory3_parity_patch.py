from pathlib import Path
import shutil
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
patch_root = Path(__file__).resolve().parent

props = root / "gradle.properties"
text = props.read_text()
if "mod_version=0.6.0-alpha" not in text:
    raise RuntimeError("Expected validated 0.6.0-alpha source base")
props.write_text(text.replace("mod_version=0.6.0-alpha", "mod_version=0.6.1-alpha", 1))

# Keep the large block-entity source in small plain-text chunks so GitHub and CI
# can reproduce the source exactly without fragile embedded binary/base64 payloads.
block_entity = "".join(
    (patch_root / f"FarmingStationBlockEntity.part{i:02d}").read_text()
    for i in range(4)
)

# 0.6.1 parity hardening: the modernized/SkyFactory-style station requires an
# actual Ender IO capacitor before it can operate. Earlier draft chunks still
# treated an empty capacitor slot as basic tier, which made the dedicated
# capacitor slot cosmetic. Keep the chunks readable and enforce the final
# behavior here when reconstructing the validated source.
old_empty_capacitor = "if (stack.isEmpty()) return 1; // old machine behaved as a basic tier by default"
new_empty_capacitor = "if (stack.isEmpty()) return 0; // 0.6.1 requires a real Ender IO capacitor"
if old_empty_capacitor not in block_entity:
    raise RuntimeError("Expected pre-0.6.1 empty-capacitor behavior was not found")
block_entity = block_entity.replace(old_empty_capacitor, new_empty_capacitor, 1)

redstone_gate = "        if (!isMachineEnabledByRedstone()) return;\n"
capacitor_gate = (
    redstone_gate
    + "        if (capacitorTier(inventory.getStackInSlot(CAPACITOR_SLOT)) <= 0) {\n"
    + "            setNotification(\"A capacitor is required\");\n"
    + "            return;\n"
    + "        }\n"
)
if redstone_gate not in block_entity:
    raise RuntimeError("Expected Farming Station redstone gate was not found")
block_entity = block_entity.replace(redstone_gate, capacitor_gate, 1)

be_target = root / "src/main/java/com/loyacrown/enderlegacy/blockentity/FarmingStationBlockEntity.java"
be_target.write_text(block_entity)

for name, target in {
    "FarmingStationMenu.java": "src/main/java/com/loyacrown/enderlegacy/menu/FarmingStationMenu.java",
    "FarmingStationScreen.java": "src/main/java/com/loyacrown/enderlegacy/client/FarmingStationScreen.java",
}.items():
    destination = root / target
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(patch_root / name, destination)

be = be_target.read_text()
menu = (root / "src/main/java/com/loyacrown/enderlegacy/menu/FarmingStationMenu.java").read_text()
screen = (root / "src/main/java/com/loyacrown/enderlegacy/client/FarmingStationScreen.java").read_text()
checks = [
    ("ItemStackHandler(16)", be),
    ("FIRST_TOOL_SLOT = 0", be),
    ("FIRST_FERTILIZER_SLOT = 3", be),
    ("FIRST_SUPPLY_SLOT = 5", be),
    ("FIRST_OUTPUT_SLOT = 9", be),
    ("CAPACITOR_SLOT = 15", be),
    ("FERTILIZER_ACTION_ENERGY = 160", be),
    ("supplySlotFor", be),
    ("toggleSupplySlotLocked", be),
    ("SupplySlotLocks", be),
    ("A capacitor is required", be),
    ("if (stack.isEmpty()) return 0; // 0.6.1 requires a real Ender IO capacitor", be),
    ("MACHINE_SLOT_COUNT = 16", menu),
    ("FIRST_SUPPLY_LOCK_BUTTON_ID", menu),
    ("data.get(11 + supplyIndex)", menu),
    ("imageWidth = 184", screen),
    ("I/O Configuration", screen),
    ("drawSupplyLock(graphics, 0", screen),
    ("drawSupplyLock(graphics, 3", screen),
]
for token, content in checks:
    if token not in content:
        raise RuntimeError(f"0.6.1 parity invariant missing: {token}")

print("Applied 0.6.1 SkyFactory 3 Farming Station parity patch")
