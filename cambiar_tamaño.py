import sys

from PIL import Image
import os

def batch_resize(folder_in,folder_out, width, height):
    for filename in os.listdir(folder_in):
        if filename.endswith(('.jpeg', '.jpg', '.png')):
            img = Image.open(os.path.join(folder_in, filename))
            img = img.resize((width, height))
            img.save(os.path.join(folder_out, f"resized_{filename}"))
            print(f'{filename} Redimensionado')


if __name__ == '__main__':
    batch_resize('images','images_resized', 800, 600)