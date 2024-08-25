from app.common.constants import IMAGES_DIRECTORY


import os


def get_tile_mask_to_position() -> dict[int, tuple[int, int]]:
    pattern_dir = os.path.join(IMAGES_DIRECTORY, "tilesets", "patterns.txt")
    res = {}
    with open(pattern_dir) as f:
        masks = f.read().splitlines()

    for i, mask in enumerate(masks):
        ns = [0]
        for j in range(8):
            if mask[j] == "1":
                ns = [(n << 1) + 1 for n in ns]
            elif mask[j] == "0":
                ns = [n << 1 for n in ns]
            elif mask[j] == "X":
                ns = [n << 1 for n in ns]
                ns += [n + 1 for n in ns]
            else:
                ns = []
                break
        for n in ns:
            res[n] = (i % 6, i // 6)
    return res