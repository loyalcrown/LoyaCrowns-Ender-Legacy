from pathlib import Path
import sys

root = Path(sys.argv[1])
p = root / 'src/main/java/com/loyacrown/enderlegacy/client/ClientModEvents.java'
p.write_text('''package com.loyacrown.enderlegacy.client;

import com.loyacrown.enderlegacy.LoyaCrownsEnderLegacy;
import com.loyacrown.enderlegacy.registry.LegacyMenus;
import net.minecraft.client.gui.screens.MenuScreens;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;

@Mod.EventBusSubscriber(modid = LoyaCrownsEnderLegacy.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public final class ClientModEvents {
    private ClientModEvents() {}

    @SubscribeEvent
    public static void onClientSetup(FMLClientSetupEvent event) {
        event.enqueueWork(() ->
                MenuScreens.register(LegacyMenus.FARMING_STATION.get(), FarmingStationScreen::new));
    }
}
''')
print('Fixed Farming Station screen registration for Forge 1.20.1.')
