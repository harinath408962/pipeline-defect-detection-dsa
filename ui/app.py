import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from defect_detection import rgb_to_binary_map
from region_analysis import dfs
from classification import classify_local
from severity_priority import add_to_priority


def process_image_logic(pixels, width, height, pipe_id):
    binary_map = rgb_to_binary_map(pixels, width, height)

    visited = [[False] * width for _ in range(height)]

    global_min_i = global_min_j = float("inf")
    global_max_i = global_max_j = -1

    total_continuity = 0
    region_count = 0
    final_defect = "NORMAL"

    for i in range(height):
        for j in range(width):
            if binary_map[i][j] == 1 and not visited[i][j]:
                area, length, avg_color, mi, mj, Ma, Mb = dfs(
                    binary_map, pixels, visited, i, j, height, width
                )

                global_min_i = min(global_min_i, mi)
                global_min_j = min(global_min_j, mj)
                global_max_i = max(global_max_i, Ma)
                global_max_j = max(global_max_j, Mb)

                total_continuity += length
                region_count += 1

                local_defect = classify_local(avg_color)
                if final_defect == "NORMAL":
                    final_defect = local_defect

    global_length = max(
        global_max_i - global_min_i,
        global_max_j - global_min_j,
        0
    )

    avg_continuity = total_continuity / max(region_count, 1)

    if global_length > 100 and avg_continuity > 5:
        final_defect = "CRACK"

    add_to_priority(pipe_id, final_defect, int(global_length))

    return final_defect, binary_map
