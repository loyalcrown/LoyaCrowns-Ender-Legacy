# 0.5.7 Inventory Panel power and nutrient parity

This pass builds on the validated 0.5.6 Inventory Panel filter-card implementation and restores the classic 1.12.2 operating-resource model more accurately.

- The Inventory Panel is powered by **Nutrient Distillation**, not external RF/FE.
- The internal nutrient tank holds **2,000 mB**.
- Nutrient Distillation is converted into internal panel power at the classic **800 power per mB** rate.
- Network scanning consumes **0.1 power per backing inventory slot**.
- Extraction consumes **32 power per operation + 12 power per item**.
- Fluid containers can fill the panel through its fluid input capability.
- The panel intentionally does **not** expose an external energy input capability.
- Nutrient amount and internal power persist in NBT and are synchronized to the Inventory Panel GUI.
- The GUI reports whether the panel is online and warns when Nutrient Distillation is required.

These values and the nutrient-powered design are based on the later classic Ender IO 1.12.2 Inventory Panel implementation while the addon remains targeted at Minecraft 1.20.1.
