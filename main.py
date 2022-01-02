import battlesystem
import constants
import keyboard
import pygame
import pygame.display
import pygame.draw
import pygame.event
import pygame.key
import pygame.time
import scene

# Initialisation
pygame.init()
display = pygame.display.set_mode((constants.DISPLAY_WIDTH, constants.DISPLAY_HEIGHT))
pygame.display.set_caption(constants.CAPTION)

clock = pygame.time.Clock()
keyboard_input = keyboard.Keyboard()
battle_system = battlesystem.BattleSystem()

dungeon_id = "BeachCave"
user_id = "0025"
dungeon_scene = scene.DungeonScene(dungeon_id, user_id)

# Game loop
running = True
while running:
    # Gets the keyboard state
    keyboard_input.update()

    # Checks if user quits
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # Toggle Fullscreen
    if keyboard_input.is_pressed(pygame.K_F11):
        if display.get_flags() & pygame.FULLSCREEN:
            pygame.display.set_mode((constants.DISPLAY_WIDTH, constants.DISPLAY_HEIGHT))
        else:
            pygame.display.set_mode((constants.DISPLAY_WIDTH, constants.DISPLAY_HEIGHT), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
    
    dungeon_scene.processInput(keyboard_input)
    dungeon_scene.update()
    dungeon_scene.render()
    display.blit(dungeon_scene.display, (0, 0))

    pygame.display.update()
    clock.tick(constants.FPS)

pygame.quit()