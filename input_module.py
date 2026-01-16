from PIL import Image

def load_image(uploaded_file):
    img = Image.open(uploaded_file).convert("RGB")
    width, height = img.size
    pixels = img.load()
    return pixels, width, height
