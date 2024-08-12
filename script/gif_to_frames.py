from PIL import Image
import os


def extract_frames(gif_path, output_folder):
    # Open the GIF file
    with Image.open(gif_path) as img:
        # Ensure the output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        frame_count = 0
        # Loop through each frame of the GIF
        while True:
            frame = img.copy()
            frame.save(os.path.join(output_folder, f"frame_{frame_count}.png"))
            frame_count += 1
            try:
                img.seek(frame_count)
            except EOFError:
                break


gif_path = "C:\\Users\\Samir HC\\Documents\\GitHub\\dungeon-explorer\\assets\\images\\bg\\visual\\V00P01\\V00P01.gif"
output_folder = "out"
extract_frames(gif_path, output_folder)
