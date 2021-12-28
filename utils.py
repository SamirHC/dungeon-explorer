import constants
import pygame
import pygame.transform
import text

def scale(image: pygame.Surface, size: int) -> pygame.Surface:
    return pygame.transform.scale(image, (int(size), int(size)))

def cool_font(text_obj: text.Text, color: pygame.Color, position: tuple[int, int]):
    x, y = position
    text_surf = text.Text(text_obj, color).surface
    shadow_surf = text.Text(text_obj, constants.BLACK).surface
    constants.display.blit(shadow_surf, (x + 1, y))
    constants.display.blit(shadow_surf, (x, y + 1))
    constants.display.blit(text_surf, position)

def remove_duplicates(collection):
    return list(dict.fromkeys(collection))