# 0.6.0 Modern Machine Foundation

This payload is applied on top of the validated `0.5.9-alpha` source snapshot.

It begins the visual/control modernization pass requested for LoyaCrown's Ender Legacy:

- backports the official public-domain Ender IO 1.21.1 Farming Station casing artwork to the 1.20.1 restoration;
- adds persisted machine redstone modes matching modern Ender IO: Always Active, Active With Signal, Active Without Signal, and Never Active;
- adds persisted per-face item and energy IO modes to the shared powered-machine base;
- gives the Farming Station functional Redstone and IO Configuration buttons;
- makes redstone mode actually pause Farming Station work;
- makes sided item/power capabilities honor the selected face configuration;
- preserves the previous 1.12-style Farming Station model as `farming_station_legacy.json` for future skin/resource-pack selection.

The modern artwork comes from Team-EnderIO/EnderIO's 1.21.1 branch, whose `LICENSE.txt` dedicates the project to the public domain.

Payload SHA-256: `799380e0831887f6aa5c8b1775105a7a3d4c79f912236d129111bf1053d3d4b7`
