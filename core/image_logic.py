from defect_detection import rgb_to_binary_map, detect_linear_crack
from region_analysis import dfs
from classification import classify_local
from severity_priority import add_to_priority


def process_image_logic(pixels, width, height, pipe_id):

    # ======================================================
    # 1️⃣ STRUCTURAL (LINEAR) CRACK DETECTION — FIRST
    # ======================================================
    if detect_linear_crack(pixels, width, height):
        final_defect = "CRACK"
        add_to_priority(pipe_id, final_defect, width)

        return {
            "final_defect": final_defect,
            "binary_sample": [[0]*20 for _ in range(10)],
            "total_pixels": width * height,
            "suspicious_pixels": 0,
            "affected_percentage": 0.0
        }

    # ======================================================
    # 2️⃣ COLOR-BASED BINARY MAP (CORROSION / RUST)
    # ======================================================
    binary_map = rgb_to_binary_map(pixels, width, height)
    visited = [[False]*width for _ in range(height)]

    total_length = 0
    regions = 0
    suspicious_pixels = 0
    final_defect = "NORMAL"

    for r in range(height):
        for c in range(width):
            if binary_map[r][c] == 1 and not visited[r][c]:
                area, length, avg_color, mi, mj, Ma, Mb = dfs(
                    binary_map, pixels, visited, r, c, height, width
                )

                suspicious_pixels += area
                regions += 1
                total_length += length

                local = classify_local(avg_color)
                if final_defect == "NORMAL" and local != "NORMAL":
                    final_defect = local

    total_pixels = width * height
    affected_percentage = round((suspicious_pixels / total_pixels) * 100, 2)

    add_to_priority(pipe_id, final_defect, int(affected_percentage))

    # ======================================================
    # 3️⃣ SAFE BINARY SAMPLE FOR UI
    # ======================================================
    center = height // 2
    binary_sample = [
        row[:20] for row in binary_map[max(0, center-5):center+5]
    ]

    return {
        "final_defect": final_defect,
        "binary_sample": binary_sample,
        "total_pixels": total_pixels,
        "suspicious_pixels": suspicious_pixels,
        "affected_percentage": affected_percentage
    }
