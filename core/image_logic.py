from defect_detection import rgb_to_binary_map
from region_analysis import dfs
from classification import classify_local
from severity_priority import add_to_priority

def process_image_logic(pixels, width, height, pipe_id):
    binary_map = rgb_to_binary_map(pixels, width, height)
    visited = [[False]*width for _ in range(height)]

    global_min_r = global_min_c = 10**9
    global_max_r = global_max_c = -1
    total_length = 0
    regions = 0
    final_defect = "NORMAL"

    for r in range(height):
        for c in range(width):
            if binary_map[r][c] == 1 and not visited[r][c]:
                area, length, avg_color, mi, mj, Ma, Mb = dfs(
                    binary_map, pixels, visited, r, c, height, width
                )

                global_min_r = min(global_min_r, mi)
                global_min_c = min(global_min_c, mj)
                global_max_r = max(global_max_r, Ma)
                global_max_c = max(global_max_c, Mb)

                total_length += length
                regions += 1

                local = classify_local(avg_color)
                if final_defect == "NORMAL":
                    final_defect = local

    global_span = max(
        global_max_r - global_min_r,
        global_max_c - global_min_c
    )

    avg_continuity = total_length / max(regions, 1)

    # ✅ CRACK RULE (STRICT)
    if global_span > 120 and avg_continuity > 6:
        final_defect = "CRACK"

    add_to_priority(pipe_id, final_defect, int(global_span))
    return final_defect, binary_map
