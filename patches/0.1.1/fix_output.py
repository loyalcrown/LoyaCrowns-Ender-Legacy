from pathlib import Path

path = Path("LoyaCrowns-Ender-Legacy/src/main/java/com/loyacrown/enderlegacy/blockentity/FarmingStationBlockEntity.java")
source = path.read_text()
old = '''    private void storeDrops(ServerLevel serverLevel, BlockPos pos, List<ItemStack> drops) {
        for (ItemStack drop : drops) {
            ItemStack remainder = drop.copy();
            for (int slot = FIRST_OUTPUT_SLOT; slot <= LAST_OUTPUT_SLOT && !remainder.isEmpty(); slot++) {
                remainder = inventory.insertItem(slot, remainder, false);
            }
            if (!remainder.isEmpty()) {
                Block.popResource(serverLevel, pos, remainder);
            }
        }
    }
'''
new = '''    private void storeDrops(ServerLevel serverLevel, BlockPos pos, List<ItemStack> drops) {
        for (ItemStack drop : drops) {
            ItemStack remainder = insertIntoOutput(drop);
            if (!remainder.isEmpty()) {
                Block.popResource(serverLevel, pos, remainder);
            }
        }
    }

    /**
     * Output slots reject external insertion, so harvested items are merged internally
     * with setStackInSlot instead of ItemStackHandler.insertItem().
     */
    private ItemStack insertIntoOutput(ItemStack stack) {
        ItemStack remainder = stack.copy();
        for (int slot = FIRST_OUTPUT_SLOT; slot <= LAST_OUTPUT_SLOT && !remainder.isEmpty(); slot++) {
            ItemStack existing = inventory.getStackInSlot(slot);
            if (existing.isEmpty()) {
                int move = Math.min(remainder.getCount(), Math.min(remainder.getMaxStackSize(), inventory.getSlotLimit(slot)));
                ItemStack placed = remainder.copy();
                placed.setCount(move);
                inventory.setStackInSlot(slot, placed);
                remainder.shrink(move);
                continue;
            }
            if (!ItemStack.isSameItemSameTags(existing, remainder)) {
                continue;
            }
            int limit = Math.min(existing.getMaxStackSize(), inventory.getSlotLimit(slot));
            int space = limit - existing.getCount();
            if (space <= 0) {
                continue;
            }
            int move = Math.min(space, remainder.getCount());
            ItemStack merged = existing.copy();
            merged.grow(move);
            inventory.setStackInSlot(slot, merged);
            remainder.shrink(move);
        }
        return remainder;
    }
'''
if old not in source:
    raise SystemExit("Expected storeDrops block was not found; refusing to patch an unknown source revision.")
path.write_text(source.replace(old, new))
print("Patched Farming Station internal output routing.")
