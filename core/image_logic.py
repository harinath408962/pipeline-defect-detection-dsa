from defect_detection import rgb_to_binary_map
from region_analysis import dfs, binary_map_summary
from classification import classify_local
from severity_priority import add_to_priority


def process_image_logic(pixels, width, height, pipe_id):
    binary_map = rgb_to_binary_map(pixels, width, height)
    visited = [[False]*width for _ in range(height)]

    gmin_r = gmin_c = 10**9
    gmax_r = gmax_c = -1
    total_length = 0
    regions = 0
    final_defect = "NORMAL"

    for r in range(height):
        for c in range(width):
            if binary_map[r][c] == 1 and not visited[r][c]:
                area, length, avg_color, mi, mj, Ma, Mb = dfs(
                    binary_map, pixels, visited, r, c, height, width
                )

                gmin_r = min(gmin_r, mi)
                gmin_c = min(gmin_c, mj)
                gmax_r = max(gmax_r, Ma)
                gmax_c = max(gmax_c, Mb)

                total_length += length
                regions += 1

                local = classify_local(avg_color)
                if final_defect == "NORMAL":
                    final_defect = local

    global_span = max(gmax_r - gmin_r, gmax_c - gmin_c)
    avg_continuity = total_length / max(regions, 1)

    if global_span > 120 and avg_continuity > 6:
        final_defect = "CRACK"

    add_to_priority(pipe_id, final_defect, int(global_span))

    total, suspicious, percent = binary_map_summary(binary_map)

    return {
        "final_defect": final_defect,
        "binary_sample": binary_map,
        "total_pixels": total,
        "suspicious_pixels": suspicious,
        "affected_percentage": percent
    }
