from pathlib import Path
import shutil
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
patch_root = Path(__file__).resolve().parent

props = root / "gradle.properties"
text = props.read_text()
if "mod_version=0.6.1-alpha" not in text:
    raise RuntimeError("Expected validated 0.6.1-alpha source base")
props.write_text(text.replace("mod_version=0.6.1-alpha", "mod_version=0.6.2-alpha", 1))

# Replace the runtime channel index with the restored public/private channel-list implementation.
network_target = root / "src/main/java/com/loyacrown/enderlegacy/util/DimensionalTransceiverNetwork.java"
shutil.copyfile(patch_root / "DimensionalTransceiverNetwork.java", network_target)

be_path = root / "src/main/java/com/loyacrown/enderlegacy/blockentity/DimensionalTransceiverBlockEntity.java"
be = be_path.read_text()

def replace_once(content, old, new, label):
    if old not in content:
        raise RuntimeError(f"0.6.2 patch anchor missing: {label}")
    return content.replace(old, new, 1)

be = replace_once(be,
    "import com.loyacrown.enderlegacy.util.MachineInteractionUtil;",
    "import com.loyacrown.enderlegacy.util.MachineInteractionUtil;\nimport com.loyacrown.enderlegacy.util.MachineIOMode;",
    "MachineIOMode import")
be = replace_once(be,
    "    private final EnumSet<ResourceType> privateChannels = EnumSet.noneOf(ResourceType.class);",
    "    private final EnumSet<ResourceType> privateChannels = EnumSet.noneOf(ResourceType.class);\n"
    "    private final EnumMap<Direction, MachineIOMode> sideModes = new EnumMap<>(Direction.class);",
    "side mode field")
be = replace_once(be,
    "        for (ResourceType type : ResourceType.values()) {\n"
    "            channels.put(type, \"default\");\n"
    "            modes.put(type, Mode.BOTH);\n"
    "        }",
    "        for (ResourceType type : ResourceType.values()) {\n"
    "            channels.put(type, \"default\");\n"
    "            modes.put(type, Mode.BOTH);\n"
    "        }\n"
    "        for (Direction direction : Direction.values()) sideModes.put(direction, MachineIOMode.INPUT_OUTPUT);",
    "side mode defaults")
be = replace_once(be,
    "    public UUID getOwner() {\n        return owner;\n    }",
    "    public UUID getOwner() {\n        return owner;\n    }\n\n"
    "    public MachineIOMode getSideMode(Direction direction) {\n"
    "        return sideModes.getOrDefault(direction, MachineIOMode.INPUT_OUTPUT);\n"
    "    }\n\n"
    "    public int getSideModeOrdinal(Direction direction) { return getSideMode(direction).ordinal(); }\n\n"
    "    public void cycleSideMode(Direction direction) {\n"
    "        sideModes.put(direction, getSideMode(direction).next());\n"
    "        setChangedAndSync();\n"
    "    }\n\n"
    "    public java.util.List<String> getAvailableChannels(ResourceType type) {\n"
    "        return DimensionalTransceiverNetwork.listChannels(this, type, isPrivate(type));\n"
    "    }\n\n"
    "    public void cycleAvailableChannel(ResourceType type, boolean backwards) {\n"
    "        java.util.List<String> available = getAvailableChannels(type);\n"
    "        if (available.isEmpty()) return;\n"
    "        String current = getChannel(type);\n"
    "        int index = available.indexOf(current);\n"
    "        if (index < 0) index = 0;\n"
    "        int next = Math.floorMod(index + (backwards ? -1 : 1), available.size());\n"
    "        channels.put(type, available.get(next));\n"
    "        setChangedAndSync();\n"
    "    }",
    "channel-list helpers")
be = replace_once(be,
    "        if (cap == ForgeCapabilities.ITEM_HANDLER) return itemCapability.cast();\n"
    "        if (cap == ForgeCapabilities.FLUID_HANDLER) return fluidCapability.cast();",
    "        if (side != null && getSideMode(side) == MachineIOMode.DISABLED) return LazyOptional.empty();\n"
    "        if (cap == ForgeCapabilities.ITEM_HANDLER) return itemCapability.cast();\n"
    "        if (cap == ForgeCapabilities.FLUID_HANDLER) return fluidCapability.cast();",
    "side disabled capability gate")
be = replace_once(be,
    "        if (!registered) registerNetwork();\n        if (++tickCounter < 5) return;",
    "        if (!registered) registerNetwork();\n"
    "        if (!isMachineEnabledByRedstone()) return;\n"
    "        if (++tickCounter < 5) return;",
    "redstone gate")
be = replace_once(be,
    "            case 2 -> {\n"
    "                if (privateChannels.contains(selectedType)) privateChannels.remove(selectedType);\n"
    "                else privateChannels.add(selectedType);\n"
    "            }\n"
    "            default -> { return; }",
    "            case 2 -> {\n"
    "                if (privateChannels.contains(selectedType)) privateChannels.remove(selectedType);\n"
    "                else privateChannels.add(selectedType);\n"
    "            }\n"
    "            case 3 -> cycleAvailableChannel(selectedType, false);\n"
    "            case 4 -> cycleAvailableChannel(selectedType, true);\n"
    "            case 5 -> cycleRedstoneMode();\n"
    "            default -> {\n"
    "                if (buttonId >= 10 && buttonId < 16) cycleSideMode(Direction.values()[buttonId - 10]);\n"
    "                else return;\n"
    "            }",
    "expanded menu buttons")
be = replace_once(be,
    "                    case 6 -> countItems();\n                    default -> 0;",
    "                    case 6 -> countItems();\n"
    "                    case 7 -> getRedstoneMode().ordinal();\n"
    "                    case 8 -> getSideModeOrdinal(Direction.DOWN);\n"
    "                    case 9 -> getSideModeOrdinal(Direction.UP);\n"
    "                    case 10 -> getSideModeOrdinal(Direction.NORTH);\n"
    "                    case 11 -> getSideModeOrdinal(Direction.SOUTH);\n"
    "                    case 12 -> getSideModeOrdinal(Direction.WEST);\n"
    "                    case 13 -> getSideModeOrdinal(Direction.EAST);\n"
    "                    default -> 0;",
    "expanded menu data")
be = replace_once(be, "                return 7;", "                return 14;", "menu data count")
be = replace_once(be,
    "        tag.putString(\"SelectedType\", selectedType.name());",
    "        tag.putString(\"SelectedType\", selectedType.name());\n"
    "        CompoundTag sides = new CompoundTag();\n"
    "        for (Direction direction : Direction.values()) sides.putString(direction.getName(), getSideMode(direction).name());\n"
    "        tag.put(\"SideModes\", sides);",
    "side mode save")
be = replace_once(be,
    "        owner = tag.hasUUID(\"Owner\") ? tag.getUUID(\"Owner\") : null;\n"
    "        inventory.deserializeNBT(tag.getCompound(\"Inventory\"));",
    "        owner = tag.hasUUID(\"Owner\") ? tag.getUUID(\"Owner\") : null;\n"
    "        CompoundTag sides = tag.getCompound(\"SideModes\");\n"
    "        for (Direction direction : Direction.values()) {\n"
    "            String saved = sides.getString(direction.getName());\n"
    "            if (!saved.isBlank()) {\n"
    "                try { sideModes.put(direction, MachineIOMode.valueOf(saved)); }\n"
    "                catch (IllegalArgumentException ignored) { sideModes.put(direction, MachineIOMode.INPUT_OUTPUT); }\n"
    "            }\n"
    "        }\n"
    "        inventory.deserializeNBT(tag.getCompound(\"Inventory\"));",
    "side mode load")
be_path.write_text(be)

menu_path = root / "src/main/java/com/loyacrown/enderlegacy/menu/DimensionalTransceiverMenu.java"
menu = menu_path.read_text()
menu = replace_once(menu,
    "import com.loyacrown.enderlegacy.registry.LegacyMenus;",
    "import com.loyacrown.enderlegacy.registry.LegacyMenus;\n"
    "import com.loyacrown.enderlegacy.util.MachineIOMode;\n"
    "import com.loyacrown.enderlegacy.util.MachineRedstoneMode;\n"
    "import net.minecraft.core.Direction;",
    "menu machine mode imports")
menu = replace_once(menu,
    "public class DimensionalTransceiverMenu extends AbstractContainerMenu {\n    private static final int MACHINE_SLOT_COUNT = 9;",
    "public class DimensionalTransceiverMenu extends AbstractContainerMenu {\n"
    "    public static final int RESOURCE_BUTTON_ID = 0;\n"
    "    public static final int MODE_BUTTON_ID = 1;\n"
    "    public static final int PRIVACY_BUTTON_ID = 2;\n"
    "    public static final int NEXT_CHANNEL_BUTTON_ID = 3;\n"
    "    public static final int PREVIOUS_CHANNEL_BUTTON_ID = 4;\n"
    "    public static final int REDSTONE_BUTTON_ID = 5;\n"
    "    public static final int FIRST_SIDE_BUTTON_ID = 10;\n"
    "    private static final int MACHINE_SLOT_COUNT = 9;",
    "menu button ids")
menu = replace_once(menu, "new SimpleContainerData(7)", "new SimpleContainerData(14)", "client data count")
menu = replace_once(menu,
    "    public String getSelectedChannelName() {\n        return transceiver.getChannel(getSelectedType());\n    }",
    "    public String getSelectedChannelName() {\n        return transceiver.getChannel(getSelectedType());\n    }\n\n"
    "    public MachineRedstoneMode getRedstoneMode() {\n"
    "        MachineRedstoneMode[] values = MachineRedstoneMode.values();\n"
    "        return values[Math.floorMod(data.get(7), values.length)];\n"
    "    }\n\n"
    "    public MachineIOMode getSideMode(Direction direction) {\n"
    "        MachineIOMode[] values = MachineIOMode.values();\n"
    "        return values[Math.floorMod(data.get(8 + direction.ordinal()), values.length)];\n"
    "    }",
    "menu getters")
menu = replace_once(menu,
    "        if (id >= 0 && id <= 2) {\n            if (!player.level().isClientSide) transceiver.handleMenuButton(player, id);\n            return true;\n        }",
    "        if ((id >= 0 && id <= REDSTONE_BUTTON_ID)\n"
    "                || (id >= FIRST_SIDE_BUTTON_ID && id < FIRST_SIDE_BUTTON_ID + 6)) {\n"
    "            if (!player.level().isClientSide) transceiver.handleMenuButton(player, id);\n"
    "            return true;\n"
    "        }",
    "menu click handling")
menu_path.write_text(menu)

screen_path = root / "src/main/java/com/loyacrown/enderlegacy/client/DimensionalTransceiverScreen.java"
screen = screen_path.read_text()
screen = replace_once(screen,
    "    private Button privacyButton;",
    "    private Button privacyButton;\n"
    "    private Button previousChannelButton;\n"
    "    private Button nextChannelButton;\n"
    "    private Button redstoneButton;",
    "screen extra buttons")
screen = replace_once(screen,
    "        privacyButton = addRenderableWidget(Button.builder(Component.empty(), button -> sendButton(2))\n"
    "                .bounds(leftPos + 126, topPos + 58, 46, 16).build());\n"
    "        refreshButtons();",
    "        privacyButton = addRenderableWidget(Button.builder(Component.empty(), button -> sendButton(2))\n"
    "                .bounds(leftPos + 126, topPos + 58, 46, 16).build());\n"
    "        previousChannelButton = addRenderableWidget(Button.builder(Component.literal(\"<\"), button -> sendButton(4))\n"
    "                .bounds(leftPos + 90, topPos + 1, 16, 16).build());\n"
    "        nextChannelButton = addRenderableWidget(Button.builder(Component.literal(\">\"), button -> sendButton(3))\n"
    "                .bounds(leftPos + 154, topPos + 1, 16, 16).build());\n"
    "        redstoneButton = addRenderableWidget(Button.builder(Component.empty(), button -> sendButton(5))\n"
    "                .bounds(leftPos + 108, topPos + 1, 16, 16).build());\n"
    "        refreshButtons();",
    "screen channel/redstone controls")
screen = replace_once(screen,
    "        if (privacyButton != null) privacyButton.setMessage(Component.literal(menu.isSelectedPrivate() ? \"PRIVATE\" : \"PUBLIC\"));",
    "        if (privacyButton != null) privacyButton.setMessage(Component.literal(menu.isSelectedPrivate() ? \"PRIVATE\" : \"PUBLIC\"));\n"
    "        if (redstoneButton != null) redstoneButton.setMessage(Component.literal(switch (menu.getRedstoneMode()) {\n"
    "            case ALWAYS_ACTIVE -> \"●\";\n"
    "            case ACTIVE_WITH_SIGNAL -> \"+\";\n"
    "            case ACTIVE_WITHOUT_SIGNAL -> \"−\";\n"
    "            case NEVER_ACTIVE -> \"×\";\n"
    "        }));",
    "screen redstone glyph")
screen = replace_once(screen,
    "        graphics.drawString(font, Component.literal(\"Ch: \" + menu.getSelectedChannelName()), 92, 7, 0x404040, false);",
    "        String channel = menu.getSelectedChannelName();\n"
    "        if (channel.length() > 9) channel = channel.substring(0, 8) + \"…\";\n"
    "        graphics.drawString(font, Component.literal(\"Ch: \" + channel), 92, 7, 0x404040, false);",
    "screen channel label")
screen = replace_once(screen,
    "        } else if (localX >= 25 && localX <= 45 && localY >= 20 && localY <= 72) {\n"
    "            graphics.renderTooltip(font,\n"
    "                    Component.literal(menu.getFluidAmount() + \" / 16000 mB\"), mouseX, mouseY);\n"
    "        }",
    "        } else if (localX >= 25 && localX <= 45 && localY >= 20 && localY <= 72) {\n"
    "            graphics.renderTooltip(font,\n"
    "                    Component.literal(menu.getFluidAmount() + \" / 16000 mB\"), mouseX, mouseY);\n"
    "        } else if (localX >= 90 && localX <= 170 && localY >= 1 && localY <= 17) {\n"
    "            graphics.renderTooltip(font, Component.literal((menu.isSelectedPrivate() ? \"Private\" : \"Public\")\n"
    "                    + \" \" + menu.getSelectedType().name().toLowerCase() + \" channel: \"\n"
    "                    + menu.getSelectedChannelName()), mouseX, mouseY);\n"
    "        }",
    "screen control tooltip")
screen_path.write_text(screen)

checks = [
    ("listChannels(this, type, isPrivate(type))", be),
    ("isMachineEnabledByRedstone", be),
    ("SideModes", be),
    ("NEXT_CHANNEL_BUTTON_ID", menu),
    ("REDSTONE_BUTTON_ID", menu),
    ("new SimpleContainerData(14)", menu),
    ("previousChannelButton", screen),
    ("redstoneButton", screen),
]
for token, content in checks:
    if token not in content:
        raise RuntimeError(f"0.6.2 parity invariant missing: {token}")

print("Applied 0.6.2 Dimensional Transceiver parity patch")
