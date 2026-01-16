def is_defective_pixel(r, g, b):
    return (r > 120 and g < 120 and b < 120)


def rgb_to_binary_map(pixels, width, height):
    binary_map = [[0]*width for _ in range(height)]

    for i in range(height):
        for j in range(width):
            r, g, b = pixels[j, i]
            if is_defective_pixel(r, g, b):
                binary_map[i][j] = 1

    return binary_map