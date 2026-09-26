package com.loyacrown.enderlegacy.blockentity;

import com.loyacrown.enderlegacy.registry.LegacyBlockEntities;
import com.loyacrown.enderlegacy.util.MachineInteractionUtil;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.AxeItem;
import net.minecraft.world.item.HoeItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.CocoaBlock;
import net.minecraft.world.level.block.CropBlock;
import net.minecraft.world.level.block.NetherWartBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.capabilities.ForgeCapabilities;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.items.ItemStackHandler;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

import java.util.ArrayDeque;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * A practical 1.20.1 recreation of the legacy Ender IO Farming Station.
 *
 * Slot layout intentionally mirrors the old machine's concepts:
 * 0 hoe, 1 axe, 2-5 planting supplies, 6-10 harvest output, 11 capacitor.
 * The original 1.7.10 machine used tool/supply/output/upgrade slot groups and
 * increased its working radius with stronger capacitors.
 */
public class FarmingStationBlockEntity extends LegacyPoweredBlockEntity implements LegacyTickingBlockEntity,
        LegacyInteractableBlockEntity, LegacyInventoryHolder {
    private static final int CROP_ACTION_ENERGY = 500;
    private static final int AXE_ACTION_ENERGY = 1_000;
    private static final int BASE_RANGE = 3;

    private static final int HOE_SLOT = 0;
    private static final int AXE_SLOT = 1;
    private static final int FIRST_SUPPLY_SLOT = 2;
    private static final int LAST_SUPPLY_SLOT = 5;
    private static final int FIRST_OUTPUT_SLOT = 6;
    private static final int LAST_OUTPUT_SLOT = 10;
    private static final int CAPACITOR_SLOT = 11;

    private final ItemStackHandler inventory = new ItemStackHandler(12) {
        @Override
        public boolean isItemValid(int slot, @NotNull ItemStack stack) {
            if (slot == HOE_SLOT) {
                return stack.getItem() instanceof HoeItem;
            }
            if (slot == AXE_SLOT) {
                return stack.getItem() instanceof AxeItem;
            }
            if (slot >= FIRST_SUPPLY_SLOT && slot <= LAST_SUPPLY_SLOT) {
                return isPlantingSupply(stack);
            }
            if (slot >= FIRST_OUTPUT_SLOT && slot <= LAST_OUTPUT_SLOT) {
                return false;
            }
            if (slot == CAPACITOR_SLOT) {
                return capacitorTier(stack) > 0;
            }
            return false;
        }

        @Override
        protected void onContentsChanged(int slot) {
            setChanged();
        }
    };
    private LazyOptional<ItemStackHandler> itemCapability = LazyOptional.empty();
    private int tickCounter;
    private int scanIndex;
    private String notification = "";

    public FarmingStationBlockEntity(BlockPos pos, BlockState state) {
        super(LegacyBlockEntities.FARMING_STATION.get(), pos, state, 1_000_000, 4_000, 0);
    }

    @Override
    public void onLoad() {
        super.onLoad();
        itemCapability = LazyOptional.of(() -> inventory);
    }

    @Override
    public void invalidateCaps() {
        super.invalidateCaps();
        itemCapability.invalidate();
    }

    @Override
    public <T> @NotNull LazyOptional<T> getCapability(@NotNull Capability<T> cap, @Nullable Direction side) {
        if (cap == ForgeCapabilities.ITEM_HANDLER) {
            return itemCapability.cast();
        }
        return super.getCapability(cap, side);
    }

    @Override
    public void serverTick() {
        if (!(level instanceof ServerLevel serverLevel)) {
            return;
        }
        if (++tickCounter < 10) {
            return;
        }
        tickCounter = 0;

        int range = getFarmRange();
        int diameter = range * 2 + 1;
        int total = diameter * diameter;
        for (int attempt = 0; attempt < 12; attempt++) {
            int idx = Math.floorMod(scanIndex++, total);
            int dx = (idx % diameter) - range;
            int dz = (idx / diameter) - range;
            BlockPos target = worldPosition.offset(dx, 0, dz);

            if (tryHarvest(serverLevel, target)
                    || tryPrepareSoil(serverLevel, target)
                    || tryPlant(serverLevel, target)) {
                setChanged();
                break;
            }
        }
    }

    private boolean tryHarvest(ServerLevel serverLevel, BlockPos pos) {
        BlockState state = serverLevel.getBlockState(pos);

        if (state.getBlock() instanceof CropBlock crop && crop.isMaxAge(state)) {
            if (!consumeEnergy(CROP_ACTION_ENERGY)) return false;
            List<ItemStack> drops = Block.getDrops(state, serverLevel, pos, serverLevel.getBlockEntity(pos));
            serverLevel.setBlock(pos, crop.getStateForAge(0), Block.UPDATE_ALL);
            storeDrops(serverLevel, pos, drops);
            clearNotification();
            return true;
        }
        if (state.is(Blocks.NETHER_WART) && state.getValue(NetherWartBlock.AGE) >= NetherWartBlock.MAX_AGE) {
            if (!consumeEnergy(CROP_ACTION_ENERGY)) return false;
            List<ItemStack> drops = Block.getDrops(state, serverLevel, pos, serverLevel.getBlockEntity(pos));
            serverLevel.setBlock(pos, state.setValue(NetherWartBlock.AGE, 0), Block.UPDATE_ALL);
            storeDrops(serverLevel, pos, drops);
            clearNotification();
            return true;
        }
        if (state.getBlock() instanceof CocoaBlock && state.getValue(CocoaBlock.AGE) >= CocoaBlock.MAX_AGE) {
            if (!consumeEnergy(CROP_ACTION_ENERGY)) return false;
            List<ItemStack> drops = Block.getDrops(state, serverLevel, pos, serverLevel.getBlockEntity(pos));
            serverLevel.setBlock(pos, state.setValue(CocoaBlock.AGE, 0), Block.UPDATE_ALL);
            storeDrops(serverLevel, pos, drops);
            clearNotification();
            return true;
        }
        if (state.is(Blocks.MELON) || state.is(Blocks.PUMPKIN)) {
            if (!consumeEnergy(CROP_ACTION_ENERGY)) return false;
            List<ItemStack> drops = Block.getDrops(state, serverLevel, pos, serverLevel.getBlockEntity(pos));
            serverLevel.removeBlock(pos, false);
            storeDrops(serverLevel, pos, drops);
            clearNotification();
            return true;
        }
        if (state.is(Blocks.SUGAR_CANE) || state.is(Blocks.CACTUS)) {
            return harvestColumn(serverLevel, pos, state.getBlock());
        }
        if (state.is(BlockTags.LOGS) && looksLikeTree(serverLevel, pos)) {
            return harvestTree(serverLevel, pos);
        }
        return false;
    }

    private boolean harvestColumn(ServerLevel level, BlockPos base, Block block) {
        // Leave the bottom block planted and harvest up to the next three growth blocks.
        if (!level.getBlockState(base.below()).is(block)) {
            for (int dy = 1; dy <= 3; dy++) {
                BlockPos target = base.above(dy);
                BlockState state = level.getBlockState(target);
                if (!state.is(block)) break;
                if (!consumeEnergy(CROP_ACTION_ENERGY)) return false;
                List<ItemStack> drops = Block.getDrops(state, level, target, level.getBlockEntity(target));
                level.removeBlock(target, false);
                storeDrops(level, target, drops);
                clearNotification();
                return true;
            }
        }
        return false;
    }

    private boolean looksLikeTree(ServerLevel level, BlockPos base) {
        for (int y = 1; y <= 10; y++) {
            BlockPos center = base.above(y);
            for (int x = -2; x <= 2; x++) {
                for (int z = -2; z <= 2; z++) {
                    if (level.getBlockState(center.offset(x, 0, z)).is(BlockTags.LEAVES)) {
                        return true;
                    }
                }
            }
        }
        return false;
    }

    private boolean harvestTree(ServerLevel level, BlockPos base) {
        if (!hasAxe()) {
            setNotification("Needs an axe");
            return false;
        }
        if (energy.getEnergyStored() < AXE_ACTION_ENERGY) {
            return false;
        }

        ArrayDeque<BlockPos> open = new ArrayDeque<>();
        Set<BlockPos> visited = new HashSet<>();
        open.add(base);
        int chopped = 0;

        while (!open.isEmpty() && chopped < 128 && hasAxe()) {
            BlockPos pos = open.removeFirst();
            if (!visited.add(pos)) continue;
            if (pos.getY() < base.getY() || pos.getY() > base.getY() + 24) continue;
            if (Math.abs(pos.getX() - base.getX()) > 6 || Math.abs(pos.getZ() - base.getZ()) > 6) continue;

            BlockState state = level.getBlockState(pos);
            if (!state.is(BlockTags.LOGS)) continue;
            if (!consumeEnergy(AXE_ACTION_ENERGY)) break;

            List<ItemStack> drops = Block.getDrops(state, level, pos, level.getBlockEntity(pos));
            level.removeBlock(pos, false);
            storeDrops(level, pos, drops);
            damageTool(AXE_SLOT);
            chopped++;

            for (Direction direction : Direction.values()) {
                open.addLast(pos.relative(direction));
            }
        }

        if (chopped > 0) {
            clearNotification();
            return true;
        }
        return false;
    }

    private boolean tryPrepareSoil(ServerLevel serverLevel, BlockPos plantPos) {
        if (!serverLevel.getBlockState(plantPos).isAir()) {
            return false;
        }
        BlockPos soilPos = plantPos.below();
        BlockState soil = serverLevel.getBlockState(soilPos);
        if (!(soil.is(Blocks.DIRT) || soil.is(Blocks.GRASS_BLOCK) || soil.is(Blocks.COARSE_DIRT) || soil.is(Blocks.DIRT_PATH))) {
            return false;
        }
        if (!hasCropSeed()) {
            return false;
        }
        if (!hasHoe()) {
            setNotification("Needs a hoe");
            return false;
        }
        if (!consumeEnergy(CROP_ACTION_ENERGY)) {
            return false;
        }

        serverLevel.setBlock(soilPos, Blocks.FARMLAND.defaultBlockState(), Block.UPDATE_ALL);
        damageTool(HOE_SLOT);
        clearNotification();
        return true;
    }

    private boolean tryPlant(ServerLevel serverLevel, BlockPos plantPos) {
        if (!serverLevel.getBlockState(plantPos).isAir()) {
            return false;
        }
        BlockState soil = serverLevel.getBlockState(plantPos.below());

        if (soil.is(Blocks.FARMLAND)) {
            return tryPlant(serverLevel, plantPos, Items.WHEAT_SEEDS, Blocks.WHEAT.defaultBlockState())
                    || tryPlant(serverLevel, plantPos, Items.CARROT, Blocks.CARROTS.defaultBlockState())
                    || tryPlant(serverLevel, plantPos, Items.POTATO, Blocks.POTATOES.defaultBlockState())
                    || tryPlant(serverLevel, plantPos, Items.BEETROOT_SEEDS, Blocks.BEETROOTS.defaultBlockState());
        }
        if (soil.is(Blocks.SOUL_SAND)) {
            return tryPlant(serverLevel, plantPos, Items.NETHER_WART, Blocks.NETHER_WART.defaultBlockState());
        }

        // Legacy Farming Station also supported trees. These cover all vanilla 1.20.1 saplings.
        if (soil.is(BlockTags.DIRT)) {
            return tryPlant(serverLevel, plantPos, Items.OAK_SAPLING, Blocks.OAK_SAPLING.defaultBlockState())
                    || tryPlant(serverLevel, plantPos, Items.SPRUCE_SAPLING, Blocks.SPRUCE_SAPLING.defaultBlockState())
                    || tryPlant(serverLevel, plantPos, Items.BIRCH_SAPLING, Blocks.BIRCH_SAPLING.defaultBlockState())
                    || tryPlant(serverLevel, plantPos, Items.JUNGLE_SAPLING, Blocks.JUNGLE_SAPLING.defaultBlockState())
                    || tryPlant(serverLevel, plantPos, Items.ACACIA_SAPLING, Blocks.ACACIA_SAPLING.defaultBlockState())
                    || tryPlant(serverLevel, plantPos, Items.DARK_OAK_SAPLING, Blocks.DARK_OAK_SAPLING.defaultBlockState())
                    || tryPlant(serverLevel, plantPos, Items.CHERRY_SAPLING, Blocks.CHERRY_SAPLING.defaultBlockState());
        }

        // Vertical vanilla plants that the old farmer family also handled.
        if (tryPlantIfSurvives(serverLevel, plantPos, Items.SUGAR_CANE, Blocks.SUGAR_CANE.defaultBlockState())) return true;
        return tryPlantIfSurvives(serverLevel, plantPos, Items.CACTUS, Blocks.CACTUS.defaultBlockState());
    }

    private boolean tryPlant(ServerLevel level, BlockPos pos, Item seed, BlockState plantedState) {
        int slot = findSupply(seed);
        if (slot < 0) return false;
        if (!plantedState.canSurvive(level, pos)) return false;
        if (!consumeEnergy(CROP_ACTION_ENERGY)) return false;

        inventory.extractItem(slot, 1, false);
        level.setBlock(pos, plantedState, Block.UPDATE_ALL);
        clearNotification();
        return true;
    }

    private boolean tryPlantIfSurvives(ServerLevel level, BlockPos pos, Item item, BlockState plantedState) {
        return tryPlant(level, pos, item, plantedState);
    }

    private int findSupply(Item item) {
        for (int slot = FIRST_SUPPLY_SLOT; slot <= LAST_SUPPLY_SLOT; slot++) {
            if (inventory.getStackInSlot(slot).is(item)) {
                return slot;
            }
        }
        return -1;
    }

    private boolean hasCropSeed() {
        return findSupply(Items.WHEAT_SEEDS) >= 0
                || findSupply(Items.CARROT) >= 0
                || findSupply(Items.POTATO) >= 0
                || findSupply(Items.BEETROOT_SEEDS) >= 0;
    }

    private void storeDrops(ServerLevel serverLevel, BlockPos pos, List<ItemStack> drops) {
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

    private boolean hasHoe() {
        return inventory.getStackInSlot(HOE_SLOT).getItem() instanceof HoeItem;
    }

    private boolean hasAxe() {
        return inventory.getStackInSlot(AXE_SLOT).getItem() instanceof AxeItem;
    }

    private void damageTool(int slot) {
        ItemStack tool = inventory.getStackInSlot(slot);
        if (tool.isEmpty() || !tool.isDamageableItem()) return;
        int nextDamage = tool.getDamageValue() + 1;
        if (nextDamage >= tool.getMaxDamage()) {
            inventory.setStackInSlot(slot, ItemStack.EMPTY);
        } else {
            tool.setDamageValue(nextDamage);
            inventory.setStackInSlot(slot, tool);
        }
    }

    private boolean consumeEnergy(int amount) {
        if (energy.getEnergyStored() < amount) return false;
        energy.removeEnergyInternal(amount, false);
        return true;
    }

    private int getFarmRange() {
        int tier = capacitorTier(inventory.getStackInSlot(CAPACITOR_SLOT));
        return BASE_RANGE + Math.max(0, tier - 1) * 2;
    }

    private static int capacitorTier(ItemStack stack) {
        if (stack.isEmpty()) return 1; // old machine behaved as a basic tier by default
        ResourceLocation id = BuiltInRegistries.ITEM.getKey(stack.getItem());
        if (!"enderio".equals(id.getNamespace())) return 0;
        return switch (id.getPath()) {
            case "basic_capacitor" -> 1;
            case "double_layer_capacitor" -> 2;
            case "octadic_capacitor" -> 3;
            default -> 0;
        };
    }

    private static boolean isPlantingSupply(ItemStack stack) {
        Item item = stack.getItem();
        return item == Items.WHEAT_SEEDS || item == Items.CARROT || item == Items.POTATO
                || item == Items.BEETROOT_SEEDS || item == Items.NETHER_WART
                || item == Items.OAK_SAPLING || item == Items.SPRUCE_SAPLING || item == Items.BIRCH_SAPLING
                || item == Items.JUNGLE_SAPLING || item == Items.ACACIA_SAPLING || item == Items.DARK_OAK_SAPLING
                || item == Items.CHERRY_SAPLING || item == Items.SUGAR_CANE || item == Items.CACTUS;
    }

    private void setNotification(String message) {
        notification = message;
    }

    private void clearNotification() {
        notification = "";
    }

    @Override
    public InteractionResult onUse(Player player, InteractionHand hand) {
        String status = "Farming Station — " + energy.getEnergyStored() + "/" + energy.getMaxEnergyStored()
                + " FE, range " + getFarmRange()
                + ", supplies " + countFilledSlots(FIRST_SUPPLY_SLOT, LAST_SUPPLY_SLOT) + "/4"
                + ", output " + countFilledSlots(FIRST_OUTPUT_SLOT, LAST_OUTPUT_SLOT) + "/5"
                + (notification.isEmpty() ? "" : ", " + notification);
        if (player.getItemInHand(hand).isEmpty() && !player.isShiftKeyDown()) {
            player.displayClientMessage(Component.literal(status), true);
            return InteractionResult.sidedSuccess(player.level().isClientSide);
        }
        return MachineInteractionUtil.insertOrExtract(player, hand, inventory, status);
    }

    private int countFilledSlots(int first, int last) {
        int count = 0;
        for (int i = first; i <= last; i++) {
            if (!inventory.getStackInSlot(i).isEmpty()) count++;
        }
        return count;
    }

    @Override
    public ItemStackHandler getInventory() {
        return inventory;
    }

    @Override
    protected void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);
        tag.put("Inventory", inventory.serializeNBT());
        tag.putInt("ScanIndex", scanIndex);
        tag.putString("Notification", notification);
    }

    @Override
    public void load(CompoundTag tag) {
        super.load(tag);
        inventory.deserializeNBT(tag.getCompound("Inventory"));
        scanIndex = tag.getInt("ScanIndex");
        notification = tag.getString("Notification");
    }
}
