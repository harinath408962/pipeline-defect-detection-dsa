def dfs(binary_map, pixels, visited, row, col, height, width):
    stack = [(row, col)]
    visited[row][col] = True

    area = 0
    min_r = min_c = 10**9
    max_r = max_c = -1
    total_r = total_g = total_b = 0

    while stack:
        r, c = stack.pop()
        area += 1

        min_r = min(min_r, r)
        min_c = min(min_c, c)
        max_r = max(max_r, r)
        max_c = max(max_c, c)

        # ✅ correct pixel access
        pr, pg, pb = pixels[c, r]
        total_r += pr
        total_g += pg
        total_b += pb

        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r + dr, c + dc
            if (
                0 <= nr < height and
                0 <= nc < width and
                not visited[nr][nc] and
                binary_map[nr][nc] == 1
            ):
                visited[nr][nc] = True
                stack.append((nr, nc))

    avg_color = (
        total_r // area,
        total_g // area,
        total_b // area
    )

    length = max(max_r - min_r, max_c - min_c)
    return area, length, avg_color, min_r, min_c, max_r, max_c


# ✅ THIS FUNCTION WAS MISSING (YOUR ERROR)
def binary_map_summary(binary_map):
    total = 0
    suspicious = 0

    for row in binary_map:
        for cell in row:
            total += 1
            if cell == 1:
                suspicious += 1

    percent = round((suspicious / total) * 100, 2)
    return total, suspicious, percent
