import os

import pygame

from app.common.constants import IMAGES_DIRECTORY
from app.db import (
    colormap,
    font,
    frame,
    genericpokemon,
    groundmap,
    move,
    music,
    pokemonsprite,
    portrait,
    tileset,
    damage_chart,
    statanimation,
    item
)
from app.model.animation import Animation

# Databases
music_db = music.MusicDatabase()
colormap_db = colormap.ColorMapDatabase()
tileset_db = tileset.TilesetDatabase()
move_db = move.MoveDatabase()
groundmap_db = groundmap.GroundMapDatabase()
genericpokemon_db = genericpokemon.GenericPokemonDatabase()
pokemonsprite_db = pokemonsprite.PokemonSpriteDatabase()
portrait_db = portrait.PortraitDatabase()
frame_db = frame.FrameDatabase()
font_db = font.FontDatabase()
statanimation_db = statanimation.StatAnimDatabase()
item_db = item.ItemDatabase()

stat_stage_chart = damage_chart.StatStageChart()
type_chart = damage_chart.TypeChart()

# Surfaces
empty_surface = pygame.Surface((0, 0))

pointer_surface_path = os.path.join(IMAGES_DIRECTORY, "misc", "pointer.png")
pointer_surface = pygame.image.load(pointer_surface_path)
pointer_surface.set_colorkey(pointer_surface.get_at((0, 0)))

# Animations
pointer_animation = Animation([pointer_surface, empty_surface], [30, 30])
