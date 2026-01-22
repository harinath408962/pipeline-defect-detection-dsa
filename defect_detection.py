# =========================================================
# DEFECT DETECTION MODULE (COLOR + STRUCTURAL)
# =========================================================

def rgb_to_binary_map(pixels, width, height):
    binary_map = [[0]*width for _ in range(height)]

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[y, x]   # ✅ FIXED ORDER

            # Rust / corrosion color rule
            if (r > 120 and r > g and r > b):
                binary_map[y][x] = 1

    return binary_map



def detect_linear_crack(pixels, width, height):
    dark_count = 0
    rust_like = 0

    for y in range(height):
        for x in range(width - 1):   # ✅ SAFE LIMIT
            r, g, b = pixels[y, x]
            r2, g2, b2 = pixels[y, x + 1]

            if r < 80 and g < 80 and b < 80:
                dark_count += 1

            if r > g and r > b and r > 100:
                rust_like += 1

    if dark_count > 300 and rust_like < dark_count * 0.3:
        return True

    return False



