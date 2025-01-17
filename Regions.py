import typing

from .Logic import can_ice_beam, can_missile, can_phazon, can_plasma_beam, can_power_beam, can_scan, can_super_missile, can_thermal, can_wave_beam, can_xray, has_energy_tanks, has_required_artifact_count
from .LogicCombat import can_combat_prime, can_combat_ridley
from .data.ChozoRuins import ChozoRuinsAreaData
from .data.MagmoorCaverns import MagmoorCavernsAreaData
from .data.PhazonMines import PhazonMinesAreaData
from .data.PhendranaDrifts import PhendranaDriftsAreaData
from .data.RoomNames import RoomName
from .data.TallonOverworld import TallonOverworldAreaData
from BaseClasses import CollectionState, Region
if typing.TYPE_CHECKING:
    from . import MetroidPrimeWorld


def create_regions(world: 'MetroidPrimeWorld', final_boss_selection):
    # create all regions and populate with locations
    menu = Region("Menu", world.player, world.multiworld)
    world.multiworld.regions.append(menu)

    for area_data in world.game_region_data.values():
      area_data.create_world_region(world)

    impact_crater = Region("Impact Crater", world.player, world.multiworld)
    world.multiworld.regions.append(impact_crater)

    mission_complete = Region("Mission Complete", world.player, world.multiworld)
    world.multiworld.regions.append(mission_complete)

    starting_room = world.get_region(world.starting_room_data.name)
    menu.connect(starting_room, "Starting Room")

    def get_region_lambda():
        def can_access_elevator(state: CollectionState):
            if world.options.pre_scan_elevators.value:
                return True
            return can_scan(state, world.player)
        return can_access_elevator

    for area, mappings in world.elevator_mapping.items():
        for elevator, target in mappings.items():
            source = world.multiworld.get_region(elevator, world.player)
            destination = world.multiworld.get_region(target, world.player)
            source.connect(destination, elevator, get_region_lambda())

    artifact_temple = world.multiworld.get_region(RoomName.Artifact_Temple.value, world.player)

    if final_boss_selection == 0 or final_boss_selection == 2:
        artifact_temple.connect(impact_crater, "Crater Access", lambda state: (
            can_missile(state, world.player) and
            has_required_artifact_count(state, world.player) and
            can_combat_prime(state, world.player) and
            can_combat_ridley(state, world.player) and
            can_phazon(state, world.player) and
            can_plasma_beam(state, world.player) and can_wave_beam(state, world.player) and can_ice_beam(state, world.player) and can_power_beam(state, world.player) and
            can_xray(state, world.player, True) and can_thermal(state, world.player, True)))
        impact_crater.connect(mission_complete, "Mission Complete")

    elif final_boss_selection == 1:
        artifact_temple.connect(mission_complete, "Mission Complete", lambda state:
                                can_missile(state, world.player) and
                                has_required_artifact_count(state, world.player) and (can_plasma_beam(state, world.player) or can_super_missile(state, world.player)) and
                                can_combat_ridley(state, world.player)
                                )
    elif final_boss_selection == 3:
        artifact_temple.connect(mission_complete, "Mission Complete", lambda state: (
            can_missile(state, world.player) and
            has_required_artifact_count(state, world.player)))

    # from Utils import visualize_regions
    # visualize_regions(world.multiworld.get_region("Menu", world.player), "my_world.puml")
