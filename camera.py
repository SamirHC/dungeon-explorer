import constants
import pokemon


class Camera:
    def __init__(self, target: pokemon.Pokemon):
        self.target = target

    @property
    def size(self) -> tuple[int, int]:
        return constants.DISPLAY_SIZE

    @property
    def position(self) -> tuple[int, int]:
        return (self.x, self.y)

    @property
    def x(self) -> int:
        return constants.DISPLAY_WIDTH / 2 - self.target.blit_pos[0]
        #return (self.target.grid_pos[0] - 5) * constants.TILE_SIZE + self.offset[0]

    @property
    def y(self) -> int:
        return constants.DISPLAY_HEIGHT / 2 - self.target.blit_pos[1]
        #return (self.target.grid_pos[1] - 4) * constants.TILE_SIZE + self.offset[1]
