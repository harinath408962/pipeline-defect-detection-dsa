from PIL import Image

def load_image(path):
    img = Image.open(path).convert("RGB")
    pixels = img.load()
    width, height = img.size
    return pixels, width, height
