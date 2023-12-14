import os

# from PIL import Image

base_dir = os.path.join("assets", "images", "portrait")

# Combine to sheet
"""
def paste_portrait(path: str, name: str, position: tuple[int, int], flipped=False):
    suffix = "^" if flipped else ""
    if flipped:
        x, y = position
        position = x, y + 160

    filename = f"{name}{suffix}.png"
    if filename not in os.listdir(path):
        return
    portrait = Image.open(os.path.join(path, filename))
    sheet.paste(portrait, position)

def paste_normal(path: str, flipped=False):
    paste_portrait(path, "Normal", (0, 0), flipped)

def paste_happy(path: str, flipped=False):
    paste_portrait(path, "Happy", (40, 0), flipped)

def paste_pain(path: str, flipped=False):
    paste_portrait(path, "Pain", (80, 0), flipped)

def paste_angry(path: str, flipped=False):
    paste_portrait(path, "Angry", (120, 0), flipped)

def paste_worried(path: str, flipped=False):
    paste_portrait(path, "Worried", (160, 0), flipped)

def paste_sad(path: str, flipped=False):
    paste_portrait(path, "Sad", (0, 40), flipped)

def paste_crying(path: str, flipped=False):
    paste_portrait(path, "Crying", (40, 40), flipped)

def paste_shouting(path: str, flipped=False):
    paste_portrait(path, "Shouting", (80, 40), flipped)

def paste_teary(path: str, flipped=False):
    paste_portrait(path, "Teary-Eyed", (120, 40), flipped)

def paste_determined(path: str, flipped=False):
    paste_portrait(path, "Determined", (160, 40), flipped)

def paste_joyous(path: str, flipped=False):
    paste_portrait(path, "Joyous", (0, 80), flipped)

def paste_inspired(path: str, flipped=False):
    paste_portrait(path, "Inspired", (40, 80), flipped)

def paste_surprised(path: str, flipped=False):
    paste_portrait(path, "Surprised", (80, 80), flipped)

def paste_dizzy(path: str, flipped=False):
    paste_portrait(path, "Dizzy", (120, 80), flipped)

def paste_special0(path: str, flipped=False):
    paste_portrait(path, "Special0", (160, 80), flipped)

def paste_special1(path: str, flipped=False):
    paste_portrait(path, "Special1", (0, 120), flipped)

def paste_sigh(path: str, flipped=False):
    paste_portrait(path, "Sigh", (40, 120), flipped)

def paste_stunned(path: str, flipped=False):
    paste_portrait(path, "Stunned", (80, 120), flipped)

def paste_special2(path: str, flipped=False):
    paste_portrait(path, "Special2", (120, 120), flipped)

def paste_special3(path: str, flipped=False):
    paste_portrait(path, "Special3", (160, 120), flipped)

for folder in os.listdir(base_dir):
    if folder == "to_sheet.py":
        continue
    folder_path = os.path.join(base_dir, folder)
    sheet = Image.new("RGBA", (200, 320))
    paste_normal(folder_path)
    paste_happy(folder_path)
    paste_pain(folder_path)
    paste_angry(folder_path)
    paste_worried(folder_path)
    paste_sad(folder_path)
    paste_crying(folder_path)
    paste_shouting(folder_path)
    paste_teary(folder_path)
    paste_determined(folder_path)
    paste_joyous(folder_path)
    paste_inspired(folder_path)
    paste_surprised(folder_path)
    paste_dizzy(folder_path)
    paste_special0(folder_path)
    paste_special1(folder_path)
    paste_sigh(folder_path)
    paste_stunned(folder_path)
    paste_special2(folder_path)
    paste_special3(folder_path)

    paste_normal(folder_path, True)
    paste_happy(folder_path, True)
    paste_pain(folder_path, True)
    paste_angry(folder_path, True)
    paste_worried(folder_path, True)
    paste_sad(folder_path, True)
    paste_crying(folder_path, True)
    paste_shouting(folder_path, True)
    paste_teary(folder_path, True)
    paste_determined(folder_path, True)
    paste_joyous(folder_path, True)
    paste_inspired(folder_path, True)
    paste_surprised(folder_path, True)
    paste_dizzy(folder_path, True)
    paste_special0(folder_path, True)
    paste_special1(folder_path, True)
    paste_sigh(folder_path, True)
    paste_stunned(folder_path, True)
    paste_special2(folder_path, True)
    paste_special3(folder_path, True)

    sheet.save(os.path.join(folder_path, f"portrait_sheet{int(folder)}.png"))
"""

"""
for folder in os.listdir(base_dir):
    if folder == "to_sheet.py":
        continue
    folder_path = os.path.join(base_dir, folder)
    for image in os.listdir(folder_path):
        if not image.endswith(".png"):
            continue
        if image == f"portrait_sheet{int(folder)}.png":
            continue
        os.remove(os.path.join(folder_path, image))
"""

# Rename
for folder in os.listdir(base_dir):
    if folder == "to_sheet.py":
        continue
    folder_path = os.path.join(base_dir, folder)
    new_folder_path = os.path.join(base_dir, str(int(folder)))
    os.rename(folder_path, new_folder_path)
