import os
import shutil

dirname = os.path.dirname(__file__)
path = os.path.join(dirname, "..", "assets", "images", "sprites")
    

def check_is_chunsoft(dir):
    credits_path = os.path.join(dir, "credits.txt")
    with open(credits_path, "r") as f:
        data = f.read()
    return "CHUNSOFT" in data


for d in os.walk(path):
    curr = d[0]
    if "credits.txt" in os.listdir(curr) and not check_is_chunsoft(curr):
       rel_dest = os.path.relpath(curr, path)
       dest = os.path.join(path, "..", "custom_sprites", rel_dest)
       shutil.move(curr, dest)
    
for d in os.walk(path):
    if not os.listdir(curr):
        os.rmdir(curr)