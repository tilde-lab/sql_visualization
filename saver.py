"""
Saving an image to a specific address.
"""
import shutil


class Saver():
    """
    That class saves images in a specific path, which given as an optional argument.
    """
    def __init__(self, output_path, img_name):
        self.output_path = output_path
        self.img_name = img_name

    def save(self):
        try:
            shutil.move(f'./diagram_folder/{self.img_name}', self.output_path)
        except:
            print(f'Incorrect path to output or "{self.img_name}" already exist.')