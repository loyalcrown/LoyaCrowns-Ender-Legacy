package com.loyacrown.enderlegacy.menu;

import com.loyacrown.enderlegacy.blockentity.FarmingStationBlockEntity;
import com.loyacrown.enderlegacy.registry.LegacyMenus;
import com.loyacrown.enderlegacy.util.MachineIOMode;
import com.loyacrown.enderlegacy.util.MachineRedstoneMode;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ContainerData;
import net.minecraft.world.inventory.SimpleContainerData;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraftforge.items.SlotItemHandler;

/**
 * Farming Station menu using the 16-slot layout from Ender IO 3.1.193 / SkyFactory 3,
 * arranged with the compact coordinates used by the current Ender IO Farming Station.
 */
public class FarmingStationMenu extends AbstractContainerMenu {
    public static final int FIRST_SUPPLY_LOCK_BUTTON_ID = 0;
    public static final int FIRST_SIDE_BUTTON_ID = 10;
    public static final int REDSTONE_BUTTON_ID = 20;
    public static final int RANGE_BUTTON_ID = 21;
    public static final int MACHINE_SLOT_COUNT = 16;

    private final FarmingStationBlockEntity station;
    private final ContainerData data;

    public FarmingStationMenu(int containerId, Inventory playerInventory, FriendlyByteBuf buffer) {
        this(containerId, playerInventory, findStation(playerInventory, buffer.readBlockPos()), new SimpleContainerData(15));
    }

    public FarmingStationMenu(int containerId, Inventory playerInventory, FarmingStationBlockEntity station) {
        this(containerId, playerInventory, station, station.createMenuData());
    }

    private FarmingStationMenu(int containerId, Inventory playerInventory, FarmingStationBlockEntity station, ContainerData data) {
        super(LegacyMenus.FARMING_STATION.get(), containerId);
        this.station = station;
        this.data = data;

        // 0-2: tool inputs, same coordinates as the modern Ender IO Farming Station.
        addSlot(new SlotItemHandler(station.getInventory(), 0, 44, 19));
        addSlot(new SlotItemHandler(station.getInventory(), 1, 62, 19));
        addSlot(new SlotItemHandler(station.getInventory(), 2, 80, 19));

        // 3-4: fertilizer / bonemeal.
        addSlot(new SlotItemHandler(station.getInventory(), 3, 116, 19));
        addSlot(new SlotItemHandler(station.getInventory(), 4, 134, 19));

        // 5-8: four planting/supply quadrants.
        addSlot(new SlotItemHandler(station.getInventory(), 5, 53, 44));
        addSlot(new SlotItemHandler(station.getInventory(), 6, 71, 44));
        addSlot(new SlotItemHandler(station.getInventory(), 7, 53, 62));
        addSlot(new SlotItemHandler(station.getInventory(), 8, 71, 62));

        // 9-14: six output slots.
        for (int i = 0; i < 6; i++) {
            addSlot(new SlotItemHandler(station.getInventory(), 9 + i,
                    107 + 18 * (i % 3), i < 3 ? 44 : 62));
        }

        // 15: capacitor.
        addSlot(new SlotItemHandler(station.getInventory(), 15, 12, 63));

        for (int row = 0; row < 3; row++) {
            for (int column = 0; column < 9; column++) {
                addSlot(new net.minecraft.world.inventory.Slot(
                        playerInventory, column + row * 9 + 9, 8 + column * 18, 87 + row * 18));
            }
        }
        for (int column = 0; column < 9; column++) {
            addSlot(new net.minecraft.world.inventory.Slot(playerInventory, column, 8 + column * 18, 145));
        }

        addDataSlots(data);
    }

    private static FarmingStationBlockEntity findStation(Inventory inventory, BlockPos pos) {
        BlockEntity blockEntity = inventory.player.level().getBlockEntity(pos);
        if (blockEntity instanceof FarmingStationBlockEntity station) return station;
        throw new IllegalStateException("Farming Station menu opened without a Farming Station at " + pos);
    }

    public int getEnergyStored() { return data.get(0); }
    public int getMaxEnergyStored() { return data.get(1); }
    public int getFarmRange() { return data.get(2); }
    public boolean isRangeVisible() { return data.get(3) != 0; }

    public MachineRedstoneMode getRedstoneMode() {
        MachineRedstoneMode[] values = MachineRedstoneMode.values();
        return values[Math.floorMod(data.get(4), values.length)];
    }

    public MachineIOMode getSideMode(Direction direction) {
        MachineIOMode[] values = MachineIOMode.values();
        return values[Math.floorMod(data.get(5 + direction.ordinal()), values.length)];
    }

    public boolean isSupplySlotLocked(int supplyIndex) {
        return supplyIndex >= 0 && supplyIndex < 4 && data.get(11 + supplyIndex) != 0;
    }

    @Override
    public boolean clickMenuButton(Player player, int id) {
        if (id >= FIRST_SUPPLY_LOCK_BUTTON_ID && id < FIRST_SUPPLY_LOCK_BUTTON_ID + 4) {
            if (!player.level().isClientSide) station.toggleSupplySlotLocked(id - FIRST_SUPPLY_LOCK_BUTTON_ID);
            return true;
        }
        if (id >= FIRST_SIDE_BUTTON_ID && id < FIRST_SIDE_BUTTON_ID + 6) {
            if (!player.level().isClientSide) station.cycleSideMode(Direction.values()[id - FIRST_SIDE_BUTTON_ID]);
            return true;
        }
        if (id == REDSTONE_BUTTON_ID) {
            if (!player.level().isClientSide) station.cycleRedstoneMode();
            return true;
        }
        if (id == RANGE_BUTTON_ID) {
            if (!player.level().isClientSide) station.toggleShowRange();
            return true;
        }
        return super.clickMenuButton(player, id);
    }

    @Override
    public boolean stillValid(Player player) {
        if (station.isRemoved() || station.getLevel() != player.level()) return false;
        double dx = player.getX() - (station.getBlockPos().getX() + 0.5D);
        double dy = player.getY() - (station.getBlockPos().getY() + 0.5D);
        double dz = player.getZ() - (station.getBlockPos().getZ() + 0.5D);
        return dx * dx + dy * dy + dz * dz <= 64.0D;
    }

    @Override
    public ItemStack quickMoveStack(Player player, int index) {
        if (index < 0 || index >= slots.size()) return ItemStack.EMPTY;
        var slot = slots.get(index);
        if (!slot.hasItem()) return ItemStack.EMPTY;

        ItemStack stack = slot.getItem();
        ItemStack original = stack.copy();
        if (index < MACHINE_SLOT_COUNT) {
            if (!moveItemStackTo(stack, MACHINE_SLOT_COUNT, slots.size(), true)) return ItemStack.EMPTY;
        } else if (!moveItemStackTo(stack, 0, MACHINE_SLOT_COUNT, false)) {
            return ItemStack.EMPTY;
        }

        if (stack.isEmpty()) slot.set(ItemStack.EMPTY);
        else slot.setChanged();
        slot.onTake(player, stack);
        return original;
    }
}
