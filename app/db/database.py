import os
import sqlite3

import pygame

from app.common import constants
from app.db import (
    base_pokemon,
    bg_sprite,
    colormap,
    dungeon_data,
    font,
    frame,
    map_background,
    move,
    music,
    pokemonsprite,
    portrait,
    tileset,
    damage_chart,
    sfx,
    statanimation,
    item,
    trap,
    shadow,
    quiz_question,
)
from app.model.animation import Animation

# Databases
main_db = None

bg_sprite_db = None
music_db = None
colormap_db = None
dungeon_data_db = None
tileset_db = None
move_db = None
map_background_db = None
base_pokemon_db = None
pokemonsprite_db = None
portrait_db = None
frame_db = None
font_db = None
sfx_db = None
statanimation_db = None
item_db = None
trap_db = None
shadow_db = None
quiz_question_db = None

stat_stage_chart = None
type_chart = None

# Surfaces
pointer_surface = None
icon_surface = None

# Animations
pointer_animation = None


def init_database():
    global main_db

    global bg_sprite_db
    global music_db
    global colormap_db
    global dungeon_data_db
    global tileset_db
    global move_db
    global map_background_db
    global base_pokemon_db
    global pokemonsprite_db
    global portrait_db
    global frame_db
    global font_db
    global sfx_db
    global statanimation_db
    global item_db
    global trap_db
    global shadow_db
    global quiz_question_db

    global stat_stage_chart
    global type_chart

    # Surfaces
    global pointer_surface
    global icon_surface

    # Animations
    global pointer_animation

    # Databases
    main_db = sqlite3.connect(os.path.join(constants.GAMEDATA_DIRECTORY, "gamedata.db"))

    bg_sprite_db = bg_sprite.BgSpriteDatabase()
    music_db = music.MusicDatabase()
    colormap_db = colormap.ColorMapDatabase()
    dungeon_data_db = dungeon_data.DungeonDataDatabase()
    tileset_db = tileset.TilesetDatabase()
    move_db = move.MoveDatabase()
    map_background_db = map_background.MapBackgroundDatabase()
    base_pokemon_db = base_pokemon.BasePokemonDatabase()
    pokemonsprite_db = pokemonsprite.PokemonSpriteDatabase()
    portrait_db = portrait.PortraitDatabase()
    frame_db = frame.FrameDatabase()
    font_db = font.FontDatabase()
    sfx_db = sfx.SfxDatabase()
    statanimation_db = statanimation.StatAnimDatabase()
    item_db = item.ItemDatabase()
    trap_db = trap.TrapDatabase()
    shadow_db = shadow.ShadowDatabase()
    quiz_question_db = quiz_question.QuizQuestionDatabase()

    stat_stage_chart = damage_chart.StatStageChart()
    type_chart = damage_chart.TypeChart()

    # Surfaces
    pointer_surface_path = os.path.join(
        constants.IMAGES_DIRECTORY, "misc", "pointer.png"
    )
    pointer_surface = pygame.image.load(pointer_surface_path)
    pointer_surface.set_colorkey(pointer_surface.get_at((0, 0)))
    
    icon_path = os.path.join(constants.IMAGES_DIRECTORY, "icon", "icon.png")
    icon_surface = pygame.image.load(icon_path)

    # Animations
    pointer_animation = Animation([pointer_surface, constants.EMPTY_SURFACE], [30, 30])
