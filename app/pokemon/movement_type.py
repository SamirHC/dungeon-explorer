from enum import Enum
from app.dungeon.terrain import Terrain


class MovementType(Enum):
    NORMAL = 0
    # UNUSED = 1
    LEVITATING = 2
    PHASING = 3
    LAVA_WALKER = 4
    WATER_WALKER = 5

    def get_walkable_terrains(self) -> tuple[Terrain]:
        return walkable_tiles[self]
    
    def can_traverse(self, terrain: Terrain) -> bool:
        return terrain in self.get_walkable_terrains()

walkable_tiles = {
    MovementType.NORMAL: (Terrain.GROUND,),
    MovementType.LEVITATING: (
        Terrain.GROUND, Terrain.WATER, Terrain.VOID, Terrain.LAVA),
    MovementType.PHASING: tuple(iter(Terrain)),
    MovementType.WATER_WALKER: (Terrain.GROUND, Terrain.WATER),
    MovementType.LAVA_WALKER: (Terrain.GROUND, Terrain.LAVA)
}
