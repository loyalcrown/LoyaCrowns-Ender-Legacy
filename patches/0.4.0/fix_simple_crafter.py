from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: fix_simple_crafter.py <source-root>")

root = Path(sys.argv[1])
path = root / "src/main/java/com/loyacrown/enderlegacy/blockentity/SimpleCrafterBlockEntity.java"
source = path.read_text()

if "import net.minecraft.world.inventory.TransientCraftingContainer;" not in source:
    source = source.replace(
        "import net.minecraft.world.inventory.CraftingContainer;",
        "import net.minecraft.world.inventory.CraftingContainer;\nimport net.minecraft.world.inventory.TransientCraftingContainer;",
    )

source = source.replace(
    "new CraftingContainer(new DummyMenu(),3,3)",
    "new TransientCraftingContainer(new DummyMenu(),3,3)",
)

path.write_text(source)
print("Fixed Simple Crafter crafting-grid implementation for Minecraft 1.20.1.")
