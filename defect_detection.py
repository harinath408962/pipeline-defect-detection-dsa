# =========================================================
# DEFECT DETECTION MODULE (COLOR + STRUCTURAL)
# =========================================================

def rgb_to_binary_map(pixels, width, height):
    binary_map = [[0]*width for _ in range(height)]
    
    # calculate global average brightness for baseline
    total_brightness = 0
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[y, x]
            total_brightness += (int(r) + int(g) + int(b))
    
    if width * height > 0:
        global_avg_brightness = total_brightness / (3 * width * height)
    else:
        global_avg_brightness = 128  # Fallback

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[y, x]
            brightness = (int(r) + int(g) + int(b)) / 3

            # 1. Dark Anomaly (Crack/Damp) - darker than global avg
            # Relaxed to 0.75 to detect lighter damp patches
            if brightness < global_avg_brightness * 0.75:
                binary_map[y][x] = 1
                
            # 2. Rust / Corrosion - Specific Color Rules
            # Red dominance + Deviation from gray
            elif (int(r) > 100 and int(r) > int(g) + 20 and int(r) > int(b) + 20):
                binary_map[y][x] = 1
                
            # 3. High Contrast Anomaly (General)
            # If a pixel is very different from its neighbors (Laplacian-like check could be here, 
            # but per instructions, keeping it simple pixel-level first, relying on global contrast)
            
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



