import os
import shutil

dirname = os.path.dirname(__file__)
path = os.path.join(dirname, "..", "assets", "images", "sprites")
    

def check_is_chunsoft(dir):
    credits_path = os.path.join(dir, "credits.txt")
    with open(credits_path, "r") as f:
        data = f.read()
    return "CHUNSOFT" in data

def move_custom_sprites():
    for d in os.walk(path):
        curr = d[0]
        if "credits.txt" in os.listdir(curr) and not check_is_chunsoft(curr):
            rel_dest = os.path.relpath(curr, path)
            dest = os.path.join(path, "..", "custom_sprites", rel_dest)
            shutil.move(curr, dest)

def flatten(directory):
    for dirpath, _, filenames in os.walk(directory, topdown=False):
        for filename in filenames:
            i = 0
            source = os.path.join(dirpath, filename)
            target = os.path.join(directory, filename)

            while os.path.exists(target):
                i += 1
                file_parts = os.path.splitext(os.path.basename(filename))

                target = os.path.join(
                    directory,
                    file_parts[0] + "_" + str(i) + file_parts[1],
                )

            shutil.move(source, target)

            print("Moved ", source, " to ", target)

        if dirpath != directory:
            os.rmdir(dirpath)

            print("Deleted ", dirpath)

walk = os.walk(path)
next(walk)
for d in walk:
    curr = d[0]
    print(curr)