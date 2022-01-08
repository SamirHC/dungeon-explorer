import constants
import keyboard
import pygame
import pygame.display
import pygame.draw
import pygame.event
import pygame.key
import pygame.time
import scene
import scenemanager

# Initialisation
pygame.init()
display = pygame.display.set_mode(constants.DISPLAY_SIZE)
pygame.display.set_caption(constants.CAPTION)

clock = pygame.time.Clock()
keyboard_input = keyboard.Keyboard()
scene_manager = scenemanager.SceneManager()
dungeon_id = "BeachCave"
user_id = "0025"
dungeon_scene = scene.DungeonScene(dungeon_id, user_id)
scene_manager.add(dungeon_scene)

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
            pygame.display.set_mode(constants.DISPLAY_SIZE)
        else:
            pygame.display.set_mode(constants.DISPLAY_SIZE,
                                    pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)

    scene_manager.process_input(keyboard_input)
    scene_manager.update()
    scene_manager.render(display)

    clock.tick(constants.FPS)

pygame.quit()
