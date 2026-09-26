# Graphical Power Monitor: base cube + exact 1.12.2 frame/screen geometry overlay.
with zipfile.ZipFile(jar12) as z:
    panel=json.loads(z.read('assets/enderio/models/block/block_advanced_power_monitor.json').decode())
    face=json.loads(z.read('assets/enderio/models/block/block_advanced_power_monitor_itemfront.json').decode())
base_cube={
 'from':[0,0,0],'to':[16,16,16],
 'faces':{
   'down':{'texture':'#bottom','cullface':'down'},'up':{'texture':'#top','cullface':'up'},
   'north':{'texture':'#side','cullface':'north'},'south':{'texture':'#side','cullface':'south'},
   'west':{'texture':'#side','cullface':'west'},'east':{'texture':'#side','cullface':'east'}
 }}
# old panel sits at the south face; preserve that exact geometry.
adv_model={
 'textures':{
   'particle':'loyacrowns_ender_legacy:block/machine_side_1_12',
   'bottom':'loyacrowns_ender_legacy:block/machine_bottom_1_12',
   'top':'loyacrowns_ender_legacy:block/machine_top_1_12',
   'side':'loyacrowns_ender_legacy:block/machine_side_1_12',
   'texture':'loyacrowns_ender_legacy:block/advanced_power_monitor_frame',
   'fakeface':'loyacrowns_ender_legacy:block/advanced_power_monitor_screen',
 },
 'elements':[base_cube]+panel.get('elements',[])+face.get('elements',[])
}
writej(models/'advanced_power_monitor.json',adv_model)
writej(states/'advanced_power_monitor.json',{'variants':{'':{'model':'loyacrowns_ender_legacy:block/advanced_power_monitor'}}})
writej(items/'advanced_power_monitor.json',{'parent':'loyacrowns_ender_legacy:block/advanced_power_monitor'})

# New Java block: 1.12 Exit Rail behavior (eject riders then destroy non-furnace minecart).
exit_java=root/'src/main/java/com/loyacrown/enderlegacy/block/LegacyExitRailBlock.java'
exit_java.write_text('''package com.loyacrown.enderlegacy.block;\n\nimport net.minecraft.core.BlockPos;\nimport net.minecraft.world.entity.Entity;\nimport net.minecraft.world.entity.vehicle.AbstractMinecart;\nimport net.minecraft.world.entity.vehicle.MinecartFurnace;\nimport net.minecraft.world.level.Level;\nimport net.minecraft.world.level.block.PoweredRailBlock;\nimport net.minecraft.world.level.block.state.BlockBehaviour;\nimport net.minecraft.world.level.block.state.BlockState;\n\n/**\n * 1.20.1 recreation of Ender IO 5.3.72's Exit Rail. The old rail had a very\n * low max speed, ejected riders, and destroyed ordinary rideable minecarts.\n * Furnace minecarts were explicitly exempt in the 1.12 implementation.\n */\npublic class LegacyExitRailBlock extends PoweredRailBlock {\n    public LegacyExitRailBlock(BlockBehaviour.Properties properties) {\n        super(properties);\n    }\n\n    @Override\n    public void entityInside(BlockState state, Level level, BlockPos pos, Entity entity) {\n        super.entityInside(state, level, pos, entity);\n        if (level.isClientSide || !(entity instanceof AbstractMinecart cart) || cart instanceof MinecartFurnace) {\n            return;\n        }\n        cart.ejectPassengers();\n        cart.discard();\n    }\n}\n''')

# Registry additions.
lb=root/'src/main/java/com/loyacrown/enderlegacy/registry/LegacyBlocks.java'
s=lb.read_text()
s=s.replace('import com.loyacrown.enderlegacy.block.LegacyEnderRailBlock;','import com.loyacrown.enderlegacy.block.LegacyEnderRailBlock;\nimport com.loyacrown.enderlegacy.block.LegacyExitRailBlock;')
s=s.replace('    public static final RegistryObject<Block> POWER_MONITOR = registerBlock("power_monitor",\n            () -> new LegacyPowerMonitorBlock(machineProps(), () -> LegacyBlockEntities.POWER_MONITOR.get()));',
'''    public static final RegistryObject<Block> POWER_MONITOR = registerBlock("power_monitor",\n            () -> new LegacyPowerMonitorBlock(machineProps(), () -> LegacyBlockEntities.POWER_MONITOR.get()));\n    public static final RegistryObject<Block> ADVANCED_POWER_MONITOR = registerBlock("advanced_power_monitor",\n            () -> new LegacyPowerMonitorBlock(machineProps(), () -> LegacyBlockEntities.POWER_MONITOR.get()));''')
s=s.replace('    public static final RegistryObject<Block> ENDER_RAIL = registerBlock("ender_rail",\n            () -> new LegacyEnderRailBlock(BlockBehaviour.Properties.copy(Blocks.POWERED_RAIL).noCollission().strength(0.7F)));',
'''    public static final RegistryObject<Block> ENDER_RAIL = registerBlock("ender_rail",\n            () -> new LegacyEnderRailBlock(BlockBehaviour.Properties.copy(Blocks.POWERED_RAIL).noCollission().strength(0.7F)));\n    public static final RegistryObject<Block> EXIT_RAIL = registerBlock("exit_rail",\n            () -> new LegacyExitRailBlock(BlockBehaviour.Properties.copy(Blocks.POWERED_RAIL).noCollission().strength(0.7F)));''')
lb.write_text(s)

lbe=root/'src/main/java/com/loyacrown/enderlegacy/registry/LegacyBlockEntities.java'
s=lbe.read_text().replace('LegacyBlocks.POWER_MONITOR.get()).build(null));','LegacyBlocks.POWER_MONITOR.get(), LegacyBlocks.ADVANCED_POWER_MONITOR.get()).build(null));')
lbe.write_text(s)

# Lang.
lang=assets/'lang/en_us.json'
d=json.loads(lang.read_text())
d['block.loyacrowns_ender_legacy.advanced_power_monitor']='Graphical Power Monitor'
d['block.loyacrowns_ender_legacy.exit_rail']='Exit Rail'
lang.write_text(json.dumps(dict(sorted(d.items())),indent=2)+"\n")

# Loot & recipes for new blocks.
def self_loot(name):
    return {'type':'minecraft:block','pools':[{'bonus_rolls':0.0,'conditions':[{'condition':'minecraft:survives_explosion'}],'entries':[{'type':'minecraft:item','name':f'loyacrowns_ender_legacy:{name}'}],'rolls':1.0}]}
for name in ['advanced_power_monitor','exit_rail']:
    writej(loot/(name+'.json'),self_loot(name))
writej(recipes/'exit_rail.json',{
 'type':'minecraft:crafting_shaped','category':'transportation','pattern':['IPI','ISI','IRI'],
 'key':{'I':{'tag':'forge:ingots/iron'},'P':{'item':'minecraft:piston'},'S':{'item':'minecraft:stone_pressure_plate'},'R':{'item':'minecraft:redstone'}},
 'result':{'item':'loyacrowns_ender_legacy:exit_rail','count':6},'show_notification':True})
writej(recipes/'advanced_power_monitor.json',{
 'type':'minecraft:crafting_shaped','category':'misc','pattern':['WWW','WPW','RYG'],
 'key':{'W':{'item':'minecraft:black_wool'},'P':{'item':'loyacrowns_ender_legacy:power_monitor'},'R':{'item':'minecraft:red_dye'},'Y':{'item':'minecraft:yellow_dye'},'G':{'item':'minecraft:green_dye'}},
 'result':{'item':'loyacrowns_ender_legacy:advanced_power_monitor'},'show_notification':True})

# Asset validation script catches missing textures/models before a JAR is published.
tools=root/'tools'; tools.mkdir(exist_ok=True)
(tools/'validate_assets.py').write_text(r'''from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parents[1] / 'src/main/resources/assets/loyacrowns_ender_legacy'
errors=[]

def load(path):
    try:
        return json.loads(path.read_text())
    except Exception as e:
        errors.append(f'{path.relative_to(ROOT)}: invalid JSON: {e}')
        return None

def walk_strings(obj, key=None):
    if isinstance(obj, dict):
        for k,v in obj.items():
            yield from walk_strings(v,k)
    elif isinstance(obj, list):
        for v in obj: yield from walk_strings(v,key)
    elif isinstance(obj,str):
        yield key,obj

for path in list((ROOT/'blockstates').glob('*.json')) + list((ROOT/'models').rglob('*.json')):
    obj=load(path)
    if obj is None: continue
    for key,value in walk_strings(obj):
        if key == 'model' and value.startswith('loyacrowns_ender_legacy:'):
            rel=value.split(':',1)[1]
            candidate=ROOT/'models'/(rel+'.json')
            if not candidate.exists(): errors.append(f'{path.relative_to(ROOT)} -> missing model {candidate.relative_to(ROOT)}')
        if key == 'parent' and value.startswith('loyacrowns_ender_legacy:'):
            rel=value.split(':',1)[1]
            candidate=ROOT/'models'/(rel+'.json')
            if not candidate.exists(): errors.append(f'{path.relative_to(ROOT)} -> missing parent {candidate.relative_to(ROOT)}')
        if key not in {'model','parent'} and value.startswith('loyacrowns_ender_legacy:block/'):
            rel=value.split(':',1)[1].replace('block/','',1)
            candidate=ROOT/'textures/block'/(rel+'.png')
            if not candidate.exists(): errors.append(f'{path.relative_to(ROOT)} -> missing texture {candidate.relative_to(ROOT)}')

if errors:
    print('\n'.join(errors))
    sys.exit(1)
print('Asset validation passed: every LoyalCrown model/texture reference resolves.')
''')

# Reference audit from the supplied 1.12.2 JAR.
(root/'REFERENCE_1_12_2.md').write_text('''# Ender IO 1.12.2 reference\n\nReference JAR: `EnderIO-1.12.2-5.3.72.jar`. The addon still targets Minecraft 1.20.1 / Forge 47.4.x / Ender IO 6.2.15-beta; no 1.12 bytecode is loaded at runtime.\n\n## 0.2.0-alpha first-pass changes\n\n- Dark Steel Anvil now uses the correct anvil geometry and exact 1.12.2 body/top artwork.\n- Ender Rail now has complete rail-state models and its original 1.7.10 artwork (the block itself was removed before Ender IO 5.3.72).\n- Added the 1.12.2 Exit Rail with exact 5.3.72 texture and ported eject/destroy behavior.\n- Added the 1.12.2 Graphical Power Monitor using the existing 1.20 power-monitor logic plus the 5.3.72 animated screen/frame artwork.\n- Farming Station, Reservoir, Combustion Generator, Power Monitor, Dimensional Transceiver, and Photovoltaic cells now preferentially use exact 5.3.72 textures where practical.\n- Added automated resource-reference validation so missing model/texture paths fail CI instead of becoming purple/black blocks in game.\n\n## Still queued from 5.3.72\n\nThe 1.12.2 reference also contains removed machines and systems such as the Ender Generator, Frank'n'Zombie Generator, Lava Generator, enhanced machine variants, Inventory Panel/storage blocks, Telepad/Dialing Device, additional obelisks, Electric Lights, and several utility/decorative blocks. These need individual 1.20.1 ports so they do not duplicate blocks already present in Ender IO 6.2.15-beta.\n''')

# Changelog.
(root/'CHANGELOG.md').write_text('''# Changelog\n\n## 0.2.0-alpha\n- Switched the visual reference forward to Ender IO 1.12.2-5.3.72 where applicable.\n- Fixed Dark Steel Anvil geometry/texture.\n- Fixed Ender Rail blockstate coverage and restored original Ender Rail art.\n- Added 1.12.2 Exit Rail with legacy eject/destroy behavior.\n- Added Graphical Power Monitor with 1.12.2 animated display art.\n- Updated several existing machine textures to their 1.12.2 versions.\n- Added automated missing-model/missing-texture validation.\n- Kept Minecraft 1.20.1, Forge 47.4.x, Java 17, and Ender IO 6.2.15-beta compatibility target.\n\n## 0.1.1-alpha\n- Expanded Farming Station crop/tree handling and output routing.\n''')

print('Upgraded source to 0.2.0-alpha')
