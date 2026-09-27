package com.loyacrown.enderlegacy.client;

import com.loyacrown.enderlegacy.LoyaCrownsEnderLegacy;
import com.loyacrown.enderlegacy.menu.FarmingStationMenu;
import com.loyacrown.enderlegacy.util.MachineIOMode;
import com.loyacrown.enderlegacy.util.MachineRedstoneMode;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;

import java.util.EnumMap;
import java.util.Map;

/**
 * Compact Farming Station screen styled after the current Ender IO machine UI.
 * Functionality remains the SkyFactory 3 / Ender IO 3.1.193 16-slot machine.
 */
public class FarmingStationScreen extends AbstractContainerScreen<FarmingStationMenu> {
    private static final ResourceLocation TEXTURE = new ResourceLocation(
            LoyaCrownsEnderLegacy.MOD_ID, "textures/gui/farm_station.png");

    private Button redstoneButton;
    private Button ioButton;
    private Button rangeButton;
    private final Map<Direction, Button> sideButtons = new EnumMap<>(Direction.class);
    private boolean ioOverlayVisible;

    public FarmingStationScreen(FarmingStationMenu menu, Inventory inventory, Component title) {
        super(menu, inventory, title);
        this.imageWidth = 184;
        this.imageHeight = 169;
        this.inventoryLabelY = 75;
        this.titleLabelY = 6;
    }

    @Override
    protected void init() {
        super.init();
        int controlsX = leftPos + imageWidth - 6 - 16;

        redstoneButton = addRenderableWidget(Button.builder(Component.literal(redstoneGlyph()), button -> {
            if (minecraft != null && minecraft.gameMode != null) {
                minecraft.gameMode.handleInventoryButtonClick(menu.containerId, FarmingStationMenu.REDSTONE_BUTTON_ID);
            }
        }).bounds(controlsX, topPos + 6, 16, 16).build());

        ioButton = addRenderableWidget(Button.builder(Component.literal("IO"), button -> {
            ioOverlayVisible = !ioOverlayVisible;
            updateOverlayVisibility();
        }).bounds(controlsX, topPos + 24, 16, 16).build());

        rangeButton = addRenderableWidget(Button.builder(Component.literal("F"), button -> {
            if (minecraft != null && minecraft.gameMode != null) {
                minecraft.gameMode.handleInventoryButtonClick(menu.containerId, FarmingStationMenu.RANGE_BUTTON_ID);
            }
        }).bounds(controlsX, topPos + 42, 16, 16).build());

        sideButtons.clear();
        Direction[] directions = {Direction.DOWN, Direction.UP, Direction.NORTH, Direction.SOUTH, Direction.WEST, Direction.EAST};
        int startX = leftPos + 34;
        int startY = topPos + 39;
        for (int i = 0; i < directions.length; i++) {
            Direction direction = directions[i];
            int x = startX + (i % 3) * 42;
            int y = startY + (i / 3) * 19;
            Button button = addRenderableWidget(Button.builder(Component.literal(sideGlyph(direction)), ignored -> {
                if (minecraft != null && minecraft.gameMode != null) {
                    minecraft.gameMode.handleInventoryButtonClick(menu.containerId,
                            FarmingStationMenu.FIRST_SIDE_BUTTON_ID + direction.ordinal());
                }
            }).bounds(x, y, 38, 16).build());
            sideButtons.put(direction, button);
        }
        updateOverlayVisibility();
    }

    private void updateOverlayVisibility() {
        for (Button button : sideButtons.values()) button.visible = ioOverlayVisible;
    }

    private String redstoneGlyph() {
        return switch (menu.getRedstoneMode()) {
            case ALWAYS_ACTIVE -> "●";
            case ACTIVE_WITH_SIGNAL -> "+";
            case ACTIVE_WITHOUT_SIGNAL -> "−";
            case NEVER_ACTIVE -> "×";
        };
    }

    private String sideGlyph(Direction direction) {
        String side = switch (direction) {
            case DOWN -> "D";
            case UP -> "U";
            case NORTH -> "N";
            case SOUTH -> "S";
            case WEST -> "W";
            case EAST -> "E";
        };
        String mode = switch (menu.getSideMode(direction)) {
            case DISABLED -> "-";
            case INPUT -> "I";
            case OUTPUT -> "O";
            case INPUT_OUTPUT -> "B";
        };
        return side + ":" + mode;
    }

    @Override
    protected void renderBg(GuiGraphics graphics, float partialTick, int mouseX, int mouseY) {
        graphics.blit(TEXTURE, leftPos, topPos, 0, 0, imageWidth, imageHeight);

        int max = Math.max(1, menu.getMaxEnergyStored());
        int stored = Math.max(0, Math.min(menu.getEnergyStored(), max));
        int barHeight = 43;
        int filled = Math.round((stored / (float) max) * barHeight);
        if (filled > 0) {
            int bottom = topPos + 59;
            graphics.fill(leftPos + 16, bottom - filled, leftPos + 23, bottom, 0xFFB24A35);
        }

        // Activity lamp in the same right-side control stack used by modern Ender IO.
        int lampColor = stored > 0 ? 0xFF4EA75B : 0xFF555555;
        graphics.fill(leftPos + imageWidth - 20, topPos + 64, leftPos + imageWidth - 8, topPos + 76, 0xFF171717);
        graphics.fill(leftPos + imageWidth - 18, topPos + 66, leftPos + imageWidth - 10, topPos + 74, lampColor);

        if (ioOverlayVisible) {
            graphics.fill(leftPos + 27, topPos + 33, leftPos + 159, topPos + 80, 0xEE202020);
            graphics.fill(leftPos + 28, topPos + 34, leftPos + 158, topPos + 79, 0xEE454545);
            graphics.drawCenteredString(font, Component.literal("I/O Configuration"), leftPos + 93, topPos + 35, 0xFFE6E6E6);
        }

        drawSupplyLock(graphics, 0, 36, 43);
        drawSupplyLock(graphics, 1, 88, 43);
        drawSupplyLock(graphics, 2, 36, 63);
        drawSupplyLock(graphics, 3, 88, 63);
    }

    private void drawSupplyLock(GuiGraphics graphics, int index, int x, int y) {
        boolean locked = menu.isSupplySlotLocked(index);
        int left = leftPos + x;
        int top = topPos + y;
        graphics.fill(left, top, left + 8, top + 8, 0xFF181818);
        graphics.fill(left + 1, top + 1, left + 7, top + 7, locked ? 0xFFC28B31 : 0xFF626262);
        if (locked) {
            graphics.fill(left + 2, top - 2, left + 6, top + 1, 0xFFC28B31);
            graphics.fill(left + 2, top - 1, left + 3, top + 2, 0xFFC28B31);
            graphics.fill(left + 5, top - 1, left + 6, top + 2, 0xFFC28B31);
        }
    }

    @Override
    protected void renderLabels(GuiGraphics graphics, int mouseX, int mouseY) {
        // Current Ender IO machine screens keep labels visually minimal. The block title,
        // energy, redstone and I/O state are exposed through hover tooltips instead.
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        if (redstoneButton != null) redstoneButton.setMessage(Component.literal(redstoneGlyph()));
        for (var entry : sideButtons.entrySet()) entry.getValue().setMessage(Component.literal(sideGlyph(entry.getKey())));

        renderBackground(graphics);
        super.render(graphics, mouseX, mouseY, partialTick);
        renderTooltip(graphics, mouseX, mouseY);

        int localX = mouseX - leftPos;
        int localY = mouseY - topPos;
        if (localX >= 14 && localX <= 25 && localY >= 14 && localY <= 61) {
            graphics.renderTooltip(font,
                    Component.literal(menu.getEnergyStored() + " / " + menu.getMaxEnergyStored() + " FE"), mouseX, mouseY);
        } else if (localX >= 162 && localX <= 178 && localY >= 6 && localY <= 22) {
            graphics.renderTooltip(font, Component.literal("Redstone: " + menu.getRedstoneMode().displayName()), mouseX, mouseY);
        } else if (localX >= 162 && localX <= 178 && localY >= 24 && localY <= 40) {
            graphics.renderTooltip(font, Component.literal("Configure side I/O"), mouseX, mouseY);
        } else if (localX >= 162 && localX <= 178 && localY >= 42 && localY <= 58) {
            graphics.renderTooltip(font, Component.literal((menu.isRangeVisible() ? "Hide" : "Show")
                    + " farming range (" + menu.getFarmRange() + ")"), mouseX, mouseY);
        } else {
            int lock = supplyLockAt(localX, localY);
            if (lock >= 0) {
                graphics.renderTooltip(font, Component.literal(menu.isSupplySlotLocked(lock)
                        ? "Unlock supply slot " + (lock + 1)
                        : "Lock supply slot " + (lock + 1)), mouseX, mouseY);
            }
        }
    }

    private static int supplyLockAt(double x, double y) {
        int[][] positions = {{36, 43}, {88, 43}, {36, 63}, {88, 63}};
        for (int i = 0; i < positions.length; i++) {
            int px = positions[i][0];
            int py = positions[i][1];
            if (x >= px - 1 && x < px + 9 && y >= py - 3 && y < py + 9) return i;
        }
        return -1;
    }

    @Override
    public boolean mouseClicked(double mouseX, double mouseY, int button) {
        if (button == 0 && !ioOverlayVisible) {
            int lock = supplyLockAt(mouseX - leftPos, mouseY - topPos);
            if (lock >= 0 && minecraft != null && minecraft.gameMode != null) {
                minecraft.gameMode.handleInventoryButtonClick(menu.containerId,
                        FarmingStationMenu.FIRST_SUPPLY_LOCK_BUTTON_ID + lock);
                return true;
            }
        }
        return super.mouseClicked(mouseX, mouseY, button);
    }
}
