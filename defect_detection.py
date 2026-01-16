def is_defective_pixel(r, g, b):
    # Rust / corrosion tends to be reddish-brown
    return r > 120 and g < 100 and b < 100


def rgb_to_binary_map(pixels, width, height):
    binary_map = []

    for y in range(height):
        row = []
        for x in range(width):
            r, g, b = pixels[x, y]   # ✅ CORRECT ACCESS
            row.append(1 if is_defective_pixel(r, g, b) else 0)
        binary_map.append(row)

    return binary_map


def center_binary_sample(binary_map, size=10):
    h = len(binary_map)
    w = len(binary_map[0])

    cy = h // 2
    cx = w // 2
    half = size // 2

    sample = []
    for i in range(cy - half, cy + half):
        row = ""
        for j in range(cx - half, cx + half):
            row += "#" if binary_map[i][j] else "."
        sample.append(row)

    return sample
