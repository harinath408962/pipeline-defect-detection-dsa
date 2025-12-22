from config import DAMP_DARK_THRESHOLD

def is_defective_pixel(r, g, b):
    # Dark pixels OR rust-like pixels
    rust = (r > g and r > b and r > 90)
    dark = (r < DAMP_DARK_THRESHOLD and g < DAMP_DARK_THRESHOLD and b < DAMP_DARK_THRESHOLD)
    return rust or dark
