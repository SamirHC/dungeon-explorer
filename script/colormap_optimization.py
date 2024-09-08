import numpy as np
import os
import pygame

dirname = os.path.dirname(__file__)
colormap_dir = os.path.join(dirname, "..", "assets", "images", "colormap")


def extract_colors(surface: pygame.Surface) -> list[pygame.Color]:
    return [surface.get_at((i % 16, i // 16)) for i in range(256)]

def C_r(x: int, colors: list[pygame.Color]) -> int:
    return colors[x].r

def C_g(x: int, colors: list[pygame.Color]) -> int:
    return colors[x].g

def C_b(x: int, colors: list[pygame.Color]) -> int:
    return colors[x].b

xpoints = np.arange(256)

def get_points(colors: list[pygame.Color]):
    # Alpha -> ColorMap
    points = [None] * 256
    for a in range(0,256):
        def f(theta):
            return (
                np.linalg.norm(
                    np.array(
                        [r*(1 - a/255) + (a/255)*theta - C_r(r, colors)
                        for r in range(256)
                        ])),
                np.linalg.norm(
                    np.array(
                        [g*(1 - a/255) + (a/255)*theta - C_g(g, colors)
                        for g in range(256)
                        ])),
                np.linalg.norm(
                    np.array(
                        [b*(1 - a/255) + (a/255)*theta - C_b(b, colors)
                        for b in range(256)
                        ]))
            )
        vf = np.vectorize(f)

        points[a] = vf(xpoints)
    return points

def get_optimized_filter(colormap_surface: pygame.Surface):
    clear_colors = extract_colors(colormap_surface)
    points = get_points(clear_colors)
    optimal_colors_for_each_alpha = [
        tuple(map(int, (np.argmin(points[alpha][0]), np.argmin(points[alpha][1]), np.argmin(points[alpha][2]))))
        for alpha in range(256)
    ]

    deltas_for_each_alpha = [
        np.linalg.norm(np.array([
            points[alpha][0][optimal_colors_for_each_alpha[alpha][0]],
            points[alpha][1][optimal_colors_for_each_alpha[alpha][1]],
            points[alpha][2][optimal_colors_for_each_alpha[alpha][2]],
            ])
        )
        for alpha in range(256)
    ]

    i = np.argmin(np.array(deltas_for_each_alpha))
    print(f"Alpha: {i}, Delta: {deltas_for_each_alpha[i]}, RGB: {optimal_colors_for_each_alpha[i]}")


for file in os.listdir(colormap_dir):
    colormap_path = os.path.join(colormap_dir, file)
    colormap_surface = pygame.image.load(colormap_path)
    print(file)
    get_optimized_filter(colormap_surface)
    
"""
Output:

CLEAR.png
Alpha: 5, Delta: 79.48227080644486, RGB: (255, 255, 255)
CLOUDY.png
Alpha: 63, Delta: 158.56206451890776, RGB: (151, 151, 255)
FOG.png
Alpha: 102, Delta: 73.32121111929345, RGB: (220, 220, 220)
HAIL.png
Alpha: 53, Delta: 92.25661184887878, RGB: (0, 101, 178)
RAINY.png
Alpha: 33, Delta: 313.41421545588355, RGB: (0, 0, 233)
SANDSTORM.png
Alpha: 80, Delta: 306.6347408285109, RGB: (255, 255, 83)
SNOW.png
Alpha: 34, Delta: 209.65071481447947, RGB: (41, 148, 255)
SUNNY.png
Alpha: 29, Delta: 251.12740302288734, RGB: (255, 255, 255)
"""