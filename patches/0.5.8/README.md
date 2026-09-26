# 0.5.8 Inventory Panel Return / Storage Area parity

This pass restores the classic 1.12.2 Inventory Panel's 5x3 Return Area / Storage Area mode behavior on Minecraft 1.20.1.

- The 15 panel slots are now persistent block-entity storage instead of an ephemeral menu buffer.
- **Return Area** mode automatically exports those slots into the connected storage network.
- **Storage Area** mode disables that automatic export and keeps the 15 slots local to the panel.
- The GUI can toggle between Return Area and Storage Area with the classic area control.
- Local Storage contents participate in stored-recipe loading and crafting-grid refill calculations before the network is queried.
- The mode and all 15 slot contents persist through GUI close, chunk unload, and world restart.
- Switching from Storage Area back to Return Area immediately attempts to flush the local contents into connected storage.

This mirrors the legacy `extractionDisabled` behavior from Ender IO 5.3.72 while retaining the reconstructed 1.20.1 menu/network architecture.
