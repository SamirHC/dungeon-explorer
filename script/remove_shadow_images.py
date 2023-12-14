import os
import glob

from app.common import constants


def main():
    for dex in range(896):
        try:
            dex_dir = os.path.join(constants.IMAGES_DIRECTORY, "sprites", str(dex))
            to_remove = os.path.join(dex_dir, "*Offsets.png")
            for path in glob.glob(to_remove):
                os.remove(path)
        except Exception:
            print(f"fail {dex}")


main()
