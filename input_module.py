from PIL import Image

def load_image(image_path):
    img = Image.open(image_path).convert("RGB")
    pixels = img.load()
    width, height = img.size
    return pixels, width, height
