import os
import sqlite3

import pygame

from app.common import constants
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
    item,
)
from app.model.animation import Animation

# Databases
main_db = None

music_db = None
colormap_db = None
tileset_db = None
move_db = None
groundmap_db = None
genericpokemon_db = None
pokemonsprite_db = None
portrait_db = None
frame_db = None
font_db = None
statanimation_db = None
item_db = None

stat_stage_chart = None
type_chart = None

# Surfaces
pointer_surface = None

# Animations
pointer_animation = None


def init_database():
    global main_db

    global music_db
    global colormap_db
    global tileset_db
    global move_db
    global groundmap_db
    global genericpokemon_db
    global pokemonsprite_db
    global portrait_db
    global frame_db
    global font_db
    global statanimation_db
    global item_db

    global stat_stage_chart
    global type_chart

    # Surfaces
    global pointer_surface

    # Animations
    global pointer_animation

    # Databases
    main_db = sqlite3.connect(os.path.join(constants.GAMEDATA_DIRECTORY, "gamedata.db"))

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
    pointer_surface_path = os.path.join(constants.IMAGES_DIRECTORY, "misc", "pointer.png")
    pointer_surface = pygame.image.load(pointer_surface_path)
    pointer_surface.set_colorkey(pointer_surface.get_at((0, 0)))

    # Animations
    pointer_animation = Animation([pointer_surface, constants.EMPTY_SURFACE], [30, 30])
