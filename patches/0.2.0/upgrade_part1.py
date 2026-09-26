from pathlib import Path
import json, zipfile, shutil, copy, sys

if len(sys.argv) != 4:
    raise SystemExit('usage: upgrade_from_1_12_2.py <source-root> <EnderIO-1.12.2-5.3.72.jar> <EnderIO-1.7.10-2.2.8.381.jar>')
root=Path(sys.argv[1]).resolve()
jar12=Path(sys.argv[2]).resolve()
jar17=Path(sys.argv[3]).resolve()
res=root/'src/main/resources'
assets=res/'assets/loyacrowns_ender_legacy'
tex=assets/'textures/block'
models=assets/'models/block'
items=assets/'models/item'
states=assets/'blockstates'
data=res/'data/loyacrowns_ender_legacy'
recipes=data/'recipes'
loot=data/'loot_tables/blocks'
for d in [tex,models,items,states,recipes,loot]: d.mkdir(parents=True, exist_ok=True)

# Branding/version made permanent in the source snapshot.
gp=root/'gradle.properties'
s=gp.read_text()
s=s.replace("mod_name=LoyaCrown's Ender Legacy", "mod_name=LoyalCrown's Ender Legacy")
s=s.replace('mod_version=0.1.1-alpha','mod_version=0.2.0-alpha')
gp.write_text(s)

bg=root/'build.gradle'
s=bg.read_text().replace('LoyaCrowns-Ender-Legacy-${minecraft_version}','LoyalCrowns-Ender-Legacy-${minecraft_version}')
s=s.replace("'Specification-Vendor': 'LoyaCrown'", "'Specification-Vendor': 'LoyalCrown'")
s=s.replace("'Implementation-Vendor': 'LoyaCrown'", "'Implementation-Vendor': 'LoyalCrown'")
bg.write_text(s)

mods=res/'META-INF/mods.toml'
s=mods.read_text().replace('authors="LoyaCrown"','authors="LoyalCrown"')
mods.write_text(s)

readme=root/'README.md'
s=readme.read_text().replace("# LoyaCrown's Ender Legacy", "# LoyalCrown's Ender Legacy")
readme.write_text(s)

# exact texture extraction helpers
def extract(jar, src, dst):
    with zipfile.ZipFile(jar) as z:
        b=z.read(src)
    dst=Path(dst); dst.parent.mkdir(parents=True, exist_ok=True); dst.write_bytes(b)

# 1.12.2 textures are now the preferred visual reference when that block still existed there.
exact12={
    'machine_side_1_12.png':'assets/enderio/textures/blocks/block_machine_side.png',
    'machine_top_1_12.png':'assets/enderio/textures/blocks/block_machine_top.png',
    'machine_bottom_1_12.png':'assets/enderio/textures/blocks/block_machine_bottom.png',
    'combustion_generator_1_12.png':'assets/enderio/textures/blocks/combustion_gen_front.png',
    'combustion_generator_top_1_12.png':'assets/enderio/textures/blocks/combustion_gen_top.png',
    'reservoir_1_12.png':'assets/enderio/textures/blocks/reservoir.png',
    'power_monitor_1_12.png':'assets/enderio/textures/blocks/power_monitor.png',
    'dimensional_transceiver_1_12.png':'assets/enderio/textures/blocks/block_transceiver.png',
    'photovoltaic_cell_side_1_12.png':'assets/enderio/textures/blocks/solar_panel_normal_side.png',
    'photovoltaic_cell_top_1_12.png':'assets/enderio/textures/blocks/solar_panel_normal_top.png',
    'advanced_photovoltaic_cell_side_1_12.png':'assets/enderio/textures/blocks/solar_panel_advanced_side.png',
    'advanced_photovoltaic_cell_top_1_12.png':'assets/enderio/textures/blocks/solar_panel_advanced_top.png',
    'farming_station_side_1_12.png':'assets/enderio/textures/blocks/farm_side.png',
    'farming_station_top_1_12.png':'assets/enderio/textures/blocks/farm_base_top.png',
    'exit_rail.png':'assets/enderio/textures/blocks/block_exit_rail.png',
    'dark_steel_anvil_body.png':'assets/enderio/textures/blocks/anvil/base.png',
    'dark_steel_anvil_top.png':'assets/enderio/textures/blocks/anvil/0.png',
    'advanced_power_monitor_frame.png':'assets/enderio/textures/blocks/block_pm_on_frame.png',
    'advanced_power_monitor_screen.png':'assets/enderio/textures/blocks/block_pm_on.png',
}
for out,src in exact12.items(): extract(jar12,src,tex/out)
# animation metadata for the monitor is valid in 1.20.1 too.
extract(jar12,'assets/enderio/textures/blocks/block_pm_on_frame.png.mcmeta',tex/'advanced_power_monitor_frame.png.mcmeta')
extract(jar12,'assets/enderio/textures/blocks/block_pm_on.png.mcmeta',tex/'advanced_power_monitor_screen.png.mcmeta')

# Ender Rail was removed before 1.12.2; use its actual last legacy art instead of a substitute.
for out,src in {
    'ender_rail_north_south.png':'assets/enderio/textures/blocks/blockEnderRail.png',
    'ender_rail_north_south_reversed.png':'assets/enderio/textures/blocks/blockEnderRail_turned.png',
    'ender_rail_east_west.png':'assets/enderio/textures/blocks/blockEnderRailEastWest.png',
    'ender_rail_east_west_reversed.png':'assets/enderio/textures/blocks/blockEnderRailEastWest_turned.png',
}.items(): extract(jar17,src,tex/out)

# Improve existing model texture fidelity using exact 1.12.2 art.
def writej(path,obj):
    Path(path).write_text(json.dumps(obj,indent=2)+"\n")

writej(models/'combustion_generator.json', {
  'parent':'minecraft:block/cube','textures':{
    'down':'loyacrowns_ender_legacy:block/machine_bottom_1_12','up':'loyacrowns_ender_legacy:block/combustion_generator_top_1_12',
    'north':'loyacrowns_ender_legacy:block/combustion_generator_1_12','south':'loyacrowns_ender_legacy:block/machine_side_1_12',
    'west':'loyacrowns_ender_legacy:block/machine_side_1_12','east':'loyacrowns_ender_legacy:block/machine_side_1_12',
    'particle':'loyacrowns_ender_legacy:block/machine_side_1_12'}})
writej(models/'reservoir.json', {'parent':'minecraft:block/cube_all','textures':{'all':'loyacrowns_ender_legacy:block/reservoir_1_12'}})
writej(models/'power_monitor.json', {'parent':'minecraft:block/cube','textures':{
    'down':'loyacrowns_ender_legacy:block/machine_bottom_1_12','up':'loyacrowns_ender_legacy:block/machine_top_1_12',
    'north':'loyacrowns_ender_legacy:block/power_monitor_1_12','south':'loyacrowns_ender_legacy:block/machine_side_1_12',
    'west':'loyacrowns_ender_legacy:block/machine_side_1_12','east':'loyacrowns_ender_legacy:block/machine_side_1_12',
    'particle':'loyacrowns_ender_legacy:block/machine_side_1_12'}})
writej(models/'dimensional_transceiver.json', {'parent':'minecraft:block/cube','textures':{
    'down':'loyacrowns_ender_legacy:block/machine_bottom_1_12','up':'loyacrowns_ender_legacy:block/machine_top_1_12',
    'north':'loyacrowns_ender_legacy:block/dimensional_transceiver_1_12','south':'loyacrowns_ender_legacy:block/machine_side_1_12',
    'west':'loyacrowns_ender_legacy:block/machine_side_1_12','east':'loyacrowns_ender_legacy:block/machine_side_1_12',
    'particle':'loyacrowns_ender_legacy:block/machine_side_1_12'}})
writej(models/'photovoltaic_cell.json', {'parent':'minecraft:block/cube','textures':{
    'down':'loyacrowns_ender_legacy:block/machine_bottom_1_12','up':'loyacrowns_ender_legacy:block/photovoltaic_cell_top_1_12',
    'north':'loyacrowns_ender_legacy:block/photovoltaic_cell_side_1_12','south':'loyacrowns_ender_legacy:block/photovoltaic_cell_side_1_12',
    'west':'loyacrowns_ender_legacy:block/photovoltaic_cell_side_1_12','east':'loyacrowns_ender_legacy:block/photovoltaic_cell_side_1_12',
    'particle':'loyacrowns_ender_legacy:block/photovoltaic_cell_side_1_12'}})
writej(models/'advanced_photovoltaic_cell.json', {'parent':'minecraft:block/cube','textures':{
    'down':'loyacrowns_ender_legacy:block/machine_bottom_1_12','up':'loyacrowns_ender_legacy:block/advanced_photovoltaic_cell_top_1_12',
    'north':'loyacrowns_ender_legacy:block/advanced_photovoltaic_cell_side_1_12','south':'loyacrowns_ender_legacy:block/advanced_photovoltaic_cell_side_1_12',
    'west':'loyacrowns_ender_legacy:block/advanced_photovoltaic_cell_side_1_12','east':'loyacrowns_ender_legacy:block/advanced_photovoltaic_cell_side_1_12',
    'particle':'loyacrowns_ender_legacy:block/advanced_photovoltaic_cell_side_1_12'}})
writej(models/'farming_station.json', {'parent':'minecraft:block/cube','textures':{
    'down':'loyacrowns_ender_legacy:block/machine_bottom_1_12','up':'loyacrowns_ender_legacy:block/farming_station_top_1_12',
    'north':'loyacrowns_ender_legacy:block/farming_station_side_1_12','south':'loyacrowns_ender_legacy:block/farming_station_side_1_12',
    'west':'loyacrowns_ender_legacy:block/farming_station_side_1_12','east':'loyacrowns_ender_legacy:block/farming_station_side_1_12',
    'particle':'loyacrowns_ender_legacy:block/farming_station_side_1_12'}})

# Correct 1.20 anvil geometry, with exact Ender IO 1.12.2 Dark Steel Anvil artwork.
writej(models/'dark_steel_anvil.json', {
  'parent':'minecraft:block/template_anvil',
  'textures':{'particle':'loyacrowns_ender_legacy:block/dark_steel_anvil_body','body':'loyacrowns_ender_legacy:block/dark_steel_anvil_body','top':'loyacrowns_ender_legacy:block/dark_steel_anvil_top'}
})
writej(states/'dark_steel_anvil.json', {'variants':{
    'facing=east':{'model':'loyacrowns_ender_legacy:block/dark_steel_anvil','y':270},
    'facing=north':{'model':'loyacrowns_ender_legacy:block/dark_steel_anvil','y':180},
    'facing=south':{'model':'loyacrowns_ender_legacy:block/dark_steel_anvil'},
    'facing=west':{'model':'loyacrowns_ender_legacy:block/dark_steel_anvil','y':90},
}})

# Ender Rail model set covers every PoweredRailBlock state to prevent missing model/texture squares.
for name,parent,texture in [
    ('ender_rail_ns','minecraft:block/rail_flat','ender_rail_north_south'),
    ('ender_rail_ew','minecraft:block/rail_flat','ender_rail_east_west'),
    ('ender_rail_ns_rev','minecraft:block/rail_flat','ender_rail_north_south_reversed'),
    ('ender_rail_ew_rev','minecraft:block/rail_flat','ender_rail_east_west_reversed'),
    ('ender_rail_ne','minecraft:block/rail_raised_ne','ender_rail_north_south'),
    ('ender_rail_sw','minecraft:block/rail_raised_sw','ender_rail_north_south'),
    ('ender_rail_ne_rev','minecraft:block/rail_raised_ne','ender_rail_north_south_reversed'),
    ('ender_rail_sw_rev','minecraft:block/rail_raised_sw','ender_rail_north_south_reversed'),
]:
    writej(models/(name+'.json'), {'parent':parent,'textures':{'rail':f'loyacrowns_ender_legacy:block/{texture}'}})
variants={}
# mirror vanilla powered-rail key set; powered is used as the old rail's reversed visual state.
for powered,suf in [(False,''),(True,'_rev')]:
    p=str(powered).lower()
    variants[f'powered={p},shape=north_south']={'model':f'loyacrowns_ender_legacy:block/ender_rail_ns{suf}'}
    variants[f'powered={p},shape=east_west']={'model':f'loyacrowns_ender_legacy:block/ender_rail_ew{suf}'}
    variants[f'powered={p},shape=ascending_east']={'model':f'loyacrowns_ender_legacy:block/ender_rail_ne{suf}','y':90}
    variants[f'powered={p},shape=ascending_west']={'model':f'loyacrowns_ender_legacy:block/ender_rail_sw{suf}','y':90}
    variants[f'powered={p},shape=ascending_north']={'model':f'loyacrowns_ender_legacy:block/ender_rail_ne{suf}'}
    variants[f'powered={p},shape=ascending_south']={'model':f'loyacrowns_ender_legacy:block/ender_rail_sw{suf}'}
writej(states/'ender_rail.json', {'variants':variants})
writej(items/'ender_rail.json', {'parent':'loyacrowns_ender_legacy:block/ender_rail_ns'})

# 1.12.2 Exit Rail successor: exact texture and six valid rail shapes.
for name,parent in [('exit_rail','minecraft:block/rail_flat'),('exit_rail_ne','minecraft:block/rail_raised_ne'),('exit_rail_sw','minecraft:block/rail_raised_sw')]:
    writej(models/(name+'.json'), {'parent':parent,'textures':{'rail':'loyacrowns_ender_legacy:block/exit_rail'}})
variants={}
for powered in [False,True]:
    p=str(powered).lower()
    variants[f'powered={p},shape=north_south']={'model':'loyacrowns_ender_legacy:block/exit_rail'}
    variants[f'powered={p},shape=east_west']={'model':'loyacrowns_ender_legacy:block/exit_rail','y':90}
    variants[f'powered={p},shape=ascending_east']={'model':'loyacrowns_ender_legacy:block/exit_rail_ne','y':90}
    variants[f'powered={p},shape=ascending_west']={'model':'loyacrowns_ender_legacy:block/exit_rail_sw','y':90}
    variants[f'powered={p},shape=ascending_north']={'model':'loyacrowns_ender_legacy:block/exit_rail_ne'}
    variants[f'powered={p},shape=ascending_south']={'model':'loyacrowns_ender_legacy:block/exit_rail_sw'}
writej(states/'exit_rail.json',{'variants':variants})
writej(items/'exit_rail.json',{'parent':'loyacrowns_ender_legacy:block/exit_rail'})
