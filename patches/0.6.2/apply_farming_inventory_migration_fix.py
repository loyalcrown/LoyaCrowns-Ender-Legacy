from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
path = root / "src/main/java/com/loyacrown/enderlegacy/blockentity/FarmingStationBlockEntity.java"
text = path.read_text()

load_anchor = '''    @Override
    public void load(CompoundTag tag) {
        super.load(tag);
        inventory.deserializeNBT(tag.getCompound("Inventory"));
'''

replacement = '''    /**
     * Migrates the pre-0.6.1 12-slot Farming Station inventory into the restored
     * 16-slot SkyFactory 3 layout without allowing ItemStackHandler.deserializeNBT()
     * to resize the live handler back to 12 slots.
     *
     * Old 0.6.0 layout:
     *   0 hoe, 1 axe, 2-5 supplies, 6-10 output, 11 capacitor
     * New 0.6.1+ layout:
     *   0-2 tools, 3-4 fertilizer, 5-8 supplies, 9-14 output, 15 capacitor
     */
    private void loadInventoryWithMigration(CompoundTag inventoryTag) {
        int savedSize = inventoryTag.getInt("Size");
        if (savedSize == 16) {
            inventory.deserializeNBT(inventoryTag);
            return;
        }

        // Never deserialize a legacy-sized tag directly into the live handler:
        // Forge resizes ItemStackHandler to the serialized Size value.
        for (int slot = 0; slot < inventory.getSlots(); slot++) {
            inventory.setStackInSlot(slot, ItemStack.EMPTY);
        }
        if (savedSize <= 0) return;

        ItemStackHandler legacy = new ItemStackHandler(savedSize);
        legacy.deserializeNBT(inventoryTag);

        if (savedSize == 12) {
            inventory.setStackInSlot(0, legacy.getStackInSlot(0).copy());
            inventory.setStackInSlot(1, legacy.getStackInSlot(1).copy());
            for (int oldSlot = 2; oldSlot <= 5; oldSlot++) {
                inventory.setStackInSlot(5 + (oldSlot - 2), legacy.getStackInSlot(oldSlot).copy());
            }
            for (int oldSlot = 6; oldSlot <= 10; oldSlot++) {
                inventory.setStackInSlot(9 + (oldSlot - 6), legacy.getStackInSlot(oldSlot).copy());
            }
            inventory.setStackInSlot(15, legacy.getStackInSlot(11).copy());
            return;
        }

        // Defensive fallback for any development-era save with another size.
        // Preserve as many same-index stacks as possible rather than crashing.
        int copyCount = Math.min(savedSize, inventory.getSlots());
        for (int slot = 0; slot < copyCount; slot++) {
            inventory.setStackInSlot(slot, legacy.getStackInSlot(slot).copy());
        }
    }

    @Override
    public void load(CompoundTag tag) {
        super.load(tag);
        loadInventoryWithMigration(tag.getCompound("Inventory"));
'''

if load_anchor not in text:
    raise RuntimeError("Farming Station migration anchor not found")
text = text.replace(load_anchor, replacement, 1)

checks = [
    "loadInventoryWithMigration",
    "savedSize == 12",
    "inventory.setStackInSlot(15, legacy.getStackInSlot(11).copy())",
    "loadInventoryWithMigration(tag.getCompound(\"Inventory\"))",
]
for token in checks:
    if token not in text:
        raise RuntimeError(f"Farming Station migration invariant missing: {token}")

path.write_text(text)
print("Applied Farming Station 12-slot -> 16-slot world migration fix")
