import pygame
import os


def load_frames(folder) -> list[pygame.Surface]:
    frames = []
    for filename in sorted(os.listdir(folder)):
        frame = pygame.image.load(os.path.join(folder, filename))
        frames.append(frame)
    return frames


def frames_to_sheet(frames: list[pygame.Surface], rect: pygame.Rect) -> pygame.Surface:
    """Outputs concatenated frames surface."""
    result = pygame.Surface((rect.w * len(frames), rect.h))
    frames = [frame.subsurface(rect) for frame in frames]
    for i, frame in enumerate(frames):
        result.blit(frame, (i * rect.w, 0))
    return result


frames = load_frames("out")
sheet = frames_to_sheet(frames, pygame.Rect(0, 159, 192, 81))
pygame.image.save(
    sheet,
    "C:\\Users\\Samir HC\\Documents\\GitHub\\dungeon-explorer\\"
    "assets\\images\\bg\\visual\\V00P01\\V00P01.png",
)
