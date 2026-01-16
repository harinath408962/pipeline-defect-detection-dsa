from input_module import load_image
from defect_detection import is_defective_pixel
from region_analysis import dfs
from classification import classify_local
from severity_priority import add_to_priority, priority_queue

def process_image(image_path, pipe_id):
    pixels, width, height = load_image(image_path)

    # Step 1: Build defect map
    defect_map = [
        [1 if is_defective_pixel(*pixels[j, i]) else 0 for j in range(width)]
        for i in range(height)
    ]

    visited = [[False] * width for _ in range(height)]

    # GLOBAL TRACKING (IMPORTANT)
    global_min_i = global_min_j = float("inf")
    global_max_i = global_max_j = -1

    total_continuity = 0
    region_count = 0
    final_defect = "NORMAL"

    # Step 2: Region analysis
    for i in range(height):
        for j in range(width):
            if defect_map[i][j] and not visited[i][j]:
                area, length, avg_color, mi, mj, Ma, Mb = dfs(
                    defect_map, pixels, visited, i, j, height, width
                )

                # Track global bounding box
                global_min_i = min(global_min_i, mi)
                global_min_j = min(global_min_j, mj)
                global_max_i = max(global_max_i, Ma)
                global_max_j = max(global_max_j, Mb)

                total_continuity += length
                region_count += 1

                local_defect = classify_local(avg_color)
                if final_defect == "NORMAL":
                    final_defect = local_defect

    # Step 3: GLOBAL CRACK DECISION (FINAL FIX)
    global_length = max(
        global_max_i - global_min_i,
        global_max_j - global_min_j
    )

    avg_continuity = total_continuity / max(region_count, 1)

    # ✅ FINAL CRACK RULE (THIN + LONG + CONTINUOUS)
    if global_length > 100 and avg_continuity > 5:
        final_defect = "CRACK"

    add_to_priority(pipe_id, final_defect, int(global_length))

    return final_defect


# ================= RUN SYSTEM =================

images = [
    ("images/pipe1.jpg", "PIPE_001"),
    ("images/pipe2.jpg", "PIPE_002"),
    ("images/pipe3.jpg", "PIPE_003"),
]

print("\n===== PIPELINE DEFECT DETECTION SYSTEM =====\n")

for img, pid in images:
    result = process_image(img, pid)
    print(f"Image: {img}")
    print(f"Pipe ID: {pid}")
    print(f"Final Defect: {result}")
    print("-" * 40)

print("\n===== PRIORITY ORDER =====\n")
while priority_queue:
    _, pid, defect, score = priority_queue.pop(0)
    print(pid, defect, score)
